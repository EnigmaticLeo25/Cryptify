from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify,make_response
from controller import *
from database import db
from controller import supabase

def configure_routes(app):
    @app.route('/login',methods=['GET','POST'])
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
                response.set_cookie("authToken",return_details[1][0]["username"])
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
    @app.route('/')
    def home():
        auth_token = request.cookies.get('authToken')
        if auth_token:
            users = (
                supabase.table("User").select().execute()
            ).data
            return render_template('home.html',users=users,user_cookie = auth_token)
        else:
            users = (
                supabase.table("User").select().execute()
            ).data
            return render_template('home.html',users=users)
        
    @app.route('/logout')
    def logout():
        response = make_response(redirect(url_for('login')))
        response.set_cookie('authToken', '', expires=0)  
        return response
    
    @app.route('/bank',methods=['GET', 'POST'])
    def bank():
        if request.method == "POST":
            
            auth_token = request.cookies.get('authToken')
            priv_key = request.form.get('priv_key')
            balance = getBalance(priv_key)
            if auth_token:
                if balance!=-1:
                    users = (
                supabase.table("User").select().execute()
            )
                    return render_template('home.html',users=users,user_cookie = auth_token,bank_details=balance)
                else:
                    users = (
                supabase.table("User").select().execute()
            )
                    return render_template('home.html',users=users,user_cookie = auth_token)    
            else:
                users = (
                supabase.table("User").select().execute()
                )
                return render_template('home.html',users=users)
        
    
    
