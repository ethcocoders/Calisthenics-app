from app import app, db, Plan
from datetime import date

def seed_data():
    with app.app_context():
        # Check if plans already exist to avoid duplicates
        if Plan.query.first() is not None:
            print('Database already seeded with plans. Skipping.')
            return

        # Data transcribed from the static Plan.html prototype
        plans_to_add = [
            Plan(
                title='Upper Body Strength', 
                plan_type='Strength',
                start_date=date(2025, 11, 1), 
                end_date=date(2025, 11, 30),
                description='Focus on push-ups, pull-ups, and dips progression. Target: 20 push-ups, 10 pull-ups, 8 dips.',
                status='completed'
            ),
            Plan(
                title='Core Development', 
                plan_type='Strength',
                start_date=date(2025, 11, 5), 
                end_date=date(2025, 11, 25),
                description='Build core strength with planks, leg raises, and Russian twists. Target: 2-minute plank, 20 leg raises.',
                status='completed'
            ),
            Plan(
                title='Skill Progression', 
                plan_type='Skill',
                start_date=date(2025, 11, 10), 
                end_date=date(2025, 12, 10),
                description='Work on handstand balance and muscle-up progression. Daily skill practice for 15 minutes.',
                status='pending' # Will be "In Progress" based on date logic later
            ),
            Plan(
                title='Flexibility & Mobility', 
                plan_type='Flexibility',
                start_date=date(2025, 11, 15), 
                end_date=date(2025, 12, 15),
                description='Improve flexibility with daily stretching routine. Focus on shoulders, hips, and hamstrings.',
                status='pending' # Will be "Upcoming" based on date logic later
            ),
            Plan(
                title='Endurance Training', 
                plan_type='Endurance',
                start_date=date(2025, 11, 20), 
                end_date=date(2025, 12, 20),
                description='Build muscular endurance with high-rep circuits. Target: 50 push-ups in 5 minutes.',
                status='pending' # Will be "Upcoming" based on date logic later
            )
        ]

        # Add all plan objects to the session and commit
        db.session.bulk_save_objects(plans_to_add)
        db.session.commit()
        
        print('Database has been seeded with initial plan data.')

if __name__ == '__main__':
    seed_data()
