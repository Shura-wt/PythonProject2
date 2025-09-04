from sqlalchemy import DateTime

from ..templates.TimestampMixin import TimestampMixin
from . import db
from datetime import *  # Importation de datetime



def current_time():
    return datetime.now(timezone.utc)

class Status(TimestampMixin,db.Model):
    __tablename__ = 'status'

    id = db.Column(db.Integer, primary_key=True , autoincrement=True)
    baes_id = db.Column(db.BigInteger, db.ForeignKey('baes.id'), nullable=False)
    erreur = db.Column(db.Integer, name='erreur', nullable=False)
    is_solved = db.Column(db.Boolean, default=False, nullable=False)
    is_ignored = db.Column(db.Boolean, default=False, nullable=False)
    temperature = db.Column(db.Float, nullable=True)
    vibration = db.Column(db.Boolean, nullable=True, default=False)
    acknowledged_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    acknowledged_at = db.Column(DateTime(timezone=True), nullable=True)

    # Ajouter cette relation
    acknowledged_by = db.relationship('User', foreign_keys=[acknowledged_by_user_id])

    # Contrainte d'unicité fonctionnelle sur baes_id et erreur
    #__table_args__ = (
    #    db.UniqueConstraint('baes_id', 'erreur', name='uq_baes_erreur'),
    #)

    timestamp = db.Column(
        DateTime(timezone=True),
        default=current_time,
        nullable=False
    )

    def __repr__(self):
        return f"<Status(baes_id={self.baes_id}, erreur={self.erreur}, timestamp={self.timestamp})>"
