from app import app, db, UserProfile, MotivationItem

def seed_motivation():
    """Seeds the database with initial motivation items if they don't exist."""
    with app.app_context():
        # --- 1. Check if items already exist ---
        if MotivationItem.query.first():
            print("Motivation items already exist. Skipping seeding.")
            return

        # --- 2. Get or create the user profile ---
        user = UserProfile.query.first()
        if not user:
            print("Creating a default UserProfile for seeding motivation.")
            user = UserProfile(id=1, level=1, experience_points=0)
            db.session.add(user)
            db.session.commit()

        print("Seeding motivation items...")

        # --- 3. Define the motivation items based on the HTML ---
        items = [
            MotivationItem(
                title="From Zero to Hero",
                description="Watch this inspiring transformation story of a complete beginner who mastered advanced calisthenics skills in just 2 years.",
                category="video",
                author="Jake Williams",
                is_favorite=True,
                user_id=user.id
            ),
            MotivationItem(
                title="The Calisthenics Bible",
                description="Comprehensive guide to bodyweight training with detailed progressions, nutrition advice, and mindset strategies.",
                category="book",
                author="Mike Chen",
                is_favorite=True,
                user_id=user.id
            ),
            MotivationItem(
                title="Strength Through Struggle",
                description="Powerful reminder that every challenging workout is building your future strength and resilience.",
                category="quote",
                author="Unknown",
                is_favorite=True,
                user_id=user.id
            ),
            MotivationItem(
                title="Rocky IV - Siberian Training",
                description="Iconic training sequence showing Rocky's raw, natural training in the harsh Siberian wilderness - pure calisthenics inspiration.",
                category="movie",
                author="Sylvester Stallone",
                is_favorite=False,
                user_id=user.id
            ),
            MotivationItem(
                title="The Mind-Muscle Connection",
                description="Episode 45: Learn how to develop the mental focus needed to push through plateaus and achieve your fitness goals.",
                category="podcast",
                author="Fitness Mindset",
                is_favorite=False,
                user_id=user.id
            ),
            MotivationItem(
                title="Street Workout World Finals",
                description="Watch the world's best calisthenics athletes compete in incredible displays of strength, skill, and creativity.",
                category="video",
                author="World Championship",
                is_favorite=False,
                user_id=user.id
            ),
            MotivationItem(
                title="Atomic Habits",
                description="Learn how to build good habits and break bad ones with this groundbreaking guide to behavior change and personal development.",
                category="book",
                author="James Clear",
                is_favorite=True,
                user_id=user.id
            ),
            MotivationItem(
                title="The Power of Discipline",
                description="Perfect reminder for those days when you don't feel like training but know you'll regret skipping it tomorrow.",
                category="quote",
                author="Abraham Lincoln",
                is_favorite=False,
                user_id=user.id
            )
        ]

        # --- 4. Add all items to the session and commit ---
        db.session.bulk_save_objects(items)
        db.session.commit()
        print("Successfully seeded 8 motivation items.")

if __name__ == "__main__":
    seed_motivation()
