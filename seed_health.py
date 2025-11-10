from app import app, db, UserProfile, HealthRecord, HealthPlanItem
from datetime import date

def seed_health_data():
    """Seeds the UserProfile, HealthRecord, and HealthPlanItem tables."""
    with app.app_context():
        # --- 1. Seed User Profile (Singleton) ---
        if UserProfile.query.first() is None:
            print("Seeding user profile...")
            # We assume a single user for now.
            user_profile = UserProfile(height=183, age=28, gender='Male')
            db.session.add(user_profile)
            db.session.commit()
            print("User profile seeded successfully.")
        else:
            print("User profile already seeded.")

        # --- 2. Seed Health Records ---
        if HealthRecord.query.first() is None:
            print("Seeding health records...")
            initial_health_records = [
                HealthRecord(date=date(2025, 11, 1), weight=75.2, body_fat=14.2, notes='Good energy, completed full workout'),
                HealthRecord(date=date(2025, 10, 15), weight=75.8, body_fat=14.5, notes='Slightly tired, reduced intensity'),
                HealthRecord(date=date(2025, 10, 1), weight=76.1, body_fat=14.8, notes='Excellent performance, PR on pull-ups'),
                HealthRecord(date=date(2025, 9, 15), weight=76.5, body_fat=15.1, notes='Recovery day, light mobility work'),
                HealthRecord(date=date(2025, 9, 1), weight=77.0, body_fat=15.5, notes='Started new program, feeling good'),
                HealthRecord(date=date(2025, 8, 15), weight=77.5, body_fat=15.8, notes='Feeling strong'),
            ]
            db.session.bulk_save_objects(initial_health_records)
            db.session.commit()
            print("Health records seeded successfully.")
        else:
            print("Health records already seeded.")

        # --- 3. Seed Health Plan Items ---
        if HealthPlanItem.query.first() is None:
            print("Seeding health plan items...")
            initial_health_plan_items = [
                HealthPlanItem(title='Weekly Weight Check', description='Measure weight every Monday morning', status='pending'),
                HealthPlanItem(title='Body Fat Measurement', description='Measure body fat percentage monthly', status='pending'),
                HealthPlanItem(title='Update Health Profile', description='Review and update basic health information', status='completed'),
                HealthPlanItem(title='Track Daily Water Intake', description='Maintain 3L water intake daily', status='pending'),
            ]
            db.session.bulk_save_objects(initial_health_plan_items)
            db.session.commit()
            print("Health plan items seeded successfully.")
        else:
            print("Health plan items already seeded.")

if __name__ == '__main__':
    seed_health_data()
