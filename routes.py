from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from controller import *

def configure_routes(app):
    @app.route('/',methods=['GET','POST'])
    def login():
        if request.method == "GET":
            return render_template('login.html')
        elif request.method == "POST":
            username = request.form.get('username')
            password = request.form.get('password')
            if(check_user(username,password)):
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'danger')
    
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
