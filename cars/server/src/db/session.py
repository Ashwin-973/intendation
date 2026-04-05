from __future__ import annotations

import sys
from pathlib import Path
from typing import Generator


# _root = Path(__file__).resolve().parents[3]  
# if str(_root) not in sys.path:
#     sys.path.insert(0, str(_root))

from data import CAR_DB
from src.exceptions import DatabaseException
from src.logger import get_logger

logger = get_logger(__name__)


def get_db()->Generator[list[dict],None,None]:
    """
    yield the in-memory car database.

    mimics a real database session: we "open" the resource,
    yield it to the endpoint, then "close" (log) after the
    request is done
    """

    logger.debug("DB session opened")
    try:
        if CAR_DB is None:
            raise DatabaseException(
                "CAR_DB is None- the in-memory database was not initialised.",
                context={"db_type": "in-memory list"},
            )
        yield CAR_DB
    except DatabaseException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error while accessing the database", exc_info=exc)
        raise DatabaseException(
            "Unexpected database access failure.",
            context={"original_error": str(exc)},
        ) from exc
    finally:
        logger.debug("DB session closed")




