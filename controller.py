from models import User  
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

def register_user(fullname,email,phone_no,username,password):
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise ValueError("Email already registered.")
    
    hashed_password = generate_password_hash(password)

    new_user = User(fullname=fullname,email=email,phone_no=phone_no,username=username,password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return new_user

def check_user(email,password):
    existing_user = User.query.filter_by(email=email).first()
    if existing_user and check_password_hash(existing_user.password, password):
        return_details = [True,existing_user]    
        return return_details    
    else:
        return_details = [False,existing_user]
        return return_details