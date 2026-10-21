import logging
from collections import defaultdict
from threading import Lock


logger = logging.getLogger(__name__)


_request_metrics = defaultdict(
    lambda: {
        "count": 0,
        "total_duration_ms": 0.0,
        "slow_request_count": 0,
    }
)
_evaluation_metrics = {
    "evaluation_count": 0,
    "total_evaluator_score": 0.0,
}

_rag_metrics = {
    "request_count": 0,
    "total_retrieval_duration_ms": 0.0,
    "total_llm_duration_ms": 0.0,
    "abstention_count": 0,
}
_feedback_metrics = {
    "total_feedback": 0,
    "positive_feedback": 0,
    "negative_feedback": 0,
}
_metrics_lock = Lock()

SLOW_REQUEST_THRESHOLD_MS = 1000.0


def record_request(
    path: str,
    duration_ms: float,
) -> None:
    with _metrics_lock:
        metrics = _request_metrics[path]

        metrics["count"] += 1
        metrics["total_duration_ms"] += duration_ms

        if duration_ms >= SLOW_REQUEST_THRESHOLD_MS:
            metrics["slow_request_count"] += 1


def record_rag_request(
    retrieval_duration_ms: float,
    llm_duration_ms: float = 0.0,
    abstained: bool = False,
) -> None:
    with _metrics_lock:
        _rag_metrics["request_count"] += 1
        _rag_metrics["total_retrieval_duration_ms"] += (
            retrieval_duration_ms
        )
        _rag_metrics["total_llm_duration_ms"] += (
            llm_duration_ms
        )

        if abstained:
            _rag_metrics["abstention_count"] += 1


def get_request_metrics() -> dict:
    with _metrics_lock:
        result = {}

        for path, metrics in _request_metrics.items():
            count = metrics["count"]
            total_duration = metrics["total_duration_ms"]

            result[path] = {
                "request_count": count,
                "total_duration_ms": round(
                    total_duration,
                    2,
                ),
                "average_duration_ms": round(
                    total_duration / count,
                    2,
                )
                if count
                else 0.0,
                "slow_request_count": metrics[
                    "slow_request_count"
                ],
            }

        return result


def get_rag_metrics() -> dict:
    with _metrics_lock:
        request_count = _rag_metrics["request_count"]

        return {
            "request_count": request_count,
            "average_retrieval_duration_ms": round(
                _rag_metrics[
                    "total_retrieval_duration_ms"
                ]
                / request_count,
                2,
            )
            if request_count
            else 0.0,
            "average_llm_duration_ms": round(
                _rag_metrics[
                    "total_llm_duration_ms"
                ]
                / request_count,
                2,
            )
            if request_count
            else 0.0,
            "abstention_count": _rag_metrics[
                "abstention_count"
            ],
        }

def record_feedback(rating: int) -> None:
    with _metrics_lock:
        _feedback_metrics["total_feedback"] += 1

        if rating == 1:
            _feedback_metrics["positive_feedback"] += 1
        else:
            _feedback_metrics["negative_feedback"] += 1


def get_feedback_metrics() -> dict:
    with _metrics_lock:
        total_feedback = _feedback_metrics["total_feedback"]
        positive_feedback = _feedback_metrics["positive_feedback"]
        negative_feedback = _feedback_metrics["negative_feedback"]

        return {
            "total_feedback": total_feedback,
            "positive_feedback": positive_feedback,
            "negative_feedback": negative_feedback,
            "positive_feedback_rate": round(
                positive_feedback / total_feedback,
                3,
            ) if total_feedback else 0.0,
        }

def get_quality_metrics() -> dict:
    feedback = get_feedback_metrics()
    evaluation = get_evaluation_metrics()

    return {
        "average_evaluator_score": evaluation["average_evaluator_score"],
        "evaluation_count": evaluation["evaluation_count"],
        "positive_feedback_rate": feedback["positive_feedback_rate"],
        "total_feedback": feedback["total_feedback"],
        "positive_feedback": feedback["positive_feedback"],
        "negative_feedback": feedback["negative_feedback"],
    }

def record_evaluator_score(score: float) -> None:
    with _metrics_lock:
        _evaluation_metrics["evaluation_count"] += 1
        _evaluation_metrics["total_evaluator_score"] += score


def get_evaluation_metrics() -> dict:
    with _metrics_lock:
        count = _evaluation_metrics["evaluation_count"]
        total_score = _evaluation_metrics["total_evaluator_score"]

        return {
            "evaluation_count": count,
            "average_evaluator_score": round(
                total_score / count,
                3,
            ) if count else 0.0,
        }

_business_metrics = {
    "accounting_questions_answered": 0,
    "accounting_questions_abstained": 0,
    "transaction_explanations": 0,
}


def record_business_outcome(
    *,
    abstained: bool,
    transaction_explanation: bool = False,
) -> None:
    with _metrics_lock:
        if abstained:
            _business_metrics[
                "accounting_questions_abstained"
            ] += 1
        else:
            _business_metrics[
                "accounting_questions_answered"
            ] += 1

        if transaction_explanation:
            _business_metrics[
                "transaction_explanations"
            ] += 1


def get_business_metrics() -> dict:
    with _metrics_lock:
        answered = _business_metrics[
            "accounting_questions_answered"
        ]
        abstained = _business_metrics[
            "accounting_questions_abstained"
        ]
        transactions = _business_metrics[
            "transaction_explanations"
        ]

        total_questions = answered + abstained

        return {
            "accounting_questions_answered": answered,
            "accounting_questions_abstained": abstained,
            "transaction_explanations": transactions,
            "total_accounting_questions": total_questions,
            "answer_rate": round(
                answered / total_questions,
                3,
            ) if total_questions else 0.0,
        }