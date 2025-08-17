from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask_app.app import app as flask_app  # Import your Flask app
from flask_app.dash_app import app as dash_app  # Import your Dash app

# Gunicorn will look for `server`
server = DispatcherMiddleware(
    flask_app,  # Serve Flask at "/"
    {
        "/dash": dash_app.server  # Serve Dash at "/dash"
    }
)

if __name__ == "__main__":
    run_simple("0.0.0.0", 5000, server, use_reloader=True)
