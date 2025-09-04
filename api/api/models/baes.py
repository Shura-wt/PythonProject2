

from ..templates.TimestampMixin import TimestampMixin
from . import db


class Baes(TimestampMixin,db.Model):
    __tablename__ = 'baes'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=True)
    label = db.Column(db.String(50), nullable=True)
    position = db.Column(db.JSON, nullable=False)

    # La clé étrangère est optionnelle (nullable=True) car une BAES peut ne pas être affectée à un étage.
    etage_id = db.Column(db.Integer, db.ForeignKey('etages.id', ondelete='SET NULL'), nullable=True)
    # Relation one-to-many : Une BAES a plusieurs statuts.
    # Cascade delete-orphan pour supprimer les statuts associés lors de la suppression d'une BAES
    statuses = db.relationship('Status', backref='baes', lazy=True, cascade="all, delete-orphan")


    def __repr__(self):
        return f"<BAES {self.name}>"
