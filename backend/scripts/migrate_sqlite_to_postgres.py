import argparse
from typing import Iterable

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import (
    Tenant,
    User,
    Company,
    Campaign,
    VoiceAgent,
    CallLog,
    AuditLog,
)


MODEL_ORDER: Iterable[type] = (
    Tenant,
    User,
    Company,
    Campaign,
    VoiceAgent,
    CallLog,
    AuditLog,
)


def to_sync_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return "postgresql+psycopg2://" + url[len("postgresql+asyncpg://"):]
    if url.startswith("sqlite+aiosqlite://"):
        return "sqlite://" + url[len("sqlite+aiosqlite://"):]
    return url


def copy_table(source: Session, target: Session, model: type) -> int:
    rows = source.execute(select(model)).scalars().all()
    for row in rows:
        payload = {column.name: getattr(row, column.name) for column in model.__table__.columns}
        target.merge(model(**payload))
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate FRACTO data from SQLite to PostgreSQL.",
    )
    parser.add_argument(
        "--source",
        default="sqlite:///./fracto.db",
        help="Source DB URL (default: sqlite:///./fracto.db)",
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Target PostgreSQL URL, e.g. postgresql://user:pass@host:5432/fracto",
    )
    args = parser.parse_args()

    source_url = to_sync_url(args.source)
    target_url = to_sync_url(args.target)

    source_engine = create_engine(source_url, future=True)
    target_engine = create_engine(target_url, future=True)

    with Session(source_engine) as source_session, Session(target_engine) as target_session:
        total_rows = 0
        for model in MODEL_ORDER:
            copied = copy_table(source_session, target_session, model)
            total_rows += copied
            print(f"{model.__tablename__}: copied {copied} rows")
        target_session.commit()

    print(f"Done. Copied total rows: {total_rows}")


if __name__ == "__main__":
    main()
