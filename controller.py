from werkzeug.security import generate_password_hash, check_password_hash
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes,serialization
import hashlib
from datetime import datetime

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def generate_rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537,key_size=1024)
    public_key = private_key.public_key()
    return private_key, public_key

def fix_pem_private_key_format(pem_key):
    # Remove any unnecessary whitespaces and ensure only key data remains
    pem_key = pem_key.strip()
    
    # Split into parts: header, footer, and key data
    header = "-----BEGIN PRIVATE KEY-----"
    footer = "-----END PRIVATE KEY-----"
    key_data = pem_key.replace(header, "").replace(footer, "").replace("\n", "").replace("\r", "")
    
    # Reformat key data into 64-character chunks
    key_data_formatted = "\n".join([key_data[i:i+64] for i in range(0, len(key_data), 64)])
    
    # Reconstruct the PEM key
    fixed_pem_key = f"{header}\n{key_data_formatted}\n{footer}"
    return fixed_pem_key

def fix_pem_public_key_format(pem_key):
    # Remove any unnecessary whitespaces and ensure only key data remains
    pem_key = pem_key.strip()
    
    # Split into parts: header, footer, and key data
    header = "-----BEGIN PUBLIC KEY-----"
    footer = "-----END PUBLIC KEY-----"
    # Ensure the header and footer are removed if present
    # Debug: Check initial input

    # Ensure the header is removed
    if pem_key.startswith(header):
        pem_key = pem_key[len(header):].strip()
    
    # Ensure the footer is removed
    
    pem_key = pem_key[: -len(footer)].strip()
    
    # Debug: Check after removing header/footer
    
    # Remove intermediate newlines in the key data
    key_data = pem_key.replace("\n", "").replace("\r", "")
    
    # Debug: Check cleaned key data
    
    # Reformat key data into 64-character chunks
    key_data_formatted = "\n".join([key_data[i:i+64] for i in range(0, len(key_data), 64)])
    
    # Debug: Check formatted key data
    
    # Reconstruct the PEM key
    fixed_pem_key = f"{header}\n{key_data_formatted}\n{footer}"
    
    # Debug: Check final reconstructed key
    return fixed_pem_key

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

        nonce = generate_nonce()
        commitment = create_commitment(1, nonce)

        response2 = (supabase.table("Bank")
                .insert({"encrypted_balance":1,"user_public_key":public_key_pem,"commitment":commitment,"nonce":nonce})
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

def getBalance_priv(priv_key):
    formated_priv_key = fix_pem_private_key_format(priv_key)
    reconstructed_private_key = serialization.load_pem_private_key(formated_priv_key.encode('utf-8'),password=None)
    reconstructed_public_key = reconstructed_private_key.public_key()

    reconstructed_public_key_pem = reconstructed_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo  # Standard public key format
            ).decode('utf-8')
    
    existing_bank = (
        supabase.table("Bank").select("*").eq("user_public_key",reconstructed_public_key_pem).execute()
    ).data
    if existing_bank:
        return existing_bank[0]
    else:
        raise ValueError("Wrong Key")

def getBalance_pub(pub_key):
    formated_pub_key = fix_pem_public_key_format(pub_key)
    existing_bank = (
        supabase.table("Bank").select("*").eq("user_public_key",formated_pub_key+'\n').execute()
    ).data
    if existing_bank:
        return existing_bank[0]
    else:
        raise ValueError("Wrong Key")
    
def getTransactions(user):
    transactions_sent = (
        supabase.table("Transactions").select("*").eq("sender_balance_id",user['balance_id']).execute()
    ).data
    transactions_received = (
        supabase.table("Transactions").select("*").eq("receiver_balance_id",user['balance_id']).execute()
    ).data
    return [transactions_sent,transactions_received]

def generate_nonce():
    return os.urandom(16).hex()

def create_commitment(balance, nonce):
    # Combine balance and nonce, and hash them
    data = f"{balance}:{nonce}".encode()
    commitment = hashlib.sha256(data).hexdigest()
    return commitment

def generate_proof(balance, transaction_amount, nonce):
    if balance < transaction_amount:
        raise ValueError("Insufficient balance!")
    difference = balance - transaction_amount
    return difference, nonce

def verify_proof(commitment, difference, nonce, transaction_amount):
    # Recreate the original balance
    recreated_balance = difference + transaction_amount
    # Verify the commitment
    data = f"{recreated_balance}:{nonce}".encode()
    expected_commitment = hashlib.sha256(data).hexdigest()
    
    return expected_commitment == commitment and difference >= 0

def doTransaction(sender,receiver,amount):
    balance = sender['encrypted_balance']
    difference, proof_nonce = generate_proof(balance,amount,sender['nonce'])
    is_valid = verify_proof(sender['commitment'],difference,proof_nonce,amount)

    if is_valid:
        sender_new_balance = sender['encrypted_balance']-amount
        sender_new_commit = create_commitment(sender_new_balance,sender["nonce"])
        res = (
            supabase.table("Bank").update({"encrypted_balance":sender_new_balance,"commitment":sender_new_commit}).eq("balance_id",sender["balance_id"]).execute()
        )
        receiver_new_balance = receiver['encrypted_balance']+amount
        receiver_new_commit = create_commitment(receiver_new_balance,receiver["nonce"])
        res = (
            supabase.table("Bank").update({"encrypted_balance":receiver_new_balance,"commitment":receiver_new_commit}).eq("balance_id",receiver["balance_id"]).execute()
        )
        res = (
            supabase.table("Transactions").insert({"timestamp":datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),"sender_balance_id":sender["balance_id"],"receiver_balance_id":receiver["balance_id"],"amount":amount}).execute()
            )
    else:
        raise ValueError("Transaction amount not Valid")

def addBalance(balance_id,amount):
    existing_bank = (
        supabase.table("Bank").select("*").eq("balance_id",balance_id).execute()
    ).data
    receiver_new_balance = existing_bank[0]['encrypted_balance']+amount
    receiver_new_commit = create_commitment(receiver_new_balance,existing_bank[0]["nonce"])
    res = (
        supabase.table("Bank").update({"encrypted_balance":receiver_new_balance,"commitment":receiver_new_commit}).eq("balance_id",balance_id).execute()
    )
    return existing_bank

