from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "service": "AI Accounting Copilot",
        "version": "0.1.0",
        "environment": "production",
    }


def test_readiness_check():
    response = client.get("/ready")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ready",
        "service": "AI Accounting Copilot",
        "version": "0.1.0",
        "environment": "production",
        "database": "available",
        "ollama": "available",
    }


def test_unhandled_exception_returns_safe_error():
    import asyncio
    import json
    from unittest.mock import Mock

    from app.main import global_exception_handler

    request = Mock()
    request.url.path = "/test"

    response = asyncio.run(
        global_exception_handler(
            request,
            RuntimeError("secret internal failure"),
        )
    )

    assert response.status_code == 500
    assert response.body

    body = json.loads(response.body)

    assert body["error"] == "internal_server_error"
    assert body["message"] == (
        "An unexpected internal error occurred."
    )


def test_request_metrics_track_slow_requests():
    from app.core.metrics import (
        SLOW_REQUEST_THRESHOLD_MS,
        get_request_metrics,
        record_request,
    )

    test_path = "/test-metrics"

    record_request(
        path=test_path,
        duration_ms=SLOW_REQUEST_THRESHOLD_MS + 100,
    )

    metrics = get_request_metrics()

    assert test_path in metrics

    assert metrics[test_path]["request_count"] == 1
    assert metrics[test_path]["slow_request_count"] == 1
    assert metrics[test_path]["total_duration_ms"] == (
        SLOW_REQUEST_THRESHOLD_MS + 100
    )


def test_metrics_endpoint_returns_metrics_when_enabled():
    from app.core.config import settings

    original_value = settings.EXPOSE_METRICS

    try:
        settings.EXPOSE_METRICS = True

        response = client.get("/metrics")

        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    finally:
        settings.EXPOSE_METRICS = original_value


def test_metrics_endpoint_can_be_disabled():
    from app.core.config import settings

    original_value = settings.EXPOSE_METRICS

    try:
        settings.EXPOSE_METRICS = False

        response = client.get("/metrics")

        assert response.status_code == 200

        assert response.json() == {
            "status": "disabled",
            "message": "Metrics endpoint is disabled.",
        }

    finally:
        settings.EXPOSE_METRICS = original_value


def test_readiness_check_returns_503_when_database_unavailable():
    from unittest.mock import patch

    with patch(
        "app.api.routes.health.engine.connect",
        side_effect=Exception("database unavailable"),
    ), patch(
        "app.api.routes.health.urllib.request.urlopen",
        side_effect=Exception("ollama unavailable"),
    ):
        response = client.get("/ready")

    assert response.status_code == 503

    assert response.json() == {
        "status": "not_ready",
        "service": "AI Accounting Copilot",
        "version": "0.1.0",
        "environment": "production",
        "database": "unavailable",
        "ollama": "unavailable",
    }


def test_readiness_check_returns_503_when_ollama_unavailable():
    from unittest.mock import patch

    with patch(
        "app.api.routes.health.engine.connect",
    ), patch(
        "app.api.routes.health.urllib.request.urlopen",
        side_effect=Exception("ollama unavailable"),
    ):
        response = client.get("/ready")

    assert response.status_code == 503

    assert response.json() == {
        "status": "not_ready",
        "service": "AI Accounting Copilot",
        "version": "0.1.0",
        "environment": "production",
        "database": "available",
        "ollama": "unavailable",
    }


def test_rag_metrics_track_retrieval_llm_and_abstentions():
    from app.core.metrics import (
        get_rag_metrics,
        record_rag_request,
    )

    record_rag_request(
        retrieval_duration_ms=100.0,
        llm_duration_ms=500.0,
        abstained=False,
    )

    record_rag_request(
        retrieval_duration_ms=200.0,
        llm_duration_ms=0.0,
        abstained=True,
    )

    metrics = get_rag_metrics()

    assert metrics["request_count"] >= 2
    assert metrics["average_retrieval_duration_ms"] > 0
    assert metrics["average_llm_duration_ms"] > 0
    assert metrics["abstention_count"] >= 1