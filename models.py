from flask_sqlalchemy import SQLAlchemy
from passlib.context import CryptContext

db = SQLAlchemy()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    balance = db.Column(db.Float, default=10.0)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = pwd_context.hash(password)

    def check_password(self, password):
        return pwd_context.verify(password, self.password_hash)
