from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create tables and seed the default demo analyst user."""
    from app.models import user, incident, evidence  # noqa: F401  (register models)
    Base.metadata.create_all(bind=engine)

    from app.core.security import get_password_hash
    from app.models.user import User

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "analyst@incidentzero.ai").first()
        if not existing:
            demo_user = User(
                name="Demo Analyst",
                email="analyst@incidentzero.ai",
                password_hash=get_password_hash("demo123"),
            )
            db.add(demo_user)
            db.commit()
    finally:
        db.close()
