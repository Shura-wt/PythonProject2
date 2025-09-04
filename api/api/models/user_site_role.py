from . import db
from ..templates.TimestampMixin import TimestampMixin

class UserSiteRole(TimestampMixin, db.Model):
    __tablename__ = 'user_site_role'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id', ondelete='CASCADE'), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    # Relation avec Site et Role
    site = db.relationship('Site', backref=db.backref('user_site_roles', lazy='dynamic'))
    role = db.relationship('Role', backref=db.backref('user_site_roles', lazy='dynamic'))

    def __repr__(self):
        return f"<UserSiteRole id={self.id}, user_id={self.user_id}, site_id={self.site_id}, role_id={self.role_id}>"
