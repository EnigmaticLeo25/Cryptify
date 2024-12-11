from models import User,Bank
from database import db
from werkzeug.security import generate_password_hash, check_password_hash
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def register_user(fullname,email,phone_no,username,password):
    user = (supabase.table("User").select("*")
            .eq("username",username)
            .execute()
            )
    if(user):
        raise ValueError("User already registered.")
    
    hashed_password = generate_password_hash(password)

    response = (supabase.table("User")
                .insert({"fullname":fullname,"email":email,"phone_no":phone_no,"username":username,"password":hashed_password})
                .execute()
                )

    return response

def check_user(email,password):
    existing_user = (
        supabase.table("User").select("*").eq("email",email).execute()
    )
    
    if existing_user.data and check_password_hash(existing_user.data[0]["password"], password):
        return_details = [True,existing_user.data]    
        return return_details    
    else:
        return_details = [False,existing_user.data]
        return return_details

def getBalance(priv_key):
    existing_bank = (
        supabase.table("Bank").select("*").eq("user_private_key",priv_key).execute()
    )
    if existing_bank:
        return existing_bank.encrypted_balance
    else:
        return -1
    
def getTransactions(balance_id):
    transactions = (
        supabase.table("Transactions").select("*").eq("user_id",balance_id).execute()
    )
    count = transactions.count
    transactions = transactions.data
    return [count,transactions]
    
