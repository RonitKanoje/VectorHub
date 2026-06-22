from sqlalchemy.orm import Session
from threadcore.domains.analyst.models import DatasetDB


def create_dataset(
    db: Session, ## SQLAlchemy's database connection object.
    thread_id: str,
    name: str,
    file_path: str,
    file_type: str,
    row_count: str,
    column_count: str,
    status: str = "READY"
) -> DatasetDB:
    dataset = DatasetDB(
        thread_id=thread_id,
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
