import json

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.interview_engine import (
    build_question_order,
    detect_topic,
    get_question_by_order,
)
from app.models import InterviewMessage, InterviewSession
from app.schemas import (
    AnswerReportItem,
    CandidateRankResponse,
    CandidateReportResponse,
    MessageRequest,
    MessageResponse,
    ResultResponse,
    ShortlistResponse,
    StartInterviewRequest,
    StartInterviewResponse,
)
from app.scoring import calculate_score


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Interview Bot",
    description="ChatGPT-style AI interview chatbot MVP",
    version="1.0.0",
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_recommendation(total_score: float):
    if total_score >= 80:
        return "Strong Shortlist"

    if total_score >= 60:
        return "Shortlist"

    if total_score >= 40:
        return "Hold"

    return "Reject"

def analyze_strengths_and_weaknesses(
    answers: list,
):
    strengths = []
    weak_areas = []

    for answer in answers:
        label = answer.question or answer.topic or "Unknown area"

        if answer.score is None:
            continue

        if answer.score >= 7:
            strengths.append(label)

        elif answer.score < 5:
            weak_areas.append(label)

    return strengths, weak_areas


def detect_red_flags(
    answers: list,
):
    red_flags = []

    seen_answers = {}

    for answer in answers:
        answer_text = answer.answer.strip().lower()
        word_count = len(answer_text.split())

        if word_count <= 2:
            red_flags.append(
                "Very short answer detected"
            )

        if answer.score is not None and answer.score < 2:
            red_flags.append(
                "Very low score answer detected"
            )

        if answer_text:
            seen_answers[answer_text] = (
                seen_answers.get(answer_text, 0) + 1
            )

    for answer_text, count in seen_answers.items():
        if count >= 2:
            red_flags.append(
                "Repeated same answer detected"
            )

    return list(set(red_flags))

@app.post(
    "/interview/start",
    response_model=StartInterviewResponse,
)
def start_interview(
    payload: StartInterviewRequest,
    db: Session = Depends(get_db),
):
    session = InterviewSession(
        candidate_name=payload.candidate_name,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    bot_message = (
        f"Hi {payload.candidate_name}, welcome to the interview. "
        "Tell me about yourself."
    )

    message = InterviewMessage(
        session_id=session.id,
        sender="bot",
        message=bot_message,
    )

    db.add(message)
    db.commit()

    return StartInterviewResponse(
        session_id=session.id,
        bot_message=bot_message,
    )


@app.post(
    "/interview/{session_id}/message",
    response_model=MessageResponse,
)
def send_message(
    session_id: int,
    payload: MessageRequest,
    db: Session = Depends(get_db),
):
    session = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id)
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found",
        )

    if session.is_finished:
        return MessageResponse(
            bot_message="This interview is already finished.",
            detected_topic=session.current_topic,
            score=None,
            is_finished=True,
        )

    user_message = InterviewMessage(
        session_id=session.id,
        sender="user",
        message=payload.message,
    )

    db.add(user_message)

    score = None
    detected_topic = session.current_topic

    if session.current_topic is None:
        detected_topic = detect_topic(payload.message)

        if detected_topic is None:
            bot_message = (
                "I could not detect your topic clearly. "
                "Please mention your main skill, like Django, Python, or REST API."
            )
        else:
            session.current_topic = detected_topic
            session.current_question_index = 0

            question_order = build_question_order(
                detected_topic,
                max_questions=session.max_questions,
            )

            session.question_order = json.dumps(question_order)

            question_data = get_question_by_order(
                detected_topic,
                question_order,
                session.current_question_index,
            )

            if question_data is None:
                bot_message = (
                    "I detected your topic, but no question is available for it."
                )
                session.is_finished = True
            else:
                bot_message = question_data["question"]

    else:
        question_order = json.loads(session.question_order or "[]")

        question_data = get_question_by_order(
            session.current_topic,
            question_order,
            session.current_question_index,
        )

        if question_data is None:
            bot_message = "No active question found. Interview finished."
            session.is_finished = True
        else:
            score = calculate_score(
                candidate_answer=payload.message,
                expected_answer=question_data["expected_answer"],
                marks=question_data["marks"],
                key_points=question_data.get("key_points", []),
                wrong_concepts=question_data.get("wrong_concepts", []),
                follow_up_keywords=question_data.get("follow_up_keywords", []),
            )

            session.total_score = (session.total_score or 0) + score

            user_message.topic = session.current_topic
            user_message.score = score

            session.current_question_index += 1

            next_question = get_question_by_order(
                session.current_topic,
                question_order,
                session.current_question_index,
            )

            if next_question is None:
                session.is_finished = True
                bot_message = (
                    f"Thank you. Your interview is finished. "
                    f"Your total score is {session.total_score}."
                )
            else:
                bot_message = next_question["question"]

    bot_db_message = InterviewMessage(
        session_id=session.id,
        sender="bot",
        message=bot_message,
        topic=detected_topic,
    )

    db.add(bot_db_message)
    db.commit()

    return MessageResponse(
        bot_message=bot_message,
        detected_topic=detected_topic,
        score=score,
        is_finished=session.is_finished,
    )


