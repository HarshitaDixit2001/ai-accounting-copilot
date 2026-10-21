from app.core.exceptions import AccountingValidationError
from app.services.journal_entry_service import create_double_entry
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base

from app.models.invoice import Invoice
from app.models.transaction import AccountingTransaction
from app.models.journal_entry import JournalEntry


from app.repositories.invoice_repository import (
    create_invoice,
    get_invoice_by_id,
)

from app.repositories.transaction_repository import (
    create_transaction,
)

from app.repositories.journal_entry_repository import (
    create_journal_entry,
    get_entries_by_transaction,
)

from app.core.exceptions import (
    AccountingValidationError,
    InvoiceNotFoundError,
)
TEST_DATABASE_URL = "sqlite:///:memory:"


engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def test_create_invoice():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    invoice = Invoice(
        invoice_number="TEST-001",
        vendor="Test Vendor",
        amount=5000,
        description="Database test invoice",
    )

    saved_invoice = create_invoice(
        db,
        invoice,
    )

    assert saved_invoice.id is not None
    assert saved_invoice.invoice_number == "TEST-001"
    assert saved_invoice.vendor == "Test Vendor"
    assert saved_invoice.amount == 5000

    db.close()

    Base.metadata.drop_all(bind=engine)


def test_get_invoice_by_id():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    invoice = Invoice(
        invoice_number="TEST-002",
        vendor="Retrieval Vendor",
        amount=7500,
        description="Invoice retrieval test",
    )

    saved_invoice = create_invoice(
        db,
        invoice,
    )

    fetched_invoice = get_invoice_by_id(
        db,
        saved_invoice.id,
    )

    assert fetched_invoice is not None
    assert fetched_invoice.id == saved_invoice.id
    assert fetched_invoice.invoice_number == "TEST-002"
    assert fetched_invoice.vendor == "Retrieval Vendor"
    assert fetched_invoice.amount == 7500

    db.close()

    Base.metadata.drop_all(bind=engine)


def test_create_transaction():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    transaction = AccountingTransaction(
        transaction_type="expense",
        amount=2500,
        description="Office supplies",
        reference_number="TXN-001",
    )

    saved_transaction = create_transaction(
        db,
        transaction,
    )

    assert saved_transaction.id is not None
    assert saved_transaction.transaction_type == "expense"
    assert saved_transaction.amount == 2500
    assert saved_transaction.description == "Office supplies"
    assert saved_transaction.reference_number == "TXN-001"
    assert saved_transaction.created_at is not None

    db.close()

    Base.metadata.drop_all(bind=engine)

def test_create_journal_entries():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    transaction = AccountingTransaction(
        transaction_type="expense",
        amount=2500,
        description="Office supplies",
        reference_number="TXN-JE-001",
    )

    saved_transaction = create_transaction(
        db,
        transaction,
    )

    debit_entry = JournalEntry(
        transaction_id=saved_transaction.id,
        account_name="Office Supplies",
        debit=2500,
        credit=0,
    )

    credit_entry = JournalEntry(
        transaction_id=saved_transaction.id,
        account_name="Cash",
        debit=0,
        credit=2500,
    )

    saved_debit = create_journal_entry(
        db,
        debit_entry,
    )

    saved_credit = create_journal_entry(
        db,
        credit_entry,
    )

    assert saved_debit.id is not None
    assert saved_credit.id is not None

    entries = get_entries_by_transaction(
        db,
        saved_transaction.id,
    )

    assert len(entries) == 2

    total_debit = sum(
        entry.debit
        for entry in entries
    )

    total_credit = sum(
        entry.credit
        for entry in entries
    )

    assert total_debit == 2500
    assert total_credit == 2500
    assert total_debit == total_credit

    db.close()

    Base.metadata.drop_all(bind=engine)

def test_journal_entry_rejects_negative_amount():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    transaction = AccountingTransaction(
        transaction_type="expense",
        amount=2500,
        description="Negative amount test",
        reference_number="TXN-NEG-001",
    )

    saved_transaction = create_transaction(
        db,
        transaction,
    )

    try:
        create_double_entry(
            db,
            transaction_id=saved_transaction.id,
            debit_account="Office Supplies",
            credit_account="Cash",
            amount=-500,
        )

        assert False, "Expected AccountingValidationError"

    except AccountingValidationError as exc:
        assert str(exc) == (
            "Transaction amount must be greater than zero"
        )

    db.close()

    Base.metadata.drop_all(bind=engine)

def test_journal_entry_rejects_same_accounts():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    transaction = AccountingTransaction(
        transaction_type="expense",
        amount=2500,
        description="Same account test",
        reference_number="TXN-SAME-001",
    )

    saved_transaction = create_transaction(
        db,
        transaction,
    )

    try:
        create_double_entry(
            db,
            transaction_id=saved_transaction.id,
            debit_account="Cash",
            credit_account="Cash",
            amount=2500,
        )

        assert False, "Expected AccountingValidationError"

    except AccountingValidationError as exc:
        assert str(exc) == (
            "Debit account and credit account must be different"
        )

    db.close()

    Base.metadata.drop_all(bind=engine)

def test_journal_entry_rejects_zero_amount():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    transaction = AccountingTransaction(
        transaction_type="expense",
        amount=2500,
        description="Zero amount test",
        reference_number="TXN-ZERO-001",
    )

    saved_transaction = create_transaction(
        db,
        transaction,
    )

    try:
        create_double_entry(
            db,
            transaction_id=saved_transaction.id,
            debit_account="Office Supplies",
            credit_account="Cash",
            amount=0,
        )

        assert False, "Expected AccountingValidationError"

    except AccountingValidationError as exc:
        assert str(exc) == (
            "Transaction amount must be greater than zero"
        )

    db.close()

    Base.metadata.drop_all(bind=engine)

def test_journal_entry_rejects_nonexistent_transaction():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        create_double_entry(
            db,
            transaction_id=999999,
            debit_account="Office Supplies",
            credit_account="Cash",
            amount=2500,
        )

        assert False, "Expected InvoiceNotFoundError"

    except InvoiceNotFoundError as exc:
        assert exc.invoice_number == "Transaction 999999"

    db.close()

    Base.metadata.drop_all(bind=engine)