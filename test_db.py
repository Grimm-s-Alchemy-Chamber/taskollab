from app import create_app
from app.models import db, User

app = create_app()

with app.app_context():
    # Add a user
    new_user = User(name="Test User", email="test2@example.com", password="password123")
    db.session.add(new_user)
    db.session.commit()
    print(f"User added: {new_user.to_dict()}")

    # Fetch users
    users = User.query.all()
    print(f"All users: {[user.to_dict() for user in users]}")
