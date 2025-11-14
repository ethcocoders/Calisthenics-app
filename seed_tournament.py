from app import app, db, UserProfile, Challenge, UserChallenge, Badge

def seed_tournament_data():
    """Seeds all tables related to the tournament and gamification features."""
    with app.app_context():
        # --- 1. Seed Badges ---
        if Badge.query.first() is not None:
            print("Badges already seeded.")
        else:
            print("Seeding badges...")
            initial_badges = [
                Badge(name="Bronze Challenge", description="Awarded for completing the Level 25 challenge.", icon="fa-award", color="#cd7f32"),
                Badge(name="Silver Challenge", description="Awarded for completing the Level 40 challenge.", icon="fa-award", color="#c0c0c0"),
                Badge(name="Golden Challenge", description="Awarded for completing the Level 55 challenge.", icon="fa-trophy", color="#ffd700"),
                Badge(name="Super Challenge", description="Awarded for completing the Level 70 challenge.", icon="fa-star", color="#e91e63"),
                Badge(name="Elite Challenge", description="Awarded for completing the Level 85 challenge.", icon="fa-shield-alt", color="#74b9ff"),
                Badge(name="Grand Challenge", description="Awarded for completing the Level 100 challenge.", icon="fa-crown", color="#e67e22"),
                Badge(name="Grand Master", description="Awarded for surpassing Level 100.", icon="fa-chess-king", color="#d63031"),
            ]
            db.session.bulk_save_objects(initial_badges)
            db.session.commit()
            print("Badges seeded successfully.")

        # --- 2. Seed Milestone Challenges ---
        if Challenge.query.filter_by(is_milestone_challenge=True).first() is not None:
            print("Milestone challenges already seeded.")
        else:
            print("Seeding milestone challenges...")
            bronze_badge = Badge.query.filter_by(name="Bronze Challenge").first()
            silver_badge = Badge.query.filter_by(name="Silver Challenge").first()
            golden_badge = Badge.query.filter_by(name="Golden Challenge").first()
            super_badge = Badge.query.filter_by(name="Super Challenge").first()
            elite_badge = Badge.query.filter_by(name="Elite Challenge").first()
            grand_badge = Badge.query.filter_by(name="Grand Challenge").first()
            master_badge = Badge.query.filter_by(name="Grand Master").first()

            milestone_challenges = [
                Challenge(title="The Bronze Trial", level_requirement=25, xp_reward=1000, task_details="Complete 10 Muscle-ups", is_milestone_challenge=True, awards_badge_id=bronze_badge.id),
                Challenge(title="The Silver Gauntlet", level_requirement=40, xp_reward=2000, task_details="Hold a 30-second Front Lever", is_milestone_challenge=True, awards_badge_id=silver_badge.id),
                Challenge(title="The Golden Standard", level_requirement=55, xp_reward=3000, task_details="Perform 5 Freestanding Handstand Push-ups", is_milestone_challenge=True, awards_badge_id=golden_badge.id),
                Challenge(title="The Super Human Test", level_requirement=70, xp_reward=4000, task_details="Hold a 15-second Full Planche", is_milestone_challenge=True, awards_badge_id=super_badge.id),
                Challenge(title="The Elite Proving Ground", level_requirement=85, xp_reward=5000, task_details="Perform 3 One-Arm Pull-ups (Each Arm)", is_milestone_challenge=True, awards_badge_id=elite_badge.id),
                Challenge(title="The Grand Finale", level_requirement=100, xp_reward=10000, task_details="Complete a 10-minute non-stop freestyle routine", is_milestone_challenge=True, awards_badge_id=grand_badge.id),
                Challenge(title="Beyond Grand Master", level_requirement=101, xp_reward=0, task_details="Surpass Level 100", is_milestone_challenge=True, awards_badge_id=master_badge.id),
            ]
            db.session.bulk_save_objects(milestone_challenges)
            db.session.commit()
            print("Milestone challenges seeded successfully.")

        # --- 3. Seed UserChallenge links for system challenges ---
        user = UserProfile.query.first()
        if user:
            system_challenges = Challenge.query.filter_by(is_user_created=False).all()
            existing_links = {uc.challenge_id for uc in UserChallenge.query.filter_by(user_id=user.id).all()}
            
            new_links = []
            for challenge in system_challenges:
                if challenge.id not in existing_links:
                    new_links.append(UserChallenge(user_id=user.id, challenge_id=challenge.id, status='locked'))
            
            if new_links:
                print("Seeding new UserChallenge links...")
                db.session.bulk_save_objects(new_links)
                db.session.commit()
                print(f"{len(new_links)} new user-challenge links created.")
            else:
                print("UserChallenge links are up to date.")
        else:
            print("User not found, cannot seed UserChallenge links.")

if __name__ == '__main__':
    seed_tournament_data()
