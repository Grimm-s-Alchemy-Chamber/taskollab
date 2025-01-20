def check_task_permission(user, task, allow_shared=False):
    if task.creator_id == user.id:
        return True
    if allow_shared and task.category.name == "Shared":
        return True
    return False