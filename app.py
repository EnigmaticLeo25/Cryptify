from flask import Flask, render_template, request, redirect, url_for, flash, session
from routes import configure_routes
import os

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'
# Initialize the database
# Configure routes
configure_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
