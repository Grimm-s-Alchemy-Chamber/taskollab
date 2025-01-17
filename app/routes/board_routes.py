# from flask import Blueprint, request, jsonify
# from app.models import Board, db
#
# boards_bp = Blueprint('boards', __name__)
#
#
# @boards_bp.route('/boards', methods=['POST'])
# def create_board():
#     data = request.get_json()
#     name = data.get('name')
#     code = data.get('code')
#     created_by = data.get('created_by')
#
#     if not all([name, code, created_by]):
#         return jsonify({'error': 'Missing required fields'}), 400
#
#     new_board = Board(name=name, code=code, created_by=created_by)
#
#     try:
#         db.session.add(new_board)
#         db.session.commit()
#         return jsonify(new_board.to_dict()), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#
#
# @boards_bp.route('/boards', methods=['GET'])
# def get_boards():
#     boards = Board.query.all()
#     return jsonify([board.to_dict() for board in boards]), 200
#
#
# @boards_bp.route('/boards/join', methods=['POST'])
# def join_board():
#     data = request.get_json()
#     code = data.get('code')
#
#     if not code:
#         return jsonify({'error': 'Code is required'}), 400
#
#     board = Board.query.filter_by(code=code).first()
#
#     if not board:
#         return jsonify({'error': 'Invalid board code'}), 404
#
#     return jsonify({'message': 'Successfully joined board', 'board': board.to_dict()}), 200

from flask import Blueprint, request, jsonify
from app.models import db, Board, User
from app.services.firebase_auth import verify_token
import uuid

boards_bp = Blueprint('boards', __name__)


@boards_bp.route('/boards', methods=['POST'])
def create_board():
    try:
        token = request.headers.get('Authorization').split(" ")[1]
        user_data = verify_token(token)

        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401

        user = User.query.filter_by(firebase_uid=user_data['uid']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()
        name = data.get('name')

        if not name:
            return jsonify({"error": "Board name is required"}), 400

        # Generate a unique code for the board
        board_code = str(uuid.uuid4())[:10]

        new_board = Board(name=name, code=board_code, created_by=user.id)
        new_board.users.append(user)  # Add the creator to the board users
        db.session.add(new_board)
        db.session.commit()

        return jsonify(new_board.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@boards_bp.route('/boards', methods=['GET'])
def get_boards():
    try:
        token = request.headers.get('Authorization').split(" ")[1]
        user_data = verify_token(token)

        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401

        user = User.query.filter_by(firebase_uid=user_data['uid']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        boards = [board.to_dict() for board in user.boards]
        return jsonify(boards), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@boards_bp.route('/boards/<int:board_id>', methods=['GET'])
def get_board(board_id):
    try:
        token = request.headers.get('Authorization').split(" ")[1]
        user_data = verify_token(token)

        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401

        user = User.query.filter_by(firebase_uid=user_data['uid']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        board = Board.query.filter_by(id=board_id).first()

        if not board:
            return jsonify({"error": "Board not found"}), 404

        if user not in board.users:
            return jsonify({"error": "Access denied"}), 403

        return jsonify(board.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@boards_bp.route('/boards/<int:board_id>/add-user', methods=['POST'])
def add_user_to_board(board_id):
    try:
        token = request.headers.get('Authorization').split(" ")[1]
        user_data = verify_token(token)

        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401

        current_user = User.query.filter_by(firebase_uid=user_data['uid']).first()

        if not current_user:
            return jsonify({"error": "User not found"}), 404

        board = Board.query.filter_by(id=board_id).first()

        if not board:
            return jsonify({"error": "Board not found"}), 404

        if board.created_by != current_user.id:
            return jsonify({"error": "Only the creator can add users"}), 403

        data = request.get_json()
        user_email = data.get('email')

        if not user_email:
            return jsonify({"error": "User email is required"}), 400

        user_to_add = User.query.filter_by(email=user_email).first()

        if not user_to_add:
            return jsonify({"error": "User not found"}), 404

        if user_to_add in board.users:
            return jsonify({"error": "User already in board"}), 400

        board.users.append(user_to_add)
        db.session.commit()

        return jsonify({"message": "User added to board"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@boards_bp.route('/boards/<int:board_id>', methods=['DELETE'])
def delete_board(board_id):
    try:
        token = request.headers.get('Authorization').split(" ")[1]
        user_data = verify_token(token)

        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401

        current_user = User.query.filter_by(firebase_uid=user_data['uid']).first()

        if not current_user:
            return jsonify({"error": "User not found"}), 404

        board = Board.query.filter_by(id=board_id).first()

        if not board:
            return jsonify({"error": "Board not found"}), 404

        if board.created_by != current_user.id:
            return jsonify({"error": "Only the creator can delete the board"}), 403

        db.session.delete(board)
        db.session.commit()

        return jsonify({"message": "Board deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@boards_bp.route('/boards/<int:board_id>/users', methods=['GET'])
def get_board_users(board_id):
    try:
        token = request.headers.get('Authorization').split(" ")[1]
        user_data = verify_token(token)

        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401

        current_user = User.query.filter_by(firebase_uid=user_data['uid']).first()

        if not current_user:
            return jsonify({"error": "User not found"}), 404

        board = Board.query.filter_by(id=board_id).first()

        if not board:
            return jsonify({"error": "Board not found"}), 404

        if current_user not in board.users:
            return jsonify({"error": "Access denied"}), 403

        users = [user.to_dict() for user in board.users]
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@boards_bp.route('/boards/join', methods=['POST'])
def join_board():
    try:
        # Step 1: Get the authorization token from the header
        token = request.headers.get('Authorization').split(" ")[1]
        user_data = verify_token(token)

        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401

        # Step 2: Find the user from the Firebase UID
        current_user = User.query.filter_by(firebase_uid=user_data['uid']).first()

        if not current_user:
            return jsonify({"error": "User not found"}), 404

        # Step 3: Get the board code from the request body
        data = request.get_json()
        board_code = data.get('code')

        if not board_code:
            return jsonify({"error": "Board code is required"}), 400

        # Step 4: Find the board by code
        board = Board.query.filter_by(code=board_code).first()

        if not board:
            return jsonify({"error": "Board not found"}), 404

        # Step 5: Check if the user is already in the board
        if current_user in board.users:
            return jsonify({"error": "User is already a member of the board"}), 400

        # Step 6: Add the user to the board
        board.users.append(current_user)
        db.session.commit()

        return jsonify({"message": "Successfully joined the board", "board": board.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