@app.get(
    "/interview/{session_id}/result",
    response_model=ResultResponse,
)
def get_result(
    session_id: int,
    db: Session = Depends(get_db),
):
    session = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id)
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found",
        )

    return ResultResponse(
        session_id=session.id,
        candidate_name=session.candidate_name,
        total_score=session.total_score,
        is_finished=session.is_finished,
    )

@app.get(
    "/screening/candidates/rank",
    response_model=list[CandidateRankResponse],
)
def rank_candidates(
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.is_finished == True)
        .order_by(InterviewSession.total_score.desc())
        .all()
    )

    return [
        CandidateRankResponse(
            session_id=session.id,
            candidate_name=session.candidate_name,
            total_score=session.total_score or 0,
            is_finished=session.is_finished,
            recommendation=get_recommendation(
                session.total_score or 0,
            ),
        )
        for session in sessions
    ]

@app.get(
    "/screening/candidates/shortlist",
    response_model=ShortlistResponse,
)
def shortlist_candidates(
    limit: int = 5,
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.is_finished == True)
        .order_by(InterviewSession.total_score.desc())
        .limit(limit)
        .all()
    )

    candidates = [
        CandidateRankResponse(
            session_id=session.id,
            candidate_name=session.candidate_name,
            total_score=session.total_score or 0,
            is_finished=session.is_finished,
            recommendation=get_recommendation(
                session.total_score or 0,
            ),
        )
        for session in sessions
    ]

    return ShortlistResponse(
        count=len(candidates),
        candidates=candidates,
    )

@app.get(
    "/screening/candidates/{session_id}/report",
    response_model=CandidateReportResponse,
)
def get_candidate_report(
    session_id: int,
    db: Session = Depends(get_db),
):
    session = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id)
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found",
        )

    messages = (
        db.query(InterviewMessage)
        .filter(InterviewMessage.session_id == session_id)
        .order_by(InterviewMessage.id.asc())
        .all()
    )
    

    answers = []

    last_bot_question = None

    for message in messages:
        if message.sender == "bot":
            last_bot_question = message.message

        if message.sender == "user":
            answers.append(
                AnswerReportItem(
                    question=last_bot_question,
                    answer=message.message,
                    topic=message.topic,
                    score=message.score,
                )
            )
    strengths, weak_areas = analyze_strengths_and_weaknesses(
        answers,
    )
    red_flags = detect_red_flags(answers)
    return CandidateReportResponse(
        session_id=session.id,
        candidate_name=session.candidate_name,
        total_score=session.total_score or 0,
        is_finished=session.is_finished,
        recommendation=get_recommendation(
            session.total_score or 0,
        ),
        answers=answers,
        strengths=strengths,
        weak_areas=weak_areas,
        red_flags=red_flags
    )


