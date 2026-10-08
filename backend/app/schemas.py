from pydantic import BaseModel


class StartInterviewRequest(BaseModel):
    candidate_name: str


class StartInterviewResponse(BaseModel):
    session_id: int
    bot_message: str


class MessageRequest(BaseModel):
    message: str


class MessageResponse(BaseModel):
    bot_message: str
    detected_topic: str | None = None
    score: float | None = None
    is_finished: bool


class ResultResponse(BaseModel):
    session_id: int
    candidate_name: str
    total_score: float
    is_finished: bool



class CandidateRankResponse(BaseModel):
    session_id: int
    candidate_name: str
    total_score: float
    is_finished: bool
    recommendation: str


class ShortlistResponse(BaseModel):
    count: int
    candidates: list[CandidateRankResponse]


class AnswerReportItem(BaseModel):
    question: str | None = None
    answer: str
    topic: str | None = None
    score: float | None = None


class CandidateReportResponse(BaseModel):
    session_id: int
    candidate_name: str
    total_score: float
    is_finished: bool
    recommendation: str
    strengths: list[str]
    weak_areas: list[str]
    answers: list[AnswerReportItem]
    red_flags: list[str]