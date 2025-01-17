from flask import request, jsonify
from functools import wraps
from app.services.firebase_auth import verify_token


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization header is required"}), 401

        id_token = auth_header.split("Bearer ")[-1]
        decoded_token = verify_token(id_token)
        if not decoded_token:
            return jsonify({"error": "Invalid or expired token"}), 401

        request.user = decoded_token
        return f(*args, **kwargs)

    return decorated_function
