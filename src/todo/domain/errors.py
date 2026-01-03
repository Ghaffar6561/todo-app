"""Domain-level errors."""


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class TaskNotFoundError(Exception):
    """Raised when a task with the given ID is not found."""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        self.message = f"Task with id {task_id} not found"
        super().__init__(self.message)
