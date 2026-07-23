import sqlite3

from .models import Priority, Task

_con: sqlite3.Connection | None = None
_cursor: sqlite3.Cursor | None = None

def init_database():
    global _con, _cursor
    _con = sqlite3.connect("database.db")
    _cursor = _con.cursor()

    _create_table()

def _create_table():
    assert _cursor is not None, "Database wasn't been initialized"
    _cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT CHECK(priority IN ('High', 'Medium', 'Low')),
            deadline TEXT,
            tags TEXT
        )
        """)

def insert_task(task: Task):
    assert _cursor is not None and _con is not None, "Database wasn't initialized"
    tags_str = ",".join(task.tags) if isinstance(task.tags, list) else task.tags
    _cursor.execute(
        """
        INSERT INTO tasks (title, description, priority, deadline, tags)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            task.title,
            task.desc,
            task.priority.name,
            task.deadline,
            tags_str,
        ),
    )
    _con.commit()

def update_task_by_title(old_title: str, task: Task):
    assert _cursor is not None and _con is not None, "Database wasn't initialized"

    fields_to_update = {}
    
    if task.title is not None:
        fields_to_update["title"] = task.title
    if task.desc is not None:
        fields_to_update["description"] = task.desc
    if task.priority is not None:
        fields_to_update["priority"] = task.priority.name
    if task.deadline is not None:
        fields_to_update["deadline"] = task.deadline
    if task.tags is not None:
        fields_to_update["tags"] = ",".join(task.tags) if isinstance(task.tags, list) else task.tags

    if not fields_to_update:
        return

    set_clause = ", ".join([f"{col} = ?" for col in fields_to_update.keys()])

    values = list(fields_to_update.values()) + [old_title]

    _cursor.execute(f"UPDATE tasks SET {set_clause} WHERE title = ?", values)
    _con.commit()
    
def get_all_tasks() -> list[Task]:
    assert _cursor is not None and _con is not None, "Database wasn't initialized"
    _cursor.execute("SELECT rowid, * FROM tasks")
    rows = _cursor.fetchall()

    tasks = []
    for row_id, title, desc, priority_str, deadline, tags_str in rows:
        tags_list = tags_str.split(",") if tags_str else []

        priority_enum = (
            Priority[priority_str]
            if isinstance(priority_str, str)
            else priority_str
        )

        tasks.append(
            Task(
                title=title,
                desc=desc,
                priority=priority_enum,
                deadline=deadline,
                tags=tags_list,
            )
        )

    return tasks

def delete_by_title(title: str):
    assert _cursor is not None and _con is not None, "Database wasn't initialized"
    _cursor.execute(
        """
        DELETE FROM tasks WHERE title = ?
        """,
        [title],
    )
    _con.commit()

def close_database():
    global _con, _cursor
    if _con:
        _con.close()
        _con = None
        _cursor = None
