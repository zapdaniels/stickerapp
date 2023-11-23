import os
from pathlib import Path

# load environment settings
import dotenv
this_dir = Path(__file__).parent
dotenv.load_dotenv(this_dir)

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_WEBSITE_KEY = os.environ['RECAPTCHA_WEBSITE_KEY']
RECAPTCHA_SECRET_KEY = os.environ['RECAPTCHA_SECRET_KEY']

import requests
from flask import (
    Flask, 
    session, 
    request, 
    render_template, 
    redirect, 
    url_for, 
    flash, 
    jsonify,
)
from flask_bcrypt import Bcrypt
from flask_session import Session
from sqlalchemy.exc import IntegrityError

from models import db, User, Team, Sticker, StickerWanted, StickerOffer
from admin_app import init_admin


app = Flask(__name__, instance_path=this_dir)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["SQLITE_DB"]
app.config['SECRET_KEY'] = os.environ["BCRYPT_SECRET_KEY"]
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True 
app.config['PERMANENT_SESSION_LIFETIME'] = int(os.environ["SESSION_LIFETIME"])
app.config['SESSION_COOKIE_MAX_AGE'] = int(os.environ["SESSION_LIFETIME"])
Session(app)

db.init_app(app)
bcrypt = Bcrypt(app)
admin = init_admin(app)

@app.route('/')
def home():
    user = session.get('user')
    stickers = []
    if user:
        sticker_wanted = StickerWanted.query.filter_by(user_id=user['id']).all()
        stickers = [sw.sticker for sw in sticker_wanted]
    return render_template('mypage.html', user=user, stickers=stickers)

@app.route('/imprint')
def imprint():
    return render_template('imprint.html')

@app.route('/stickers')
def sticker():
    user = session.get('user')
    team_id =  request.args.get("team_id", default=None, type=int)
    teams = Team.query.all()
    if team_id:
        stickers = Sticker.query.filter_by(team_id=int(team_id)).all()
    else:
        stickers = Sticker.query.all()
    sticker_ids_wanted = []
    if user:
        stickers_wanted = StickerWanted.query.filter_by(user_id=user['id']).all()
        sticker_ids_wanted = [sw.sticker_id for sw in stickers_wanted]
    return render_template('sticker.html', user=user, teams=teams, team_id=team_id, stickers=stickers, sticker_ids_wanted=sticker_ids_wanted)

@app.route('/wanted')
def wanted():
    users_wanting_any_sticker = User.query.filter(User.sticker_wanted.any()).all()
    return render_template('wanted.html', users=users_wanting_any_sticker)

@app.route('/wanted/<user_id>')
def wanted_sticker(user_id):
    user = session.get('user')
    selected_user = User.query.filter_by(id=int(user_id)).first()
    stickers = []
    if selected_user:
        sticker_wanted = StickerWanted.query.filter_by(user_id=selected_user.id).all()
        stickers = [sw.sticker for sw in sticker_wanted]
    return render_template('wanted_sticker.html', selected_user=selected_user, stickers=stickers, user=user)


@app.route('/toggle', methods=['PUT'])
def toggle():
    try:
        sticker_id = request.form.get("sticker_id", type=int)
        user_id = request.form.get("user_id", type=int)
        is_checked = request.form.get("is_checked") in ['1', 'on', 'true']
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    #if "checked" == 'true':
    sticker_wanted = StickerWanted.query.filter_by(user_id=user_id, sticker_id=sticker_id).first()
    message = "no change"
    if sticker_wanted and is_checked is False:
        # Sticker request exists, delete it
        db.session.delete(sticker_wanted)
        db.session.commit()
        message = f"removed sticker entry for user sticker={sticker_id} user={user_id}"
    if sticker_wanted is None and is_checked is True:
        new = StickerWanted(user_id=user_id, sticker_id=sticker_id)
        db.session.add(new)
        db.session.commit()
        message = f"added sticker entry for user sticker={sticker_id} user={user_id}"
    print(message)
    return jsonify({"status": "ok", "message": message})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user'] = {'email': user.email, 'id' : user.id}
            flash('Login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html', sitekey=RECAPTCHA_WEBSITE_KEY)

@app.route('/profile', methods=['GET'])
def profile():
    user = session.get('user')
    if user:
        user = User.query.filter_by(id=user['id']).first()
    if not user:
        return redirect(url_for('login'))
    return render_template('profile.html', user=user)

@app.route('/profile/edit', methods=['POST'])
def profile_edit():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    if user['id'] == request.form['user_id']:
        raise ValueError("Invalid User Activity!")
    user = db.session.query(User).get(request.form['user_id'])
    user.name = request.form['user_name']
    user.contact = request.form['user_contact']
    db.session.commit()
    flash(f'Profil aktualisiert.')
    return redirect(url_for('profile'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        recaptcha_response = request.form['g-recaptcha-response']
        response = requests.post(RECAPTCHA_VERIFY_URL, params={'response' : recaptcha_response, 'secret' : RECAPTCHA_SECRET_KEY}).json()
        if not response['success']:
            flash('Registrierung fehlgeschlagen. Recaptcha nicht akzeptiert', 'error')
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(email=email, password=hashed_password)
            try:
                db.session.add(new_user)
                db.session.commit()
                session['user'] = {'email': new_user.email, 'id' : new_user.id}
                flash(f'Registrierung erfolgreich. Vervollständige dein Profil.')
                return redirect(url_for('profile'))
            except IntegrityError as e:
                flash(f'Registrierung fehlgeschlagen. Die {email} ist bereits vergeben', 'error')
            except Exception as e:
                flash(f'Registrierung fehlgeschlagen. Fehler:\n{e}', 'error')
    return render_template('register.html', sitekey=RECAPTCHA_WEBSITE_KEY)

# Create database tables within the Flask application context
with app.app_context():
    db.create_all()