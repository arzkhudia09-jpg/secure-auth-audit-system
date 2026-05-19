# Secure Authentication Audit Demo

Secure Authentication Audit Demo is an educational Flask application built to demonstrate secure authentication practices, hardening techniques, and audit-ready logging for internship and portfolio use.

## Key Features
- Secure user registration and login with server-side validation
- Password hashing (Werkzeug) and strict password policy
- CSRF protection using Flask-WTF
- Rate limiting on authentication endpoints (Flask-Limiter)
- Secure session configuration and session timeout
- Security logging (RotatingFileHandler) to `security_logs/auth.log`
- Responsive, professional dark UI for login/register/dashboard

## Quickstart (Local Development)

Prerequisites
- Python 3.8+
- Git

Install & run

```bash
git clone <repo-url>
cd secure-auth-audit
python -m venv env
env\Scripts\activate    # Windows
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` and register a test account.

## Configuration & Environment
The app reads the following environment variables:

- `SECRET_KEY` — set a strong secret for sessions (required for production)
- `PORT` — optional, defaults to 5000
- `FLASK_DEBUG` — set to `1` to enable debug mode locally

Set `SESSION_COOKIE_SECURE=True` in production and serve over HTTPS.

## Security Notes
- Passwords are hashed with Werkzeug before storage; plaintext passwords are never written to disk.
- All forms use CSRF tokens provided by Flask-WTF.
- Rate limiting helps mitigate brute-force attacks; adjust limits for your environment.
- The app sets several security headers (CSP, HSTS when over HTTPS, X-Frame-Options, etc.).

## Deployment (Render)
1. Push repository to GitHub.
2. Create a new Web Service on Render and link your GitHub repo.
3. Set environment variables in Render: `SECRET_KEY` and `PORT`.
4. Use the following build and start commands if needed:

```bash
pip install -r requirements.txt
python app.py
```

Disable debug mode in production.

## Project Structure

```
secure-auth-audit/
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── README.md
├── tools_used.md
├── audit_report_suggestions.md
├── templates/              # Jinja2 templates
├── static/                 # CSS and JS
├── instance/               # SQLite DB is created here
└── security_logs/          # Authentication audit logs
```

## Screenshots to Include
- Login page (desktop and mobile)
- Registration page with password strength
- Dashboard with recent activity and alerts

## Future Improvements
- Add multi-factor authentication (TOTP)
- Email verification for new accounts
- Use server-side session store or Redis for production
- Move to PostgreSQL for production workloads
- Add automated tests and CI security scans

---

For audit report content suggestions, see `audit_report_suggestions.md`.

- Error handling without information leakage

## 📚 Backend Integration Guide

To add backend security features, update the Flask routes in `app.py`:

### 1. Login Route
```python
@app.route('/login', methods=['POST'])
def login():
    # 1. Validate CSRF token
    # 2. Validate form inputs
    # 3. Check rate limiting
    # 4. Query user from database
    # 5. Verify password hash
    # 6. Create secure session
    # 7. Log successful/failed attempt
    # 8. Redirect to dashboard
```

### 2. Register Route
```python
@app.route('/register', methods=['POST'])
def register():
    # 1. Validate CSRF token
    # 2. Validate form inputs
    # 3. Check password policy
    # 4. Check for existing email
    # 5. Hash password
    # 6. Create database user
    # 7. Send verification email
    # 8. Log account creation
```

### 3. Dashboard Route
```python
@app.route('/dashboard')
def dashboard():
    # 1. Verify session
    # 2. Fetch user data
    # 3. Fetch login history
    # 4. Fetch security events
    # 5. Render template with data
```

## 📊 Screenshots Section

[Screenshots placeholder - add actual screenshots here]

### Login Page
- Dark theme with cyan accents
- Clean form layout with icons
- Security tips sidebar

### Registration Page
- Password strength meter
- Policy requirements checklist
- Form validation feedback

### Dashboard
- Security status overview
- Login activity timeline
- System alerts and notifications

## 🔄 Deployment

### Development
```bash
python app.py
```

### Production
- Change `debug=False` in app.py
- Use a production WSGI server (Gunicorn, uWSGI)
- Configure environment variables
- Enable HTTPS with SSL certificates
- Set up database on production server
- Configure logging to files/services
- Set up monitoring and alerting

Example with Gunicorn:
```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

## 📖 Documentation Files

- `README.md` (this file): Project overview and setup
- `tools_used.md`: Detailed technology documentation
- `audit_report.pdf`: Security audit report (placeholder)

## 🐛 Known Limitations

1. **No Backend Implementation**: Authentication logic is not implemented
2. **No Database**: User data is not persisted
3. **No Session Management**: Sessions are not tracked
4. **Frontend Only Validation**: Backend validation must be added
5. **Placeholder Data**: Dashboard shows mock data
6. **No Email Functionality**: Email verification not implemented

## 🔐 Security Best Practices

### For Users
1. Use strong, unique passwords
2. Never share your password
3. Use HTTPS connections
4. Clear cookies on shared devices
5. Check login history regularly

### For Developers
1. Always validate on server-side
2. Use parameterized queries
3. Hash passwords with strong algorithms
4. Implement rate limiting
5. Log all security events
6. Keep dependencies updated
7. Perform regular security audits

## 📞 Support & Contributions

This is a demonstration project. For production use:
1. Conduct thorough security testing
2. Implement all backend features
3. Add comprehensive error handling
4. Set up monitoring and alerts
5. Regular security audits

## 📄 License

This is a demonstration project for educational purposes.

## 🙏 Acknowledgments

- Modern security practices from OWASP
- UI design inspired by contemporary cybersecurity dashboards
- Color palette optimized for dark mode accessibility

---

**Last Updated**: May 2026
**Version**: 1.0.0 (Frontend Preview)

**Note**: This is a frontend-focused demonstration. For production deployment, comprehensive backend security implementation is required.
