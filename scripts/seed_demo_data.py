import sys
from pathlib import Path


def bootstrap_backend() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    backend_root = repo_root / "backend" / "api"
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


def main() -> None:
    bootstrap_backend()
    try:
        from app.db.base import Base
        from app.db.postgres import SessionLocal, engine
        from app.models import AlertPreference, DeviceToken, ForecastLog, NotificationLog, SavedLocation, User, UserProfile
        from scripts.seed_demo import seed_demo
    except ModuleNotFoundError as exc:
        print("Missing backend dependencies. Install backend requirements first.")
        print("Run: pip install -r backend/api/requirements.txt")
        raise SystemExit(1) from exc

    _ = (User, UserProfile, SavedLocation, AlertPreference, DeviceToken, ForecastLog, NotificationLog)
    Base.metadata.create_all(bind=engine)

    try:
        with SessionLocal() as session:
            seeded_user = seed_demo(session)
            print("Demo seed complete")
            print(f"user_id={seeded_user.id}")
            print(f"firebase_uid={seeded_user.firebase_uid}")
            print(f"email={seeded_user.email}")
    except Exception as exc:  # pragma: no cover - runtime environment dependent
        print("Demo seed failed. Ensure PostgreSQL is running and backend env is configured.")
        print(f"Error: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
