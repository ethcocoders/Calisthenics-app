from app import app, db, Workout, Event
from datetime import datetime

# --- Workout Data (unchanged) ---
pushups_instructions = """
- Start in plank position with hands shoulder-width apart
- Keep your body in a straight line from head to heels
- Lower your body until your chest nearly touches the floor
- Push back up to starting position
- Keep elbows at 45-degree angle to body
"""
pullups_instructions = "..." # (instructions omitted for brevity)
muscleups_instructions = "..."
handstand_instructions = "..."
squats_instructions = "..."
lunges_instructions = "..."
initial_workouts = [
    Workout(name="Push-ups", difficulty="Beginner", sets=3, reps="15", rest="2m", instructions=pushups_instructions),
    Workout(name="Pull-ups", difficulty="Intermediate", sets=4, reps="8", rest="3m", instructions=pullups_instructions),
    Workout(name="Muscle-ups", difficulty="Advanced", sets=3, reps="5", rest="4m", instructions=muscleups_instructions),
    Workout(name="Handstand Push-ups", difficulty="Advanced", sets=3, reps="6", rest="3m", instructions=handstand_instructions),
    Workout(name="Squats", difficulty="Beginner", sets=4, reps="20", rest="1.5m", instructions=squats_instructions),
    Workout(name="Lunges", difficulty="Intermediate", sets=3, reps="12/Leg", rest="2m", instructions=lunges_instructions)
]

# --- NEW: Event Data ---
initial_events = [
    Event(title="Upper Body Blast", category="workout", start_time=datetime(2025, 11, 8, 19, 0)),
    Event(title="Active Rest Day", category="rest", start_time=datetime(2025, 11, 9, 0, 0)),
    Event(title="Leg Day", category="workout", start_time=datetime(2025, 11, 10, 19, 0)),
    Event(title="Core & Mobility", category="workout", start_time=datetime(2025, 11, 12, 19, 0))
]


def seed_data():
    with app.app_context():
        # Seed Workouts
        if Workout.query.first() is None:
            print("Seeding workouts...")
            db.session.bulk_save_objects(initial_workouts)
            db.session.commit()
            print("Workouts seeded successfully.")
        else:
            print("Workouts already seeded.")

        # Seed Events
        if Event.query.first() is None:
            print("Seeding events...")
            db.session.bulk_save_objects(initial_events)
            db.session.commit()
            print("Events seeded successfully.")
        else:
            print("Events already seeded.")

if __name__ == '__main__':
    seed_data()
