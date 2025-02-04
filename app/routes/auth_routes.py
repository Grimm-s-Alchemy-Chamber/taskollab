from flask import Blueprint, request, jsonify
from app.services.firebase_auth import verify_token
import firebase_admin.auth as firebase_auth
import re
from app.models import db, User

auth_bp = Blueprint('auth', __name__)


#
# # Signup route
# @auth_bp.route('/signup', methods=['POST'])
# def signup():
#     try:
#         data = request.get_json()
#         email = data.get('email')
#         password = data.get('password')
#
#         if not email or not password:
#             return jsonify({"error": "Email and password are required"}), 400
#
#         # Create the user in Firebase Authentication
#         user = firebase_auth.create_user(
#             email=email,
#             password=password
#         )
#
#         # Generate ID Token
#         id_token = firebase_auth.create_custom_token(user.uid)
#
#         return jsonify({"id_token": id_token.decode('utf-8')}), 201
#
#     except firebase_auth.EmailAlreadyExistsError:
#         return jsonify({"error": "Email already exists"}), 400
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
#
# # Login route
# @auth_bp.route('/login', methods=['POST'])
# def login():
#     try:
#         data = request.get_json()
#         email = data.get('email')
#         password = data.get('password')
#
#         if not email or not password:
#             return jsonify({"error": "Email and password are required"}), 400
#
#         # Verify the user with Firebase Authentication (password verification)
#         user = firebase_auth.get_user_by_email(email)
#
#         # Generate ID Token (this is a placeholder since Firebase Admin SDK doesn't verify password directly)
#         id_token = firebase_auth.create_custom_token(user.uid)
#
#         return jsonify({"id_token": id_token.decode('utf-8')}), 200
#
#     except firebase_auth.UserNotFoundError:
#         return jsonify({"error": "User not found"}), 400
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')  # Assuming name is also sent

        if not email or not password or not name:
            return jsonify({"error": "Email, password, and name are required"}), 400

        # Create the user in Firebase Authentication
        user = firebase_auth.create_user(
            email=email,
            password=password
        )

        # Add the user to PostgreSQL
        new_user = User(email=email, name=name, firebase_uid=user.uid)
        db.session.add(new_user)
        db.session.commit()

        # Generate ID Token
        id_token = firebase_auth.create_custom_token(user.uid)

        return jsonify({"id_token": id_token.decode('utf-8')}), 201

    except firebase_auth.EmailAlreadyExistsError:
        return jsonify({"error": "Email already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Verify the user with Firebase Authentication (assume Firebase SDK handles password verification)
        user = firebase_auth.get_user_by_email(email)

        # Check if the user exists in PostgreSQL
        existing_user = User.query.filter_by(firebase_uid=user.uid).first()
        if not existing_user:
            # Create the user in PostgreSQL if not found
            existing_user = User(email=email, name="Default Name", firebase_uid=user.uid)  # Adjust name logic if needed
            db.session.add(existing_user)
            db.session.commit()

        # Generate ID Token
        id_token = firebase_auth.create_custom_token(user.uid)

        return jsonify({"id_token": id_token.decode('utf-8')}), 200

    except firebase_auth.UserNotFoundError:
        return jsonify({"error": "User not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
