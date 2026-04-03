from app.database import Base, engine

# Ensure model metadata is loaded before create_all.
from app import models  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
