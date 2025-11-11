from app import app, db, TrainingPlan
from datetime import date

def seed_plan_data():
    """Seeds the TrainingPlan table with initial data."""
    with app.app_context():
        # Check if the table is already seeded
        if TrainingPlan.query.first() is not None:
            print("Training plans already seeded.")
            return

        print("Seeding training plans...")

        initial_plans = [
            TrainingPlan(
                title="Upper Body Strength",
                description="Focus on push-ups, pull-ups, and dips progression. Target: 20 push-ups, 10 pull-ups, 8 dips.",
                start_date=date(2025, 11, 1),
                end_date=date(2025, 11, 30),
                status="completed"
            ),
            TrainingPlan(
                title="Core Development",
                description="Build core strength with planks, leg raises, and Russian twists. Target: 2-minute plank, 20 leg raises.",
                start_date=date(2025, 11, 5),
                end_date=date(2025, 11, 25),
                status="completed"
            ),
            TrainingPlan(
                title="Skill Progression",
                description="Work on handstand balance and muscle-up progression. Daily skill practice for 15 minutes.",
                start_date=date(2025, 11, 10),
                end_date=date(2025, 12, 10),
                status="pending"
            ),
            TrainingPlan(
                title="Flexibility & Mobility",
                description="Improve flexibility with daily stretching routine. Focus on shoulders, hips, and hamstrings.",
                start_date=date(2025, 11, 15),
                end_date=date(2025, 12, 15),
                status="upcoming"
            ),
            TrainingPlan(
                title="Endurance Training",
                description="Build muscular endurance with high-rep circuits. Target: 50 push-ups in 5 minutes.",
                start_date=date(2025, 11, 20),
                end_date=date(2025, 12, 20),
                status="upcoming"
            )
        ]

        db.session.bulk_save_objects(initial_plans)
        db.session.commit()
        print("Training plans seeded successfully.")

if __name__ == '__main__':
    seed_plan_data()
