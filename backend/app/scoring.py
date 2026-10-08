from sentence_transformers import SentenceTransformer, util


model = SentenceTransformer("all-MiniLM-L6-v2")


def normalize_text(text: str):
    return (text or "").lower().strip()


def calculate_semantic_similarity(
    candidate_answer: str,
    expected_answer: str,
):
    expected_embedding = model.encode(
        expected_answer,
        convert_to_tensor=True,
    )

    candidate_embedding = model.encode(
        candidate_answer,
        convert_to_tensor=True,
    )

    similarity = util.cos_sim(
        expected_embedding,
        candidate_embedding,
    ).item()

    return max(similarity, 0)


def find_matched_points(
    candidate_answer: str,
    key_points: list[str],
):
    answer = normalize_text(candidate_answer)

    matched = []
    missing = []

    for point in key_points:
        point_lower = normalize_text(point)

        if point_lower in answer:
            matched.append(point)
        else:
            missing.append(point)

    return matched, missing


def find_wrong_points(
    candidate_answer: str,
    wrong_concepts: list[str],
):
    answer = normalize_text(candidate_answer)

    wrong_points = []

    for concept in wrong_concepts:
        concept_lower = normalize_text(concept)

        if concept_lower in answer:
            wrong_points.append(concept)

    return wrong_points


def detect_follow_up_keywords(
    candidate_answer: str,
    follow_up_keywords: list[str],
):
    answer = normalize_text(candidate_answer)

    detected = []

    for keyword in follow_up_keywords:
        keyword_lower = normalize_text(keyword)

        if keyword_lower in answer:
            detected.append(keyword)

    return detected


def calculate_completeness_score(candidate_answer: str):
    word_count = len(candidate_answer.split())

    if word_count <= 2:
        return 0.1

    if word_count <= 5:
        return 0.35

    if word_count <= 10:
        return 0.65

    return 1.0


def evaluate_answer(
    candidate_answer: str,
    expected_answer: str,
    marks: int,
    key_points: list[str] | None = None,
    wrong_concepts: list[str] | None = None,
    follow_up_keywords: list[str] | None = None,
):
    key_points = key_points or []
    wrong_concepts = wrong_concepts or []
    follow_up_keywords = follow_up_keywords or []

    semantic_score = calculate_semantic_similarity(
        candidate_answer,
        expected_answer,
    )

    matched_points, missing_points = find_matched_points(
        candidate_answer,
        key_points,
    )

    wrong_points = find_wrong_points(
        candidate_answer,
        wrong_concepts,
    )

    detected_follow_ups = detect_follow_up_keywords(
        candidate_answer,
        follow_up_keywords,
    )

    if key_points:
        key_point_score = len(matched_points) / len(key_points)
    else:
        key_point_score = 0

    completeness_score = calculate_completeness_score(
        candidate_answer,
    )

    final_ratio = (
        semantic_score * 0.55
        + key_point_score * 0.30
        + completeness_score * 0.15
    )

    score = final_ratio * marks

    if wrong_points:
        score = min(score, marks * 0.2)

    if len(candidate_answer.split()) <= 2:
        score = min(score, marks * 0.2)

    score = round(score, 2)

    return {
        "score": score,
        "semantic_score": round(semantic_score, 3),
        "matched_points": matched_points,
        "missing_points": missing_points,
        "wrong_points": wrong_points,
        "detected_follow_ups": detected_follow_ups,
        "is_relevant": semantic_score >= 0.35 or bool(matched_points),
    }


def calculate_score(
    candidate_answer: str,
    expected_answer: str,
    marks: int,
    key_points: list[str] | None = None,
    wrong_concepts: list[str] | None = None,
    follow_up_keywords: list[str] | None = None,
):
    result = evaluate_answer(
        candidate_answer=candidate_answer,
        expected_answer=expected_answer,
        marks=marks,
        key_points=key_points,
        wrong_concepts=wrong_concepts,
        follow_up_keywords=follow_up_keywords,
    )

    return result["score"]