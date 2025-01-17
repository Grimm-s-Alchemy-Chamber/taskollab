# from flask import Blueprint, request, jsonify
# from app.models import Task, db
# from app import socketio
#
#
# task_bp = Blueprint('tasks', __name__)
#
# @task_bp.route('/', methods=['POST'])
# def create_task():
#     data = request.json
#     new_task = Task(name=data['name'], board_id=data['board_id'])
#     db.session.add(new_task)
#     db.session.commit()
#     return jsonify({'message': 'Task created', 'task_id': new_task.id})
#
#
# @task_bp.route('/<task_id>/complete', methods=['PUT'])
# def complete_task(task_id):
#     task = Task.query.get(task_id)
#     task.completed = True
#     db.session.commit()
#     socketio.emit('task_updated', {'task_id': task.id})
#     return jsonify({'message': 'Task marked as complete'})

from flask import Blueprint, request, jsonify
from app.models import db, Task

task_bp = Blueprint("task", __name__)


@task_bp.route("/api/task", methods=["POST"])
def create_task():
    data = request.json
    title = data.get("title")
    board_id = data.get("board_id")
    if not title or not board_id:
        return jsonify({"error": "Title and board_id are required"}), 400

    task = Task(title=title, board_id=board_id)
    db.session.add(task)
    db.session.commit()
    return jsonify({"message": "Task created", "task": {"id": task.id, "title": task.title}}), 201
