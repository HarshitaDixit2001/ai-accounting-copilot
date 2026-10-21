from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_submit_positive_feedback():
    response = client.post(
        "/feedback",
        json={
            "request_id": "test-feedback-positive",
            "rating": 1,
            "feedback": "The answer was correct.",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "recorded"
    assert body["request_id"] == "test-feedback-positive"
    assert isinstance(body["feedback_id"], int)


def test_submit_negative_feedback():
    response = client.post(
        "/feedback",
        json={
            "request_id": "test-feedback-negative",
            "rating": 0,
            "feedback": "The answer was not useful.",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "recorded"
    assert body["request_id"] == "test-feedback-negative"
    assert isinstance(body["feedback_id"], int)


def test_feedback_requires_request_id():
    response = client.post(
        "/feedback",
        json={
            "rating": 1,
            "feedback": "Missing request ID.",
        },
    )

    assert response.status_code == 422


def test_feedback_rejects_invalid_rating():
    response = client.post(
        "/feedback",
        json={
            "request_id": "test-invalid-rating",
            "rating": 2,
            "feedback": "Invalid rating.",
        },
    )

    assert response.status_code == 422


def test_feedback_metrics_endpoint():
    response = client.get("/metrics/feedback")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "feedback" in data
    assert "total_feedback" in data["feedback"]
    assert "positive_feedback" in data["feedback"]
    assert "negative_feedback" in data["feedback"]
    assert "positive_feedback_rate" in data["feedback"]

def test_quality_metrics_endpoint():
    response = client.get("/metrics/quality")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "quality" in data
    assert "positive_feedback_rate" in data["quality"]
    assert "total_feedback" in data["quality"]

def test_quality_metrics_endpoint():
    response = client.get("/metrics/quality")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "quality" in data

    quality = data["quality"]

    assert "average_evaluator_score" in quality
    assert "evaluation_count" in quality
    assert "positive_feedback_rate" in quality
    assert "total_feedback" in quality
    assert "positive_feedback" in quality
    assert "negative_feedback" in quality

def test_business_metrics_are_exposed():
    response = client.get("/metrics/quality")

    assert response.status_code == 200

    data = response.json()

    assert "business" in data

    business = data["business"]

    assert "accounting_questions_answered" in business
    assert "accounting_questions_abstained" in business
    assert "transaction_explanations" in business
    assert "total_accounting_questions" in business
    assert "answer_rate" in business

def test_metrics_summary_endpoint():
    response = client.get("/metrics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "requests" in data
    assert "rag" in data
    assert "quality" in data
    assert "feedback" in data
    assert "business" in data