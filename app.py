from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import init_db
from routes import configure_routes

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'
# Initialize the database
init_db(app)

# Configure routes
configure_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
