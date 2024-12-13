from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify,make_response
from controller import *
from controller import supabase
import json

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
            keys = register_user(fullname,email,phone_no,username,password)
            return redirect(url_for('home',pub_key=keys[0],priv_key=keys[1]))
   
    @app.route('/')
    def home():
        auth_token = request.cookies.get('authToken')
        priv_key = request.args.get('priv_key')
        pub_key = request.args.get('pub_key')
        bank_details_json = request.args.get('bank_details')
        if bank_details_json:
            bank_details_json = bank_details_json.replace("'", '"')
            bank_details = json.loads(bank_details_json)
        else:
            bank_details = None
        if auth_token:
            return render_template('home.html',user_cookie = auth_token, priv_key = priv_key,pub_key=pub_key, bank_details = bank_details)
        else:
            return render_template('home.html')
        
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
            user = getBalance_priv(priv_key)
            user_json = json.dumps(user)
            return redirect(url_for('home',bank_details=user_json))
    @app.route("/database")
    def database():
        data_User = (
                supabase.table("User").select().execute()
                ).data
        data_Bank = (
                supabase.table("Bank").select().execute()
                ).data
        data_Transactions = (
                supabase.table("Transactions").select().execute()
                ).data
        return render_template('database.html',data_User=data_User,data_Bank=data_Bank,data_Transactions=data_Transactions)

    @app.route("/transactions",methods=['GET','POST'])
    def transactions():
        if request.method == "GET":
            return render_template("transactions.html")
        if request.method == "POST":
            sender_priv_key = request.form.get('sender_priv_key')
            receiver_pub_key = request.form.get('receiver_pub_key')
            amount = request.form.get('amount')

            sender = getBalance_priv(sender_priv_key)
            receiver = getBalance_pub(receiver_pub_key)
            transaction = doTransaction(sender,receiver,amount)
            return redirect(url_for('home'))
        
    # @app.route("/account",methods=['POST'])
    # def account():
    #     if request.method == 'POST':
    #         accountName = request.form.get('accountId')
    #         account = getAccount(accountName)
    #         if account == -1:
    #             flash('Wrong username entered')
    #             return render_template('transactions.html')
    #         else:
    #             return render_template('transactions.html',accountVerified = True)
    
