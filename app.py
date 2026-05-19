"""
Secure Authentication Demo Web App - Flask Backend
Secure login, signup, CSRF protection, rate limiting, and session management.
"""

import logging
import os
import re
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from logging.handlers import RotatingFileHandler
from sqlalchemy import func
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Regexp,
)
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
LOG_DIR = os.path.join(BASE_DIR, 'security_logs')
DATABASE_PATH = os.path.join(INSTANCE_DIR, 'users.db')
LOG_FILE = os.path.join(LOG_DIR, 'auth.log')

app = Flask(__name__, instance_path=INSTANCE_DIR, instance_relative_config=True)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', f'sqlite:///{DATABASE_PATH}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() in ('1', 'true', 'yes')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None

# When using Neon/PostgreSQL on Render, SQLAlchemy will use DATABASE_URL
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace(
        'postgres://', 'postgresql://', 1
    )

os.makedirs(INSTANCE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
open(LOG_FILE, 'a').close()

auth_logger = logging.getLogger('auth_logger')
auth_logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
file_handler.setFormatter(
    logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
)
auth_logger.addHandler(file_handler)
auth_logger.propagate = False


db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    identifier = db.Column(db.String(120), nullable=True)
    success = db.Column(db.Boolean, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    details = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class LoginForm(FlaskForm):
    identifier = StringField(
        'Username or Email',
        validators=[
            DataRequired(message='Username or email is required.'),
            Length(min=3, max=120, message='Enter a valid username or email.'),
        ],
    )
    password = PasswordField('Password', validators=[DataRequired(message='Password is required.')])
    remember = BooleanField('Remember Me')


class RegisterForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required.'),
            Length(min=3, max=20, message='Username must be 3-20 characters.'),
            Regexp('^[A-Za-z0-9_]+$', message='Username may only contain letters, numbers, and underscores.'),
        ],
    )
    email = StringField(
        'Email',
        validators=[DataRequired(message='Email is required.'), Email(message='Enter a valid email address.')],
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Password is required.'), Length(min=8, message='Password must be at least 8 characters.')],
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password.'),
            EqualTo('password', message='Passwords must match.'),
        ],
    )
    terms = BooleanField('Terms', validators=[DataRequired(message='You must accept the terms.')])
    privacy = BooleanField('Privacy', validators=[DataRequired(message='You must accept the privacy policy.')])


def get_client_ip():
    forwarded_for = request.headers.get('X-Forwarded-For', None)
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def log_event(event_type: str, username: str = None, email: str = None, success: bool = None, details: str = None, level: str = 'info'):
    ip_address = get_client_ip()
    user_agent = request.user_agent.string if request else 'unknown'
    parts = [event_type]
    if username:
        parts.append(f'username={username}')
    if email:
        parts.append(f'email={email}')
    if success is not None:
        parts.append(f'success={success}')
    if details:
        parts.append(f'details={details}')
    parts.append(f'ip={ip_address}')
    parts.append(f'agent={user_agent}')
    message = ' '.join(parts)

    if level == 'warning':
        auth_logger.warning(message)
    else:
        auth_logger.info(message)


def sanitize_text(value: str) -> str:
    return value.strip() if isinstance(value, str) else ''


def validate_password_policy(password: str):
    errors = []
    if len(password) < 8:
        errors.append('Password must be at least 8 characters long.')
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain an uppercase letter.')
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain a lowercase letter.')
    if not re.search(r'[0-9]', password):
        errors.append('Password must contain a number.')
    if not re.search(r'[!@#$%^&*()_+\-=[\]{};:\"\\|,.<>/?]', password):
        errors.append('Password must contain a special character.')
    return errors


def recent_failed_attempts(identifier: str = None, ip_address: str = None, minutes: int = 15) -> int:
    threshold = datetime.utcnow() - timedelta(minutes=minutes)
    query = LoginAttempt.query.filter(LoginAttempt.success.is_(False), LoginAttempt.timestamp >= threshold)
    if identifier:
        query = query.filter(func.lower(LoginAttempt.identifier) == identifier.lower())
    if ip_address:
        query = query.filter(LoginAttempt.ip_address == ip_address)
    return query.count()


def read_recent_log_entries(lines: int = 10):
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as log_file:
            entries = [line.strip() for line in log_file.readlines()[-lines:]]
        return entries[::-1]
    except OSError:
        return []


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access the dashboard.', 'warning')
            return redirect(url_for('login'))
        return view(*args, **kwargs)

    return wrapped_view


@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Content Security Policy - restrictive by default for demo
    csp = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'"
    response.headers['Content-Security-Policy'] = csp
    # HSTS when served over HTTPS (do not enable for local HTTP dev)
    try:
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    except Exception:
        pass
    return response


limiter = Limiter(app=app, key_func=get_remote_address, default_limits=[])


