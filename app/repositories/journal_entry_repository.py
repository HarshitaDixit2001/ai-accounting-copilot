from sqlalchemy.orm import Session

from app.models.journal_entry import JournalEntry


def create_journal_entry(
    db: Session,
    journal_entry: JournalEntry,
) -> JournalEntry:
    db.add(journal_entry)
    db.commit()
    db.refresh(journal_entry)

    return journal_entry


def get_entries_by_transaction(
    db: Session,
    transaction_id: int,
) -> list[JournalEntry]:
    return (
        db.query(JournalEntry)
        .filter(
            JournalEntry.transaction_id == transaction_id
        )
        .all()
    )


def get_all_journal_entries(
    db: Session,
) -> list[JournalEntry]:
    return db.query(JournalEntry).all()