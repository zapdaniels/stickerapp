from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    name = db.Column(db.String(120), unique=True)
    contact = db.Column(db.String(200))
    sticker_wanted = db.relationship('StickerWanted', viewonly=True, lazy=True)
    sticker_offers = db.relationship('StickerOffer', viewonly=True, lazy=True)

    def __str__(self):
        return (self.name or self.email)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50), nullable=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Team(id={self.id}, name={self.name})"

class Sticker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team = db.relationship('Team', backref=db.backref('stickers', lazy=True))

    def __str__(self):
        return f"{self.name} ({self.team})"

class StickerWanted(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sticker_id = db.Column(db.Integer, db.ForeignKey('sticker.id'), nullable=False)
    user = db.relationship('User')
    sticker = db.relationship('Sticker')
    offers = db.relationship('StickerOffer', viewonly=True, lazy=True)#, cascade="all, delete")

    @property
    def team(self):
        return self.sticker.team

    def get_offers(self, user:User=None):
        if user is None:
            return self.offers
        return [o for o in self.offers if o.user_id == user.id]

class StickerOffer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sticker_wanted_id = db.Column(db.Integer, db.ForeignKey('sticker_wanted.id', ondelete="CASCADE"), nullable=False)
    offer_to = db.relationship('StickerWanted')
    user = db.relationship('User')
    sw = db.relationship('StickerWanted')


def delete_orphaned_sticker_offers():
    orphaned_offers = StickerOffer.query.all()
    for offer in orphaned_offers:
        if offer.sw is not None:
            continue
        db.session.delete(offer)
    db.session.commit()

