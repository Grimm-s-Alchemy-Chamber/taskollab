# # from flask import Blueprint, request, jsonify
# # from app.models import Task, db
# # from app import socketio
# #
# #
# # task_bp = Blueprint('tasks', __name__)
# #
# # @task_bp.route('/', methods=['POST'])
# # def create_task():
# #     data = request.json
# #     new_task = Task(name=data['name'], board_id=data['board_id'])
# #     db.session.add(new_task)
# #     db.session.commit()
# #     return jsonify({'message': 'Task created', 'task_id': new_task.id})
# #
# #
# # @task_bp.route('/<task_id>/complete', methods=['PUT'])
# # def complete_task(task_id):
# #     task = Task.query.get(task_id)
# #     task.completed = True
# #     db.session.commit()
# #     socketio.emit('task_updated', {'task_id': task.id})
# #     return jsonify({'message': 'Task marked as complete'})
#
# from flask import Blueprint, request, jsonify
# from app.models import db, Task
#
# task_bp = Blueprint("task", __name__)
#
#
# @task_bp.route("/api/task", methods=["POST"])
# def create_task():
#     data = request.json
#     title = data.get("title")
#     board_id = data.get("board_id")
#     if not title or not board_id:
#         return jsonify({"error": "Title and board_id are required"}), 400
#
#     task = Task(title=title, board_id=board_id)
#     db.session.add(task)
#     db.session.commit()
#     return jsonify({"message": "Task created", "task": {"id": task.id, "title": task.title}}), 201


from flask import Blueprint, request, jsonify
from app.models import db, Task, Board, User
from app.services.firebase_auth import verify_token

task_bp = Blueprint('task_bp', __name__)


# Create a Task
@task_bp.route('/tasks', methods=['POST'])
def create_task():
    try:
        token = request.headers.get('Authorization').split(" ")[1]
        user_data = verify_token(token)

        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401

        user = User.query.filter_by(firebase_uid=user_data['uid']).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()
        title = data.get('title')
        category = data.get('category')
        board_id = data.get('board_id')
        assigned_user_id = data.get('assigned_user_id')

        if not all([title, category, board_id]):
            return jsonify({"error": "Missing required fields"}), 400

        # Ensure board exists and user is a member of it
        board = Board.query.filter_by(id=board_id).first()
        if not board:
            return jsonify({"error": "Board not found"}), 404

        if user not in board.users:
            return jsonify({"error": "You are not part of this board"}), 403

        new_task = Task(
            title=title,
            category=category,
            board_id=board_id,
            assigned_user_id=assigned_user_id if assigned_user_id else user.id
        )

        db.session.add(new_task)
        db.session.commit()

        return jsonify(new_task.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get All Tasks
@task_bp.route('/tasks/<int:board_id>', methods=['GET'])
def get_tasks(board_id):
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
            return jsonify({"error": "You are not part of this board"}), 403

        tasks = Task.query.filter_by(board_id=board_id).all()
        tasks_data = [task.to_dict() for task in tasks]
        return jsonify(tasks_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get Task by ID
@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    try:
        token = request.headers.get('Authorization').split(" ")[1]
        user_data = verify_token(token)

        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401

        user = User.query.filter_by(firebase_uid=user_data['uid']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        task = Task.query.filter_by(id=task_id).first()

        if not task:
            return jsonify({"error": "Task not found"}), 404

        return jsonify(task.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Update Task (Status, Assigned User, Due Date, etc.)
@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        token = request.headers.get('Authorization').split(" ")[1]
        user_data = verify_token(token)

        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401

        user = User.query.filter_by(firebase_uid=user_data['uid']).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return jsonify({"error": "Task not found"}), 404

        if task.assigned_user_id != user.id:
            return jsonify({"error": "You are not assigned to this task"}), 403

        data = request.get_json()
        task.title = data.get('title', task.title)
        task.category = data.get('category', task.category)
        task.due_date = data.get('due_date', task.due_date)
        task.assigned_user_id = data.get('assigned_user_id', task.assigned_user_id)

        db.session.commit()
        return jsonify(task.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Delete Task
@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        token = request.headers.get('Authorization').split(" ")[1]
        user_data = verify_token(token)

        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401

        user = User.query.filter_by(firebase_uid=user_data['uid']).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return jsonify({"error": "Task not found"}), 404

        if task.assigned_user_id != user.id:
            return jsonify({"error": "You are not assigned to this task"}), 403

        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


