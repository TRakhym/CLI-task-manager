from enum import Enum

import argparse
import sqlite3

from src.models import Priority, Task, TaskFormatter
from src import db
from src.utility import get_priority

class Action(Enum):
    ADD    = "add"
    LIST   = "list"
    EDIT   = "edit"
    DELETE = "delete"

def add_task(title, desc, priority, deadline, tags):
    task_priority = get_priority(priority)

    new_task = Task(
        title=title,
        desc=desc,
        priority=task_priority,
        deadline=deadline,
        tags=tags
    )
    db.insert_task(new_task)
    print(f"Task '{new_task.title}' successfully created!")

def list_tasks(show_all):
    tasks = db.get_all_tasks()
    
    text = TaskFormatter(tasks)\
        .adapt_terminal_width(4)\
        .format()

    print(text)

def edit_task(old_title, title, desc, priority, deadline, tags):
    task_priority = get_priority(priority)
    
    new_task = Task(
        title=title,
        desc=desc,
        priority=task_priority,
        deadline=deadline,
        tags=tags
    )
    db.update_task_by_title(old_title, new_task)

def delete_task(title: str):
    db.delete_by_title(title)

def main():
    parser = argparse.ArgumentParser(description="CLI-task-manager")
    
    subparsers = parser.add_subparsers(dest="action", required=True, help="Select option")

    add_parser = subparsers.add_parser(Action.ADD.value, help="Add new task")
    add_parser.add_argument("title", type=str, help="Title of task")
    add_parser.add_argument("--desc", type=str, default="", help="Description")
    add_parser.add_argument(
        "--priority", 
        type=str, 
        choices=["low", "medium", "high"], 
        default=Priority.Medium.name.lower(), 
        help="Priority (low, medium, high)"
    )
    add_parser.add_argument("--deadline", type=str, default="", help="Deadline (--deadline YYYY-MM-DD)")
    add_parser.add_argument("--tags", nargs="*", default=[], help="Tags separated by spaces (--tags work urgent)")

    list_parser = subparsers.add_parser(Action.LIST.value, help="Show tasks")
    list_parser.add_argument("--all", action="store_true", help="Show all of tasks")

    edit_parser = subparsers.add_parser(Action.EDIT.value, help="Edit task")

    edit_parser.add_argument("old_title", type=str, help="Title of task")

    edit_parser.add_argument("--title", type=str, help="New title")
    edit_parser.add_argument("--desc", type=str, help="New description")
    edit_parser.add_argument(
        "--priority", 
        type=str, 
        choices=["low", "medium", "high"], 
        help="New Priority (low, medium, high)"
    )
    edit_parser.add_argument("--deadline", type=str, help="New Deadline")
    edit_parser.add_argument("--tags", nargs="*", help="New tags separated by spaces")

    delete_parser = subparsers.add_parser(Action.DELETE.value, help="Delete task by title")
    delete_parser.add_argument("title", type=str, help="Title for delete")

    args = parser.parse_args()

    db.init_database()

    match args.action:
        case Action.ADD.value:
            add_task(args.title, args.desc, args.priority, args.deadline, args.tags)

        case Action.LIST.value:
            list_tasks(show_all=args.all)

        case Action.EDIT.value:
            edit_task(args.old_title, args.title, args.desc, args.priority, args.deadline, args.tags)

        case Action.DELETE.value:
            delete_task(args.title)

    db.close_database()

if __name__ == "__main__":
    main()