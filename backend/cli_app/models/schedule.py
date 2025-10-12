class ScheduleItem:
    def __init__(self, task_id, title, scheduled_time):
        self.task_id = task_id
        self.title = title
        self.scheduled_time = scheduled_time

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "title": self.title,
            "scheduled_time": self.scheduled_time
        }
