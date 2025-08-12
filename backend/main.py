from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# The Dash app needs `server` set for WSGI mounting (common in Dash)
# If dash_app is a Dash instance, use dash_app.server
from backend.flask.app import app as flask_app  # Import your Flask app
from backend.flask.dash_app import app as dash_app  # Import your Dash app

application = DispatcherMiddleware(
    flask_app,  # Serve Flask at "/"
    {
        "/dash": dash_app.server  # Serve Dash at "/dash"
    }
)

if __name__ == "__main__":
    # For local testing only; in production use Gunicorn!
    run_simple("0.0.0.0", 5000, application, use_reloader=True)