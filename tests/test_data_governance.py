from app.services.data_governance import redact_sensitive_data


def test_redacts_email_address():
    text = "Customer email is john@example.com."

    result = redact_sensitive_data(text)

    assert "john@example.com" not in result
    assert "[REDACTED_EMAIL]" in result


def test_redacts_indian_phone_number():
    text = "Customer phone is 9876543210."

    result = redact_sensitive_data(text)

    assert "9876543210" not in result
    assert "[REDACTED_PHONE]" in result


def test_preserves_normal_accounting_text():
    text = "Debit Rent Expense and Credit Cash."

    result = redact_sensitive_data(text)

    assert result == text


def test_redacts_multiple_sensitive_values():
    text = (
        "Email: jane@example.com, "
        "phone: +91 9876543210"
    )

    result = redact_sensitive_data(text)

    assert "jane@example.com" not in result
    assert "9876543210" not in result
    assert "[REDACTED_EMAIL]" in result
    assert "[REDACTED_PHONE]" in result