from datetime import datetime

class Task:
    def __init__(self, title, priority, due_time):
        self.id = int(datetime.now().timestamp())
        self.title = title
        self.priority = priority
        self.due_time = due_time
        self.status = "Pending"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "due_time": self.due_time,
            "status": self.status
        }
