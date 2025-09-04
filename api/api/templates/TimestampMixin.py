from datetime import datetime, timezone
from sqlalchemy import Column, DateTime

def current_time():
    # Retourne l'heure actuelle en UTC avec information de fuseau horaire
    return datetime.now(timezone.utc)

class TimestampMixin:
    # Note : on précise timezone=True pour stocker un datetime aware dans la base de données
    created_at = Column(DateTime(timezone=True), default=current_time, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=current_time, onupdate=current_time, nullable=False)
