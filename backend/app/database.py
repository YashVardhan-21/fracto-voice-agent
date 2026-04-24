from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.config import settings
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from uuid import uuid4


def _make_async_url(url: str) -> str:
    """Normalise DB URLs to async drivers for SQLAlchemy async engine."""
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql+psycopg2://"):
        return "postgresql+asyncpg://" + url[len("postgresql+psycopg2://"):]
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+asyncpg://" + url[len(prefix):]
    return url


def _normalize_asyncpg_url_and_kwargs(url: str) -> tuple[str, dict]:
    """
    asyncpg does not accept `sslmode` in the URL query string.
    Convert sslmode=require/prefer/verify-* into connect_args['ssl'].
    """
    if not url.startswith("postgresql+asyncpg://"):
        return url, {}

    parts = urlsplit(url)
    query_items = parse_qsl(parts.query, keep_blank_values=True)
    keep: list[tuple[str, str]] = []
    sslmode_value: str | None = None

    for key, value in query_items:
        if key.lower() == "sslmode":
            sslmode_value = value
        else:
            keep.append((key, value))

    # Supabase pooler/pgbouncer in transaction mode is incompatible with prepared stmt caching.
    has_prepared_cache_param = any(k.lower() == "prepared_statement_cache_size" for k, _ in keep)
    if not has_prepared_cache_param:
        keep.append(("prepared_statement_cache_size", "0"))

    clean_url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(keep), parts.fragment))
    connect_args: dict = {"statement_cache_size": 0}
    if sslmode_value:
        sslmode = sslmode_value.lower()
        if sslmode in {"require", "prefer", "verify-ca", "verify-full"}:
            connect_args["ssl"] = "require"

    is_supabase_pooler = "pooler.supabase.com" in clean_url.lower()
    if is_supabase_pooler:
        connect_args["prepared_statement_name_func"] = lambda: f"__asyncpg_{uuid4()}__"
        # Pgbouncer transaction pooling is safer with no SQLAlchemy pool reuse.
        return clean_url, {"connect_args": connect_args, "poolclass": NullPool}

    if not sslmode_value:
        return clean_url, {"connect_args": connect_args}

    sslmode = sslmode_value.lower()
    if sslmode in {"disable", "allow"}:
        return clean_url, {"connect_args": connect_args}
    if sslmode in {"require", "prefer", "verify-ca", "verify-full"}:
        # Production-grade validation can be enhanced with explicit SSLContext + CA bundle.
        return clean_url, {"connect_args": connect_args}
    return clean_url, {"connect_args": connect_args}


_async_database_url = _make_async_url(settings.database_url)
_async_database_url, _async_engine_kwargs = _normalize_asyncpg_url_and_kwargs(_async_database_url)
if _async_database_url.startswith("sqlite+aiosqlite://"):
    engine = create_async_engine(
        _async_database_url,
        echo=settings.environment == "development",
    )
else:
    _engine_options = {
        "echo": settings.environment == "development",
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        **_async_engine_kwargs,
    }
    if _engine_options.get("poolclass") is not NullPool:
        _engine_options["pool_size"] = 10
        _engine_options["max_overflow"] = 20
    engine = create_async_engine(_async_database_url, **_engine_options)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
