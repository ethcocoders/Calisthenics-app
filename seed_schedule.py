from app import app, db, ScheduleItem, StickyNote
from datetime import time

# --- ScheduleItem Data ---
initial_schedule_items = [
    ScheduleItem(title="Upper Body", details="Push-ups, Pull-ups, Dips", day_of_week="Monday", time=time(18, 30), category="workout", status="completed"),
    ScheduleItem(title="Mobility", details="Stretching & Recovery", day_of_week="Monday", time=time(20, 0), category="rest", status="completed"),
    ScheduleItem(title="Leg Day", details="Squats, Lunges, Calf Raises", day_of_week="Tuesday", time=time(19, 0), category="workout", status="completed"),
    ScheduleItem(title="Core Focus", details="Planks, Leg Raises", day_of_week="Wednesday", time=time(18, 45), category="workout", status="scheduled"),
    ScheduleItem(title="Skill Work", details="Handstand Practice", day_of_week="Wednesday", time=time(20, 30), category="planned", status="scheduled"),
    ScheduleItem(title="Active Rest", details="Light Walking", day_of_week="Thursday", time=time(0, 0), category="rest", status="scheduled"),
    ScheduleItem(title="Full Body", details="Circuit Training", day_of_week="Friday", time=time(19, 15), category="workout", status="scheduled"),
    ScheduleItem(title="Outdoor Workout", details="Park Calisthenics", day_of_week="Saturday", time=time(9, 0), category="workout", status="scheduled"),
    ScheduleItem(title="Recovery", details="Foam Rolling", day_of_week="Saturday", time=time(15, 0), category="rest", status="scheduled"),
    ScheduleItem(title="Complete Rest", details="Mental Recovery", day_of_week="Sunday", time=time(0, 0), category="rest", status="scheduled"),
]

# --- StickyNote Data ---
initial_sticky_notes = [
    StickyNote(title="Form Check", content="Record push-up form this week", color="yellow"),
    StickyNote(title="Progress Goal", content="+5 pull-ups by end of month", color="orange"),
    StickyNote(title="Rest Priority", content="Don't skip Sunday rest day!", color="pink"),
    StickyNote(title="Meal Prep", content="Prepare post-workout meals", color="green"),
]

def seed_schedule_data():
    """Seeds only the ScheduleItem and StickyNote tables."""
    with app.app_context():
        # Seed ScheduleItems
        if ScheduleItem.query.first() is None:
            print("Seeding schedule items...")
            db.session.bulk_save_objects(initial_schedule_items)
            db.session.commit()
            print("Schedule items seeded successfully.")
        else:
            print("Schedule items already seeded.")

        # Seed StickyNotes
        if StickyNote.query.first() is None:
            print("Seeding sticky notes...")
            db.session.bulk_save_objects(initial_sticky_notes)
            db.session.commit()
            print("Sticky notes seeded successfully.")
        else:
            print("Sticky notes already seeded.")

if __name__ == '__main__':
    seed_schedule_data()
