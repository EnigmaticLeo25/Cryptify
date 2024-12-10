from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify,make_response
from controller import *
from database import db

def configure_routes(app):
    @app.route('/',methods=['GET','POST'])
    def login():
        if request.method == "GET":
            return render_template('login.html')
        elif request.method == "POST":
            email = request.form.get('email')
            password = request.form.get('password')
            return_details = check_user(email,password)
            if(return_details[0]):
                flash('Login successful!', 'success')
                response = make_response(redirect(url_for('home')))
                response.set_cookie(return_details[1].username,return_details[1].email)
                return response
            else:
                flash('Invalid username or password', 'danger')
                return redirect(url_for('register'))
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == "GET":
            return render_template('register.html')
        elif request.method == "POST":
            fullname = request.form.get('fullname')
            email = request.form.get('email')
            phone_no = request.form.get('phone_no')
            username = request.form.get('username')
            password = request.form.get('password')
            new_user = register_user(fullname,email,phone_no,username,password)
            return redirect(url_for('home'))
    @app.route('/home')
    def home():
        users = User.query.all()
        return render_template('home.html',users=users)
    
    
