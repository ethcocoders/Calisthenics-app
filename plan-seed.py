# --- seed_goals.py ---

from app import app, db, UserProfile, Goal, GoalMedia
from datetime import date, datetime

def seed_goals():
    """Seeds the database with initial goals if they don't exist."""
    with app.app_context():
        # --- 1. Check if goals already exist to prevent duplication ---
        if Goal.query.first():
            print("Goals already exist in the database. Skipping seeding.")
            return

        # --- 2. Get or create the user profile ---
        user = UserProfile.query.first()
        if not user:
            print("Creating a default UserProfile.")
            user = UserProfile(id=1, level=1, experience_points=0)
            db.session.add(user)
            db.session.commit() # Commit to get a user ID

        print("Seeding goals for user...")

        # --- 3. Define the goals data based on the HTML file ---

        goal1 = Goal(
            title="100 Push-ups in a Row",
            description="Achieve 100 consecutive push-ups with proper form and full range of motion.",
            status="completed",
            target_date=date(2025, 11, 5),
            completed_date=datetime(2025, 11, 5, 10, 0, 0),
            current_progress=100,
            target_progress=100,
            progress_unit="push-ups",
            user_id=user.id
        )
        db.session.add(goal1)
        db.session.flush() # Flush to get goal1.id for media linking

        goal2 = Goal(
            title="First Muscle-up",
            description="Perform your first clean muscle-up on the pull-up bar with controlled movement.",
            status="in_progress",
            target_date=date(2025, 12, 15),
            current_progress=65,
            target_progress=100,
            progress_unit="%",
            user_id=user.id
        )
        db.session.add(goal2)
        db.session.flush()

        goal3 = Goal(
            title="Handstand Hold - 60 Seconds",
            description="Hold a freestanding handstand for 60 seconds with good form and control.",
            status="in_progress",
            target_date=date(2026, 1, 20),
            current_progress=25,
            target_progress=60,
            progress_unit="seconds",
            user_id=user.id
        )
        db.session.add(goal3)
        db.session.flush()

        goal4 = Goal(
            title="Planche Progression",
            description="Begin planche progression training with tuck planche as the first milestone.",
            status="pending",
            target_date=date(2026, 2, 1),
            current_progress=0,
            target_progress=100,
            progress_unit="%",
            user_id=user.id
        )
        db.session.add(goal4)
        db.session.flush()

        # --- 4. Define and add associated media ---

        # Media for Goal 1 (Push-ups) - The first image is the "Before" photo for the gallery
        media1_1 = GoalMedia(goal_id=goal1.id, file_path="placeholder.jpg", media_type="image", is_before_photo=True)
        media1_2 = GoalMedia(goal_id=goal1.id, file_path="placeholder.jpg", media_type="image", is_after_photo=True)
        media1_3 = GoalMedia(goal_id=goal1.id, file_path="placeholder.mp4", media_type="video")

        # Media for Goal 2 (Muscle-up)
        media2_1 = GoalMedia(goal_id=goal2.id, file_path="placeholder.jpg", media_type="image")
        media2_2 = GoalMedia(goal_id=goal2.id, file_path="placeholder.jpg", media_type="image")
        media2_3 = GoalMedia(goal_id=goal2.id, file_path="placeholder.jpg", media_type="image")
        media2_4 = GoalMedia(goal_id=goal2.id, file_path="placeholder.mp4", media_type="video")
        media2_5 = GoalMedia(goal_id=goal2.id, file_path="placeholder.mp4", media_type="video")

        # Media for Goal 3 (Handstand)
        media3_1 = GoalMedia(goal_id=goal3.id, file_path="placeholder.jpg", media_type="image")
        media3_2 = GoalMedia(goal_id=goal3.id, file_path="placeholder.mp4", media_type="video")
        media3_3 = GoalMedia(goal_id=goal3.id, file_path="placeholder.mp4", media_type="video")
        media3_4 = GoalMedia(goal_id=goal3.id, file_path="placeholder.mp4", media_type="video")
        media3_5 = GoalMedia(goal_id=goal3.id, file_path="placeholder.mp4", media_type="video")

        db.session.add_all([
            media1_1, media1_2, media1_3,
            media2_1, media2_2, media2_3, media2_4, media2_5,
            media3_1, media3_2, media3_3, media3_4, media3_5
        ])

        # --- 5. Commit all changes to the database ---
        db.session.commit()
        print("Successfully seeded goals and media into the database.")

if __name__ == "__main__":
    seed_goals()
