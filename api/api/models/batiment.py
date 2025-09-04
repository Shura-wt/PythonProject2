

from ..templates.TimestampMixin import TimestampMixin
from . import db


class Batiment(TimestampMixin,db.Model):
    __tablename__ = 'batiments'

    id = db.Column(db.Integer, primary_key=True)
    polygon_points = db.Column(db.JSON)
    name = db.Column(db.String(50), nullable=False)
    # La clé étrangère est optionnelle (nullable=True) car un bâtiment peut ne pas appartenir à un site.
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=True)
    # Relation one-to-many : Un bâtiment a plusieurs étages.
    # Utilise passive_deletes pour laisser la BDD gérer la suppression en cascade des étages
    etages = db.relationship('Etage', backref='batiment', lazy=True, passive_deletes=True)




    def __repr__(self):
        return f"<Batiment {self.name}>"
