from app import app, db, UserProfile, Challenge, UserChallenge, Badge

def seed_tournament_data():
    """Seeds the Challenge/UserChallenge tables and now the Badge table."""
    with app.app_context():
        # --- 1. Seed Master Challenges ---
        if Challenge.query.filter_by(is_user_created=False).first() is not None:
            print("Master challenges already seeded.")
        else:
            print("Seeding master challenges...")
            initial_challenges = [
                Challenge(title="Push-up Endurance", level_requirement=1, xp_reward=50, task_details="Complete 50 Push-ups", time_limit="10 minutes"),
                Challenge(title="Core Strength Novice", level_requirement=5, xp_reward=100, task_details="Hold a 2-minute Plank", time_limit="2 minutes"),
                Challenge(title="Pull-up Beginner", level_requirement=10, xp_reward=150, task_details="Complete 10 strict Pull-ups", time_limit="15 minutes"),
                Challenge(title="Squat Power", level_requirement=15, xp_reward=200, task_details="Perform 100 Bodyweight Squats", time_limit="20 minutes"),
                Challenge(title="Dip Master", level_requirement=20, xp_reward=250, task_details="Complete 30 Dips", time_limit="15 minutes"),
                Challenge(title="Advanced Skill: Muscle-up", level_requirement=25, xp_reward=500, task_details="Perform 1 successful Muscle-up", time_limit=None),
                Challenge(title="Elite Endurance", level_requirement=30, xp_reward=1000, task_details="Complete a 100-rep circuit", time_limit="30 minutes"),
            ]
            db.session.bulk_save_objects(initial_challenges)
            db.session.commit()
            print("Master challenges seeded successfully.")

        # --- 2. Set Initial User Level & XP ---
        user = UserProfile.query.first()
        if user and user.level == 1 and user.experience_points == 0:
            print("Setting initial user level and XP...")
            user.level = 27
            user.experience_points = 7250 
            db.session.commit()
            print("User level and XP set to match static design.")
        
        # --- 3. Seed Initial UserChallenge Statuses ---
        if UserChallenge.query.first() is None:
            print("Seeding initial user challenge statuses...")
            user = UserProfile.query.first()
            all_challenges = Challenge.query.filter_by(is_user_created=False).all()
            if user and all_challenges:
                user_challenges = [UserChallenge(user_id=user.id, challenge_id=c.id, status='locked') for c in all_challenges]
                db.session.bulk_save_objects(user_challenges)
                db.session.commit()
                print("User challenges seeded successfully.")
        
        # --- 4. NEW: Seed Badges ---
        if Badge.query.first() is not None:
            print("Badges already seeded.")
        else:
            print("Seeding badges...")
            initial_badges = [
                Badge(name="Challenge Novice", description="Complete 5 Challenges", challenges_required=5),
                Badge(name="Challenge Adept", description="Complete 10 Challenges", challenges_required=10),
                Badge(name="Challenge Veteran", description="Complete 25 Challenges", challenges_required=25),
                Badge(name="Elite Challenger", description="Complete 50 Challenges", challenges_required=50),
                Badge(name="Super Grand Challenger", description="Complete 70 Challenges", challenges_required=70),
            ]
            db.session.bulk_save_objects(initial_badges)
            db.session.commit()
            print("Badges seeded successfully.")


if __name__ == '__main__':
    seed_tournament_data()
