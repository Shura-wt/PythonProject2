
from ..templates.TimestampMixin import TimestampMixin
from . import db

class Role(TimestampMixin, db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Relation vers UserSiteRole (à supprimer pour éviter le conflit)
    # user_roles = db.relationship('UserSiteRole', backref='role', lazy='dynamic')

    def __repr__(self):
        return f"<Role {self.name}>"
