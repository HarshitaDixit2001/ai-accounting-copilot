import re


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"
)


def redact_sensitive_data(text: str) -> str:
    """
    Redact common sensitive data before storing it in audit records.
    """

    if not text:
        return text

    redacted = EMAIL_PATTERN.sub(
        "[REDACTED_EMAIL]",
        text,
    )

    redacted = PHONE_PATTERN.sub(
        "[REDACTED_PHONE]",
        redacted,
    )

    return redacted