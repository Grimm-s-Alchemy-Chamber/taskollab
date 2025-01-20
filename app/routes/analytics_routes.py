# In app/routes/analytics_routes.py
from flask import jsonify

from app import db
from app.models import Task, Category


@analytics_bp.route('/board/<int:board_id>')
def get_board_analytics(board_id):
    # Completion rates
    tasks = Task.query.filter_by(board_id=board_id).all()
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == 'Done'])

    # Category distribution
    category_stats = db.session.query(
        Category.name,
        db.func.count(Task.id)
    ).join(Task).filter(Task.board_id == board_id).group_by(Category.name).all()

    return jsonify({
        'completion_rate': completed_tasks / total_tasks if total_tasks else 0,
        'category_distribution': dict(category_stats)
    })