@app.errorhandler(429)
def too_many_requests(e):
    form = LoginForm()
    flash('Too many login attempts. Please wait and try again.', 'warning')
    return render_template('login.html', form=form), 429


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit('5 per minute')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        identifier = sanitize_text(form.identifier.data)
        password = form.password.data
        lookup = identifier.lower()
        ip_address = get_client_ip()
        locked = recent_failed_attempts(identifier=lookup, ip_address=ip_address, minutes=15) >= 5

        if locked:
            log_event('LOGIN_LOCKOUT', email=identifier, success=False, details='Rate limit exceeded')
            flash('Too many login attempts. Please wait before trying again.', 'warning')
            return render_template('login.html', form=form)

        user = User.query.filter(
            (func.lower(User.email) == lookup) | (func.lower(User.username) == lookup)
        ).first()
        authenticated = user and check_password_hash(user.password_hash, password)

        attempt = LoginAttempt(
            user_id=user.id if user else None,
            identifier=identifier,
            success=bool(authenticated),
            ip_address=ip_address,
            user_agent=request.user_agent.string,
            details='Authentication attempt',
        )
        db.session.add(attempt)
        db.session.commit()

        if authenticated:
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = bool(form.remember.data)

            user.last_login_at = datetime.utcnow()
            db.session.commit()

            log_event('LOGIN_SUCCESS', username=user.username, email=user.email, success=True)
            flash('Login successful. Welcome back.', 'success')
            return redirect(url_for('dashboard'))

        log_event('LOGIN_FAILURE', identifier=identifier, success=False, details='Invalid credentials')
        flash('Invalid username or password. Please try again.', 'error')

    elif request.method == 'POST':
        flash('Login failed. Please complete all form fields and try again.', 'error')

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit('3 per minute')
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = sanitize_text(form.username.data)
        email = sanitize_text(form.email.data).lower()
        password = form.password.data

        policy_errors = validate_password_policy(password)
        if policy_errors:
            for error in policy_errors:
                flash(error, 'error')
            return render_template('register.html', form=form)

        existing_user = User.query.filter(
            (func.lower(User.username) == username.lower()) | (func.lower(User.email) == email)
        ).first()
        if existing_user:
            flash('Username or email already exists. Please choose a different account.', 'error')
            return render_template('register.html', form=form)

        password_hash = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()

        log_event('REGISTRATION_SUCCESS', username=username, email=email, success=True)
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    elif request.method == 'POST':
        flash('Registration failed. Please review the form and try again.', 'error')

    return render_template('register.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session.get('user_id'))
    if not user:
        session.clear()
        flash('Session expired. Please log in again.', 'warning')
        return redirect(url_for('login'))

    recent_attempts = (
        LoginAttempt.query.filter_by(user_id=user.id)
        .order_by(LoginAttempt.timestamp.desc())
        .limit(6)
        .all()
    )
    failed_attempts = (
        LoginAttempt.query.filter_by(user_id=user.id, success=False)
        .filter(LoginAttempt.timestamp >= datetime.utcnow() - timedelta(days=7))
        .count()
    )
    total_logins = LoginAttempt.query.filter_by(user_id=user.id, success=True).count()
    suspicious_activity = (
        LoginAttempt.query.filter_by(user_id=user.id, success=False)
        .filter(LoginAttempt.timestamp >= datetime.utcnow() - timedelta(hours=24))
        .count()
        >= 3
    )
    audit_events = read_recent_log_entries(12)

    return render_template(
        'dashboard.html',
        user=user,
        recent_attempts=recent_attempts,
        failed_attempts=failed_attempts,
        total_logins=total_logins,
        suspicious_activity=suspicious_activity,
        audit_events=audit_events,
    )


@app.route('/logout')
def logout():
    username = session.get('username', 'anonymous')
    session.clear()
    log_event('LOGOUT', username=username, success=True)
    flash('You have been logged out securely.', 'success')
    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


def initialize_database():
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    with app.app_context():
        # Create any missing tables
        db.create_all()

        # Apply SQLite-only schema migrations if using local SQLite storage
        if db.engine.name == 'sqlite':
            try:
                raw_conn = db.engine.raw_connection()
                cursor = raw_conn.cursor()

                # Upgrade users table schema
                cursor.execute("PRAGMA table_info(users)")
                users_columns = [row[1] for row in cursor.fetchall()]
                if 'last_login_at' not in users_columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN last_login_at DATETIME")

                # Upgrade login_attempts table schema
                cursor.execute("PRAGMA table_info(login_attempts)")
                login_columns = [row[1] for row in cursor.fetchall()]
                if 'identifier' not in login_columns:
                    cursor.execute("ALTER TABLE login_attempts ADD COLUMN identifier VARCHAR(120)")
                if 'user_agent' not in login_columns:
                    cursor.execute("ALTER TABLE login_attempts ADD COLUMN user_agent VARCHAR(255)")
                if 'details' not in login_columns:
                    cursor.execute("ALTER TABLE login_attempts ADD COLUMN details VARCHAR(255)")
                if 'ip_address' not in login_columns:
                    cursor.execute("ALTER TABLE login_attempts ADD COLUMN ip_address VARCHAR(45)")

                raw_conn.commit()
                cursor.close()
                raw_conn.close()
            except Exception:
                # If migration fails, proceed; manual migration may be required
                pass


if __name__ == '__main__':
    initialize_database()
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
