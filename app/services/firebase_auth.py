import os

import dotenv
import firebase_admin
from dotenv import load_dotenv
from firebase_admin import auth, credentials

load_dotenv()
firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS")

cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred)

from firebase_admin import auth


def verify_token(token):
    try:
        # Remove the 'Bearer ' prefix and verify the token
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None
