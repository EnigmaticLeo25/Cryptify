from database import db
from sqlalchemy import Column, DateTime
from datetime import datetime

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_no = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Bank(db.Model):
    balance_id = db.Column(db.Integer, primary_key=True)
    encrypted_balance = db.Column(db.Integer, nullable=False)
    user_public_key = db.Column(db.String(50), nullable=False)

class Transactions(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    sender_balance_id = db.Column(db.Integer, nullable=False)
    receiver_balance_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    # timestamp = Column(DateTime, default=datetime.)
    


