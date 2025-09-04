

from ..templates.TimestampMixin import TimestampMixin
from . import db


class Etage(TimestampMixin,db.Model):
    __tablename__ = 'etages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    batiment_id = db.Column(db.Integer, db.ForeignKey('batiments.id', ondelete='CASCADE'), nullable=False)

    # One-to-one vers Carte via etage_id
    carte = db.relationship('Carte', backref='etage', uselist=False, foreign_keys='Carte.etage_id', passive_deletes=True)
    # One-to-many vers BAES un etaage a plusieurs BAES
    baes = db.relationship('Baes', backref='etage', lazy=True, passive_deletes=True)


    def __repr__(self):
        return f"<Etage {self.name}>"
