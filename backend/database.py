from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()

class ConferenceRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    votes = db.Column(db.Integer, default=0)
    vote_ips = db.relationship('Vote', backref='conference_room', lazy=True)

    @hybrid_property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'votes': self.votes,
        }

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('conference_room.id'), nullable=False)
