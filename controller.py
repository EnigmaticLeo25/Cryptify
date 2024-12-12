from werkzeug.security import generate_password_hash, check_password_hash
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes,serialization

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def generate_rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537,key_size=1024)
    public_key = private_key.public_key()
    return private_key, public_key

def register_user(fullname,email,phone_no,username,password):
    user = (supabase.table("User").select("*")
            .eq("username",username)
            .execute()
            )
    if(user.data):
        raise ValueError("User already registered.")
    else:
        hashed_password = generate_password_hash(password)

        response = (supabase.table("User")
                .insert({"fullname":fullname,"email":email,"phone_no":phone_no,"username":username,"password":hashed_password})
                    .execute()
                    ) 
        private_key, public_key = generate_rsa_keys()

        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,  # Standard private key format
            encryption_algorithm=serialization.NoEncryption()  # No password protection
            ).decode('utf-8')

        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo  # Standard public key format
            ).decode('utf-8')

        response2 = (supabase.table("Bank")
                .insert({"encrypted_balance":1,"user_public_key":public_key_pem})
                    .execute()
                    )
        return [public_key_pem,private_key_pem]

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
        supabase.table("Bank").select("*").eq("balance_id",priv_key).execute()
    ).data
    if existing_bank:
        return existing_bank[0]["encrypted_balance"]
    else:
        print(existing_bank)
        return -1
    
def getTransactions(balance_id):
    transactions = (
        supabase.table("Transactions").select("*").eq("user_id",balance_id).execute()
    )
    count = transactions.count
    transactions = transactions.data
    return [count,transactions]
    
def getAccount(accountName):
    account = (
        supabase.table("Users").select("*").eq("username",accountName).execute()
    ).data
    if account:
        return account
    else:
        return -1