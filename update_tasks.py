from app import create_app
from app.models import db, Task, Category

app = create_app()

with app.app_context():
    # Find or create a default category
    default_category = Category.query.filter_by(name="Uncategorized").first()
    if not default_category:
        default_category = Category(name="Uncategorized")
        db.session.add(default_category)
        db.session.commit()

    # Update all tasks with NULL category_id to use the default category
    tasks_without_category = Task.query.filter(Task.category_id.is_(None)).all()
    for task in tasks_without_category:
        task.category_id = default_category.id

    db.session.commit()
    print(f"Updated {len(tasks_without_category)} tasks with the default category.")