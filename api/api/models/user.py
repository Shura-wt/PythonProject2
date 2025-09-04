from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from ..templates.TimestampMixin import TimestampMixin
class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Relation vers le modèle d'association
    user_site_roles = db.relationship('UserSiteRole', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.login}>"
