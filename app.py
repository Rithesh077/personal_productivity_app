import flask
from flask import Flask, request, jsonify
app = Flask(__name__)
features = [{
    "id": 1,
    "name": "Task Management",
    "description": "Organize and prioritize your tasks effectively."
}, {
    "id": 2,
    "name": "Note Taking",
    "description": "Capture your thoughts and ideas in a structured way."
}, {
    "id": 3,
    "name": "Calendar Integration",
    "description": "Sync your tasks with your calendar for better planning."
}, {
    "id": 4,
    "name": "Habit Tracking",
    "description": "Monitor your habits and stay consistent."

}, {
    "id": 5,
    "name": "Fitness Tracker",
    "description": "Track your workouts and physical activities."
}]


@app.route('/')
def home():
    data = {"title": "My Personal App",
            "description": "This is a customizable personal productivity application",
            "features": features}
    return jsonify(data)


@app.route('/features/', methods=['GET'])
def get_features():
    return jsonify({"features": features})


if __name__ == '__main__':
    app.run(debug=True)
