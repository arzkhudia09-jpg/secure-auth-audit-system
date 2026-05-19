# Secure Authentication Audit Demo

Secure Authentication Audit Demo is a Flask application that demonstrates secure authentication best practices, hardening techniques, and audit-grade logging for portfolio and audit reporting use.

## Key Features
- Secure user registration and login with server-side validation
- Password hashing with Werkzeug and strong password policy enforcement
- CSRF protection via Flask-WTF
- Rate limiting on authentication endpoints with Flask-Limiter
- Hardened session configuration and secure cookie settings
- Authentication audit logging to `security_logs/auth.log`
- Clean responsive UI for login, registration, and dashboard
- Optional PostgreSQL/Neon support via `DATABASE_URL`

## Quickstart (Local Development)

### Prerequisites
- Python 3.8+
- Git

### Install & run

```powershell
git clone <repo-url>
cd secure-auth-audit
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` and register a test account.

## Configuration & Environment
The app reads the following environment variables:

- `SECRET_KEY` — strong secret for sessions
- `DATABASE_URL` — optional PostgreSQL connection string for Neon or other hosted Postgres
- `PORT` — optional, defaults to `5000`
- `FLASK_DEBUG` — set to `1` to enable debug mode locally
- `SESSION_COOKIE_SECURE` — set to `true` in production when using HTTPS

### Neon / PostgreSQL notes
If `DATABASE_URL` begins with `postgres://`, the app rewrites it to `postgresql://` for SQLAlchemy compatibility.

## Security Notes
- Passwords are hashed before storage with Werkzeug; plaintext passwords are never written to disk.
- All forms use CSRF tokens from Flask-WTF.
- Login endpoints are rate limited to mitigate brute-force attacks.
- The app sets security headers including CSP, X-Frame-Options, and HSTS when served over HTTPS.

## Deployment (Render)
1. Push this repository to GitHub.
2. Create a new Web Service on Render and connect your repo.
3. Set environment variables in Render: `SECRET_KEY`, `DATABASE_URL`, and `SESSION_COOKIE_SECURE`.
4. Use the default build command or:

```bash
pip install -r requirements.txt
python app.py
```

Disable debug mode for production.

## Project Structure

```
secure-auth-audit/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── tools_used.md           # Technology and tooling notes
├── audit_report_suggestions.md # Audit guidance content
├── render.yaml             # Render deployment configuration
├── templates/              # Jinja2 templates
├── static/                 # CSS and JS assets
├── instance/               # Local SQLite database storage
├── security_logs/          # Audit log files
├── screenshots/            # Visual documentation and sample output
└── unessory/               # Temporary files moved out of root
```

## Recommended Improvements
- Add multi-factor authentication (TOTP)
- Add email verification for sign-up
- Use Redis or server-side sessions in production
- Harden database access and secrets management
- Add automated tests and CI security scanning
- Enable HTTPS and monitoring for deployed apps

---

## Known Limitations
- No email delivery or verification workflow included
- No automated test suite in this repo yet
- No multi-factor authentication implemented
- Local SQLite storage is used by default unless `DATABASE_URL` is provided

## Deployment Summary

### Development
```powershell
python app.py
```

### Production
- Configure environment variables
- Use HTTPS for sessions and secure cookies
- Use a production-ready WSGI server such as Gunicorn

Example:
```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

## Documentation Files
- `README.md` — project overview and setup
- `tools_used.md` — technology notes and references
- `audit_report_suggestions.md` — audit report guidance and checklist

## Security Best Practices
1. Use strong, unique passwords
2. Protect your `SECRET_KEY` and database credentials
3. Enable HTTPS in production
4. Clear cookies on shared devices
5. Monitor login activity and audit logs

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
