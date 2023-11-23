import os

from flask import session, request, redirect, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from models import db, User, Team, Sticker, StickerWanted, StickerOffer

class View(ModelView):
    can_delete = True
    column_display_pk = True
    column_hide_backrefs = False

    def is_accessible(self):
        user = session.get('user')
        if not user:
            return False
        return user['email'] == os.environ["ADMIN_EMAIL"]

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

class UserView(View):
    column_list=('id', 'name', 'email', 'contact', 'password')

class TeamView(View):
    column_list=('id', 'name')

class StickerView(View):
    column_list=('id', 'name', 'team_id', 'team')

class StickerWantedView(View):
    column_list=('id', 'user', 'sticker')

class StickerOfferView(View):
    column_list=('id', 'user', 'offer_to')


def init_admin(app):
    admin = Admin(app, name='stickerapp', template_mode='bootstrap4')
    admin.add_view(UserView(User, db.session))
    admin.add_view(TeamView(Team, db.session))
    admin.add_view(StickerView(Sticker, db.session))
    admin.add_view(StickerWantedView(StickerWanted, db.session))
    admin.add_view(StickerOfferView(StickerOffer, db.session))
    return admin