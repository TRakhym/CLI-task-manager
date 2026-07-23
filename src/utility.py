from .models import Priority

def get_priority(type: str) -> Priority | None:
    match type:
        case "low":
            return Priority.Low
        case "medium":
            return Priority.Medium
        case "high":
            return Priority.High
        case _:
            return None