from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from controller import *

def configure_routes(app):
    @app.route('/')
    def login():
        return render_template('login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == "GET":
            return render_template('register.html')
        elif request.method == "POST":
            username = request.form.get('username')
            password = request.form.get('password')
            new_user = register_user(username,password)
            return redirect(url_for('home'))
    @app.route('/home')
    def home():
        return render_template('home.html')
