from sqlalchemy.orm import Session
from threadcore.domains.analyst.models import DatasetDB
from threadcore.infrastructure.db.models import ThreadDB


def create_dataset(
    db: Session, ## SQLAlchemy's database connection object.
    thread_id: str,
    user_id : str,
    name: str,
    file_path: str,
    file_type: str,
    row_count: str,
    column_count: str,
    status: str = "READY"
) -> DatasetDB:
    thread = (
    db.query(ThreadDB)
    .filter(ThreadDB.thread_id == thread_id)
    .first()
)

    print("THREAD ID =", thread_id)
    print("THREAD FOUND =", thread)
    dataset = DatasetDB(
        thread_id=thread_id,
        user_id=user_id,
        name=name,
        file_path=file_path,
        file_type=file_type,
        row_count=row_count,
        column_count=column_count,
        status=status
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset
