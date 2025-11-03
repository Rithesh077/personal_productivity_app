from datetime import datetime
from models.task import Task
from models.schedule import ScheduleItem
from utils.storage import load_data, save_data
TASK_FILE = "data/tasks.json"
SCHEDULE_FILE = "data/schedule.json"


def add_task():
    title = input("Enter task title: ")
    try:
        priority = int(input("Enter priority (1-10): "))
    except ValueError:
        print("Invalid input for priority. Please enter a number.")
        return

    due_time = input("Enter due time (YYYY-MM-DD HH:MM): ")

    if priority < 1 or priority > 10:
        print("Priority must be between 1 and 10.")
        return
    try:
        datetime.strptime(due_time, "%Y-%m-%d %H:%M")
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD HH:MM")
        return

    task = Task(title, priority, due_time)
    tasks = load_data(TASK_FILE)
    tasks.append(task.to_dict())
    save_data(TASK_FILE, tasks)
    print("Task added successfully!")


def view_tasks():
    tasks = load_data(TASK_FILE)
    if not tasks:
        print("No tasks found.")
        return
    print("\nAll Tasks:")
    for t in tasks:
        print(
            f"[{t['id']}] {t['title']} | Priority: {t['priority']} | Due: {t['due_time']} | Status: {t['status']}")


def sort_and_schedule():
    tasks = load_data(TASK_FILE)
    if not tasks:
        print("No tasks to schedule.")
        return

    # sort by priority (desc) and then due_time
    tasks.sort(key=lambda x: (-x["priority"], x["due_time"]))
    save_data(TASK_FILE, tasks)

    schedule = []
    for t in tasks:
        item = ScheduleItem(t["id"], t["title"], t["due_time"])
        schedule.append(item.to_dict())

    save_data(SCHEDULE_FILE, schedule)
    print("\nSchedule updated based on priority.")
    view_schedule()


def view_schedule():
    schedule = load_data(SCHEDULE_FILE)
    if not schedule:
        print("No scheduled items found.")
        return
    print("\nScheduled Tasks:")
    for s in schedule:
        print(f"→ {s['title']} at {s['scheduled_time']}")


def mark_task_done():
    tasks = load_data(TASK_FILE)

    try:
        task_id = int(input("Enter task ID to mark as done: "))
    except ValueError:
        print("Invalid ID. Please enter a number.")
        return

    for t in tasks:
        if t["id"] == task_id:
            t["status"] = "Completed"
            save_data(TASK_FILE, tasks)
            print("Task marked as completed.")
            return
    print("Task not found.")


def delete_task():
    tasks = load_data(TASK_FILE)

    try:
        task_id = int(input("Enter task ID to delete: "))
    except ValueError:
        print("Invalid ID. Please enter a number.")
        return

    tasks = [t for t in tasks if t["id"] != task_id]
    save_data(TASK_FILE, tasks)
    print("🗑 Task deleted.")


def main():
    while True:
        print("""
========= PERSONAL PRODUCTIVITY APP=========
1. Add Task
2. View All Tasks
3. Sort & Auto-Schedule Tasks
4. View Schedule
5. Mark Task as Done
6. Delete Task
7. Exit
========================================================
""")
        choice = input("Enter choice: ")

        if choice == "1":
            add_task()
        elif choice == "2":
            view_tasks()
        elif choice == "3":
            sort_and_schedule()
        elif choice == "4":
            view_schedule()
        elif choice == "5":
            mark_task_done()
        elif choice == "6":
            delete_task()
        elif choice == "7":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
