from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    sticker_offers = db.relationship('StickerOffer', backref='user', lazy=True)
    sticker_wanted = db.relationship('StickerWanted', backref='user', lazy=True)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50), nullable=False)

    def __repr__(self):
        return f"Team(id={self.id}, name={self.name})"

class Sticker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team = db.relationship('Team', backref=db.backref('stickers', lazy=True))


class StickerOffer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sticker_id = db.Column(db.Integer, db.ForeignKey('sticker.id'), nullable=False)
    sticker = db.relationship('Sticker')
    amount = db.Column(db.Integer, nullable=False)

class StickerWanted(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sticker_id = db.Column(db.Integer, db.ForeignKey('sticker.id'), nullable=False)
    sticker = db.relationship('Sticker')