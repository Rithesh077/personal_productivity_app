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


@app.route('/features/<int:feature_id>', methods=['GET'])
def get_feature(feature_id):
    feature = next((f for f in features if f['id'] == feature_id), None)
    return jsonify({"feature": feature}) if feature else jsonify({"error": "Feature not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
