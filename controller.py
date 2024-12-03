from models import User  
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

def register_user(username,password):
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        raise ValueError("Email already registered.")
    
    hashed_password = generate_password_hash(password)

    new_user = User(username=username,password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return new_user