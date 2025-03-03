from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Anomaly(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(100), nullable=False)
    power_usage = db.Column(db.Float, nullable=False)
    anomaly = db.Column(db.Boolean, default=False)

class RealTimeData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    power_usage = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {"timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "power_usage": self.power_usage}
