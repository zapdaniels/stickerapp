import os
from flask import Flask, render_template, redirect, url_for, session, request, flash, jsonify

from flask_bcrypt import Bcrypt
import dotenv
import requests

from models import db, User, Team, Sticker, StickerWanted, StickerOffer
from sqlalchemy.exc import IntegrityError

dotenv.load_dotenv()


app = Flask(__name__, instance_path=os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["SQLITE_DB"]
app.config['SECRET_KEY'] = os.environ["BCRYPT_SECRET_KEY"]
db.init_app(app)
bcrypt = Bcrypt(app)

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_WEBSITE_KEY = os.environ['RECAPTCHA_WEBSITE_KEY']
RECAPTCHA_SECRET_KEY = os.environ['RECAPTCHA_SECRET_KEY']

@app.route('/')
def home():
    user = session.get('user')
    stickers = []
    if user:
        sticker_wanted = StickerWanted.query.filter_by(user_id=user['id']).all()
        stickers = [sw.sticker for sw in sticker_wanted]
    return render_template('mypage.html', user=user, stickers=stickers)

@app.route('/stickers')
def stickers():
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
    return render_template('stickers.html', user=user, teams=teams, team_id=team_id, stickers=stickers, sticker_ids_wanted=sticker_ids_wanted)

@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/users/<user_id>')
def users_stickers(user_id):
    user = session.get('user')
    selected_user = User.query.filter_by(id=int(user_id)).first()
    stickers = []
    if selected_user:
        sticker_wanted = StickerWanted.query.filter_by(user_id=selected_user.id).all()
        stickers = [sw.sticker for sw in sticker_wanted]
    return render_template('users_stickers.html', selected_user=selected_user, stickers=stickers, user=user)


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

    return render_template('login.html')

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
                return redirect(url_for('home'))
            except IntegrityError:
                flash(f'Registrierung fehlgeschlagen. Die {email} ist bereits vergeben', 'error')
            except Exception as e:
                flash(f'Registrierung fehlgeschlagen. Fehler:\n{e}', 'error')
    return render_template('register.html', sitekey=RECAPTCHA_WEBSITE_KEY)

# Create database tables within the Flask application context
with app.app_context():
    db.create_all()