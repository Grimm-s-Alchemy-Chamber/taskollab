from datetime import datetime
from app.db import db


# User Model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=True)  # For email/password auth
    firebase_uid = db.Column(db.String(128), unique=True, nullable=True)  # For Firebase auth
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    boards = db.relationship('Board', secondary='user_boards', back_populates='users')
    tasks = db.relationship('Task', back_populates='creator')

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }


# Board Model
class Board(db.Model):
    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', secondary='user_boards', back_populates='boards')
    tasks = db.relationship('Task', back_populates='board')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat()
        }


# Task Model
# Updated Task Model with categories
# Task Model
class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending')  # Example: Pending, In Progress, Done
    due_date = db.Column(db.DateTime, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)  # Updated: Foreign key
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # The user who created the task
    attachments = db.Column(db.Text, nullable=True)  # Stores file URLs or paths as text

    board = db.relationship('Board', back_populates='tasks')
    creator = db.relationship('User', back_populates='tasks')  # User who created the task
    category = db.relationship('Category', back_populates='tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'category': self.category.name if self.category else None,  # Updated: Category name
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'creator_id': self.creator_id,  # The ID of the user who created the task
            'board_id': self.board_id,
            'attachments': self.attachments  # Include attachments field

        }

# Category Model
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    tasks = db.relationship('Task', back_populates='category')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'))
    action = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Association Table: Users <-> Boards
user_boards = db.Table(
    'user_boards',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('board_id', db.Integer, db.ForeignKey('boards.id'), primary_key=True)
)