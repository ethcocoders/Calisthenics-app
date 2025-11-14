from app import app, db, UserProfile, Video
from datetime import datetime

def seed_videos():
    """Seeds the database with initial video metadata if it doesn't exist."""
    with app.app_context():
        # --- 1. Check if videos already exist ---
        if Video.query.first():
            print("Video data already exists. Skipping seeding.")
            return

        # --- 2. Get or create the user profile ---
        user = UserProfile.query.first()
        if not user:
            print("Creating a default UserProfile for seeding videos.")
            user = UserProfile(id=1, level=1, experience_points=0)
            db.session.add(user)
            db.session.commit()

        print("Seeding video metadata...")

        # --- 3. Define the video data based on the HTML ---
        videos = [
            Video(
                title="Complete Push-up Tutorial for Beginners",
                description="Learn proper push-up form, common mistakes to avoid, and progression exercises to build strength.",
                category="tutorial",
                file_path="placeholder.mp4",
                duration="12:45",
                upload_date=datetime(2025, 11, 5),
                views=2400,
                likes=156,
                user_id=user.id
            ),
            Video(
                title="Full Body Calisthenics Workout - No Equipment",
                description="Complete 25-minute full body workout that you can do anywhere with zero equipment. Perfect for beginners!",
                category="workout",
                file_path="placeholder.mp4",
                duration="25:18",
                upload_date=datetime(2025, 11, 2),
                views=5800,
                likes=342,
                user_id=user.id
            ),
            Video(
                title="6-Month Calisthenics Transformation",
                description="Watch my incredible 6-month journey from beginner to intermediate calisthenics athlete with consistent training.",
                category="progress",
                file_path="placeholder.mp4",
                duration="8:32",
                upload_date=datetime(2025, 10, 28),
                views=12300,
                likes=876,
                user_id=user.id
            ),
            Video(
                title="Pull-up Progression: From Zero to 10 Reps",
                description="Complete guide to building pull-up strength with negative reps, assisted variations, and proper programming.",
                category="tutorial",
                file_path="placeholder.mp4",
                duration="18:21",
                upload_date=datetime(2025, 10, 22),
                views=8700,
                likes=523,
                user_id=user.id
            ),
            Video(
                title="Why I Train - My Calisthenics Journey",
                description="The story behind why I started calisthenics and how it changed my life both physically and mentally.",
                category="motivation",
                file_path="placeholder.mp4",
                duration="5:47",
                upload_date=datetime(2025, 10, 15),
                views=3200,
                likes=289,
                user_id=user.id
            ),
            Video(
                title="Advanced Calisthenics Flow - Skill Training",
                description="Learn advanced calisthenics movements and smooth transitions between skills like muscle-ups, front levers, and handstands.",
                category="workout",
                file_path="placeholder.mp4",
                duration="32:05",
                upload_date=datetime(2025, 10, 10),
                views=15600,
                likes=1200,
                user_id=user.id
            ),
        ]

        # --- 4. Add all videos to the session and commit ---
        db.session.bulk_save_objects(videos)
        db.session.commit()
        print("Successfully seeded 6 video records.")

if __name__ == "__main__":
    seed_videos()
