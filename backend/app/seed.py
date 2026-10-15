from sqlalchemy.orm import Session
from app.core.config import settings
from app.models import User
from app.security import hash_password

def ensure_admin(db: Session) -> None:
    existing = db.query(User).filter(User.username == settings.bootstrap_admin_username).first()
    if existing:
        return
    db.add(User(
        username=settings.bootstrap_admin_username,
        password_hash=hash_password(settings.bootstrap_admin_password),
        role="admin",
        active=True,
    ))
    db.commit()
