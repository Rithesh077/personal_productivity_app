from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Personal Productivity App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# models


class Feature(BaseModel):
    id: int
    name: str
    description: str


class ScheduleItem(BaseModel):
    id: int
    title: str
    datetime: str  # ISO 8601 string
    note: Optional[str] = None


# in-memory data storage
features: List[Feature] = [
    Feature(id=1, name="Task Management",
            description="Organize and prioritize your tasks effectively."),
    Feature(id=2, name="Note Taking",
            description="Capture your thoughts and ideas in a structured way."),
    Feature(id=3, name="Calendar Integration",
            description="Sync your tasks with your calendar."),
    Feature(id=4, name="Habit Tracking",
            description="Monitor your habits and stay consistent."),
    Feature(id=5, name="Fitness Tracker",
            description="Track your workouts and physical activities."),
    Feature(id=6, name="Schedule Manager",
            description="Manage your schedule and appointments efficiently."),
]

schedule: List[ScheduleItem] = []


# routes
@app.get("/")
def home():
    return {
        "title": "My Personal App",
        "description": "Customizable personal productivity application",
        "features": features,
    }


@app.get("/features/{feature_id}")
def get_feature(feature_id: int):
    feature = next((f for f in features if f.id == feature_id), None)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature


@app.post("/features")
def add_feature(feature: Feature):
    features.append(feature)
    return {"feature": feature}

# schedulue management


@app.get("/schedule")
def get_schedule():
    return {"schedule": schedule}


@app.post("/schedule")
def add_schedule(item: ScheduleItem):
    schedule.append(item)
    return {"schedule_item": item}


@app.delete("/schedule/{item_id}")
def delete_schedule(item_id: int):
    global schedule
    schedule = [s for s in schedule if s.id != item_id]
    return {"message": f"Schedule item {item_id} deleted"}
