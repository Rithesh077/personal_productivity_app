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
}, {
    "id": 6,
    "name": "Schedule Manager",
    "description": "Manage your schedule and appointments efficiently."
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


@app.route('/features', methods=['POST'])
def add_feature():
    new_feature = request.get_json()
    if not new_feature or not all(k in new_feature for k in ("name", "description")):
        return jsonify({"error": "Invalid feature data"}), 400
    new_id = max(f["id"] for f in features) + 1 if features else 1
    feature = {
        "id": new_id,
        "name": new_feature["name"],
        "description": new_feature["description"]
    }
    features.append(feature)
    return jsonify({"feature": feature}), 201


if __name__ == '__main__':
    app.run(debug=True)
