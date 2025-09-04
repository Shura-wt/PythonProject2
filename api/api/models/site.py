
from . import db
from ..templates.TimestampMixin import TimestampMixin

class Site(TimestampMixin, db.Model):
    __tablename__ = 'sites'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    batiments = db.relationship('Batiment', backref='site', lazy=True)
    carte = db.relationship('Carte', backref='site', uselist=False, foreign_keys='Carte.site_id')

    # Relation vers UserSiteRole
    # user_roles = db.relationship('UserSiteRole', backref='site', lazy='dynamic')

    def __repr__(self):
        return f"<Site {self.name}>"
