from enum import Enum
import shutil
import textwrap

from typing import Callable
from functools import wraps

class Priority(Enum):
    High = 3
    Medium = 2
    Low = 1

class Task:

    def __init__(self, 
            title: str, 
            desc: str, 
            priority: Priority, 
            deadline: str, 
            tags: list[str]):
        self.title = title
        self.desc = desc
        self.priority = priority
        self.deadline = deadline
        self.tags = tags

class TaskFormatter:

    terminal_columns, _ = shutil.get_terminal_size(fallback=(80, 24))

    def __init__(self, tasks: list[Task]):
        self.tasks = tasks
        self.set_width_of_text(50)
        self.adaptive = False
        self.adaptive_line_items = 4

    @staticmethod
    def __set_limit_width(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            args_list = list(args)
            if (TaskFormatter.terminal_columns) < args_list[1]:
                args_list[1] = TaskFormatter.terminal_columns
            return func(*args_list, **kwargs)
        return wrapper

    @__set_limit_width
    def set_width_of_text(self, width: int):
        self.width_of_text = width
        self.half_of_width = int(width/2)
        return self
    
    def adapt_terminal_width(self, items: int = 4):
        self.adaptive = True
        self.adaptive_line_items = items
        return self
    
    def __format_fixed_text(self, task: Task) -> str:

        desc_lines = textwrap.wrap(task.desc, width=self.width_of_text)
        if not desc_lines:
            desc_lines = [""]
        formatted_desc = "\n".join(
            [line.ljust(self.width_of_text) for line in desc_lines]
        )

        formatted_priority = f"Priority: {task.priority.name}"
        formatted_deadline = f"Deadline: {task.deadline}"
        prio_dead_line = f"{formatted_priority:<{self.half_of_width-1}}{formatted_deadline:<{self.half_of_width-1}}".ljust(
            self.width_of_text
        )

        tag_lines = textwrap.wrap(
            "Tags: " + (", ".join(task.tags)), width=self.width_of_text
        )
        if not tag_lines:
            tag_lines = [""]
        formatted_tags = "\n".join(
            [line.ljust(self.width_of_text) for line in tag_lines]
        )

        title = "'"+task.title+"'"
        title_line = f"{title:^{self.width_of_text}}"
        border = "-" * self.width_of_text

        return (
            f"{border}\n"
            f"{title_line}\n"
            f"{border}\n"
            f"{formatted_desc}\n"
            f"{border}\n"
            f"{prio_dead_line}\n"
            f"{border}\n"
            f"{formatted_tags}\n"
            f"{border}"
        )


    def __format_adapt_text(self, tasks: list[Task]) -> str:
        rendered_tasks = [
            self.__format_fixed_text(t).splitlines() for t in tasks
        ]

        max_lines = max(len(lines) for lines in rendered_tasks)

        for lines in rendered_tasks:
            while len(lines) < max_lines:
                lines.append(" " * self.width_of_text)

        combined_lines = []
        for line_idx in range(max_lines):
            row_str = "|".join(
                f"{lines[line_idx]:<{self.width_of_text}}"
                for lines in rendered_tasks
            )
            combined_lines.append(row_str)

        return "\n".join(combined_lines)

    def format(self):
        if self.adaptive:
            total_columns = TaskFormatter.terminal_columns
            available_width_for_cards = total_columns - (
                self.adaptive_line_items - 1
            )
            col_width = int(available_width_for_cards / self.adaptive_line_items)

            self.set_width_of_text(col_width)

            return "\n".join(
                [
                    self.__format_adapt_text(
                        self.tasks[i : i + self.adaptive_line_items]
                    )
                    for i in range(0, len(self.tasks), self.adaptive_line_items)
                ]
            )
        else:
            return "\n".join(
                [self.__format_fixed_text(task) for task in self.tasks]
            )