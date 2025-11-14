import ffmpeg
import json
from datetime import datetime, time, timedelta, date
import os
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import uuid

# Get the base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))

# Initialize the Flask application
app = Flask(__name__)

# --- Configuration ---
# Secret key is required for flash messages
app.config['SECRET_KEY'] = 'a-very-secret-key-that-should-be-changed'
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'calisthenics.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads', 'goals')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

app.config['MOTIVATION_UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads', 'motivation')

# --- Make sure the motivation upload folder exists ---
if not os.path.exists(app.config['MOTIVATION_UPLOAD_FOLDER']):
    os.makedirs(app.config['MOTIVATION_UPLOAD_FOLDER'])

app.config['VIDEO_UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads', 'videos')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB limit

# --- Make sure the video upload folder exists ---
if not os.path.exists(app.config['VIDEO_UPLOAD_FOLDER']):
    os.makedirs(app.config['VIDEO_UPLOAD_FOLDER'])

# --- Helper function to format seconds into MM:SS or HH:MM:SS ---
def format_duration(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes:02}:{seconds:02}"

# --- Add this configuration line for thumbnails ---
app.config['THUMBNAIL_UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads', 'thumbnails')

# --- Make sure the thumbnail upload folder exists ---
if not os.path.exists(app.config['THUMBNAIL_UPLOAD_FOLDER']):
    os.makedirs(app.config['THUMBNAIL_UPLOAD_FOLDER'])

# --- Initialize Extensions ---
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- UserProfile MODEL ---
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Float, nullable=True)  # in cm
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    level = db.Column(db.Integer, nullable=False, default=1)
    experience_points = db.Column(db.Integer, nullable=False, default=0)

    # Relationship to access challenges created by this user
    created_challenges = db.relationship('Challenge', backref='creator', lazy='dynamic')
    goals = db.relationship('Goal', backref='user', lazy='dynamic')
    motivation_items = db.relationship('MotivationItem', backref='user', lazy='dynamic')
    videos = db.relationship('Video', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<UserProfile {self.id}>'

# --- Define HealthRecord Model ---
class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    weight = db.Column(db.Float, nullable=True) # in kg
    body_fat = db.Column(db.Float, nullable=True) # as percentage
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<HealthRecord {self.date}>'

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.String(50), nullable=False) # String to handle "12/Leg"
    rest = db.Column(db.String(50), nullable=False)
    instructions = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Workout {self.name}>'

# --- Define Event Model ---
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False) # e.g., 'workout', 'rest'
    start_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='scheduled') # New column

    def __repr__(self):
        return f'<Event {self.title}>'

# --- Define ScheduleItem Model ---
class ScheduleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    details = db.Column(db.Text, nullable=True)
    day_of_week = db.Column(db.String(20), nullable=False) # e.g., 'Monday', 'Tuesday'
    time = db.Column(db.Time, nullable=False)
    category = db.Column(db.String(50), nullable=False) # e.g., 'workout', 'rest'
    status = db.Column(db.String(50), nullable=False, default='scheduled')

    def __repr__(self):
        return f'<ScheduleItem {self.title}>'

# --- Define TrainingPlan Model ---
class TrainingPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='upcoming') # upcoming, pending, completed

    def __repr__(self):
        return f'<TrainingPlan {self.title}>'

# --- Define StickyNote Model ---
class StickyNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    color = db.Column(db.String(20), nullable=False, default='yellow')

    def __repr__(self):
        return f'<StickyNote {self.title}>'

# --- ADD THIS CODE TO app.py ---

# --- Define HealthPlanItem Model ---
class HealthPlanItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='pending') # 'pending' or 'completed'

    def __repr__(self):
        return f'<HealthPlanItem {self.title}>'

# --- NEW GOAL MODELS START HERE ---

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='pending') # 'pending', 'in_progress', 'completed'
    target_date = db.Column(db.Date, nullable=False)
    completed_date = db.Column(db.DateTime, nullable=True)
    
    current_progress = db.Column(db.Float, nullable=False, default=0)
    target_progress = db.Column(db.Float, nullable=False, default=100)
    progress_unit = db.Column(db.String(50), nullable=True) # e.g., 'reps', 'seconds', '%'

    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=True)

    media = db.relationship('GoalMedia', backref='goal', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Goal {self.title}>'

class GoalMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    media_type = db.Column(db.String(50), nullable=False) # 'image' or 'video'
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # For the Before/After gallery feature
    is_before_photo = db.Column(db.Boolean, default=False)
    is_after_photo = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<GoalMedia {self.file_path} for Goal {self.goal_id}>'

class MotivationItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False) # 'video', 'book', 'quote', etc.
    author = db.Column(db.String(150), nullable=True)
    source_url = db.Column(db.String(500), nullable=True)
    cover_image_path = db.Column(db.String(300), nullable=True)
    is_favorite = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=True)

    def __repr__(self):
        return f'<MotivationItem {self.title}>'

# --- Define Challenge Model ---
class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    level_requirement = db.Column(db.Integer, nullable=False, default=1)
    xp_reward = db.Column(db.Integer, nullable=False, default=50)
    task_details = db.Column(db.String(300), nullable=False)
    time_limit = db.Column(db.String(50), nullable=True)
    is_user_created = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=True)
    
    # New columns for milestone/badge system
    is_milestone_challenge = db.Column(db.Boolean, default=False, nullable=False)
    awards_badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'), nullable=True)
    
    badge_to_award = db.relationship('Badge')

    def __repr__(self):
        return f'<Challenge {self.title}>'

# --- Define UserChallenge (Association) Model ---
class UserChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='locked') # locked, unlocked, active, completed
    started_at = db.Column(db.DateTime, nullable=True) # New column

    user = db.relationship('UserProfile', backref=db.backref('challenges', lazy='dynamic'))
    challenge = db.relationship('Challenge', backref=db.backref('user_links', lazy='dynamic'))

    def __repr__(self):
        return f'<UserChallenge User {self.user_id} - Challenge {self.challenge_id}: {self.status}>'

# --- Define Badge Model ---
class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(50), nullable=False, default='fa-shield-alt') # e.g., fa-shield-alt, fa-trophy
    color = db.Column(db.String(50), nullable=False, default='#c0c0c0') # e.g., Hex color code
    challenges_required = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return f'<Badge {self.name}>'

# --- Define UserBadge (Association) Model ---
class UserBadge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'), nullable=False)
    date_earned = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('UserProfile', backref=db.backref('earned_badges', lazy='dynamic'))
    badge = db.relationship('Badge')

    def __repr__(self):
        return f'<UserBadge User {self.user_id} earned {self.badge.name}>'

# --- REPLACE THE Video MODEL WITH THIS UPDATED VERSION ---

# --- REPLACE THE Video MODEL WITH THIS UPDATED VERSION ---
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    
    file_path = db.Column(db.String(300), nullable=False)
    thumbnail_path = db.Column(db.String(300), nullable=True)
    duration = db.Column(db.String(20), nullable=True) # e.g., "12:45"
    size_mb = db.Column(db.Float, nullable=True) # To store file size in MB
    
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=True)

    def __repr__(self):
        return f'<Video {self.title}>'    

# --- Main Application Routes ---

@app.route('/')
def index():
    return render_template('index.html', active_page='index')

@app.route('/workouts')
def workouts():
    all_workouts = Workout.query.order_by(Workout.id).all()
    return render_template('Workouts.html', workouts=all_workouts, active_page='workouts')

# --- Routes for Adding and Deleting Workouts ---

@app.route('/workouts/add', methods=['POST'])
def add_workout():
    if request.method == 'POST':
        name = request.form['name']
        difficulty = request.form['difficulty']
        sets = request.form['sets']
        reps = request.form['reps']
        rest = request.form['rest']
        instructions = request.form['instructions']
        
        # Basic validation
        if name and difficulty and sets and reps and rest and instructions:
            # Check if workout already exists
            existing_workout = Workout.query.filter_by(name=name).first()
            if existing_workout:
                flash(f'Workout "{name}" already exists.', 'danger')
            else:
                new_workout = Workout(
                    name=name,
                    difficulty=difficulty,
                    sets=int(sets),
                    reps=reps,
                    rest=rest,
                    instructions=instructions
                )
                db.session.add(new_workout)
                db.session.commit()
                flash('Workout added successfully!', 'success')
        else:
            flash('All fields are required.', 'danger')
            
    return redirect(url_for('workouts'))

@app.route('/workouts/delete/<int:workout_id>', methods=['POST'])
def delete_workout(workout_id):
    workout_to_delete = Workout.query.get_or_404(workout_id)
    db.session.delete(workout_to_delete)
    db.session.commit()
    flash('Workout deleted successfully.', 'success')
    return redirect(url_for('workouts'))

# --- ADD THIS CODE TO app.py ---

# --- Add these new models to the 'from app import' line if you created a separate seed file ---
# (This is just a reminder, no code change needed if your models are in app.py)
# from app import ..., Goal, GoalMedia

# --- Make sure the upload folder exists ---
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# --- Placeholder Routes for Other Pages ---

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', active_page='index')

# --- GOALS SECTION START ---

@app.route('/goals')
def goals():
    # 1. Fetch user and all their goals
    user = UserProfile.query.first()
    if not user:
        # Handle case where no user exists
        return redirect(url_for('index')) # Or some setup page

    all_goals = Goal.query.filter_by(user_id=user.id).order_by(Goal.target_date.asc()).all()

    # 2. Calculate overview statistics
    total_goals = len(all_goals)
    completed_goals = Goal.query.filter_by(user_id=user.id, status='completed').count()
    completion_percentage = round((completed_goals / total_goals) * 100) if total_goals > 0 else 0

    # 3. Fetch Before/After gallery photos
    before_photo_media = GoalMedia.query.filter_by(is_before_photo=True).join(Goal).filter(Goal.user_id == user.id).first()
    after_photo_media = GoalMedia.query.filter_by(is_after_photo=True).join(Goal).filter(Goal.user_id == user.id).first()
    
    # 4. Pass data to the template
    return render_template(
        'Goals.html',
        active_page='goals',
        all_goals=all_goals,
        total_goals=total_goals,
        completed_goals=completed_goals,
        completion_percentage=completion_percentage,
        before_photo=before_photo_media,
        after_photo=after_photo_media
    )

@app.route('/goals/add', methods=['POST'])
def add_goal():
    user = UserProfile.query.first()
    if not user:
        flash('User profile not found.', 'danger')
        return redirect(url_for('goals'))

    title = request.form.get('title')
    description = request.form.get('description')
    target_date_str = request.form.get('target_date')
    notes = request.form.get('notes')
    
    if not all([title, target_date_str]):
        flash('Goal Title and Target Date are required.', 'danger')
        return redirect(url_for('goals'))

    target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()

    new_goal = Goal(
        title=title,
        description=description,
        target_date=target_date,
        notes=notes,
        status='pending',
        user_id=user.id
    )
    db.session.add(new_goal)
    db.session.flush() # To get the new_goal.id for media linking

    # Handle file uploads
    files = request.files.getlist('media_files[]')
    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            media_type = 'image' if file.mimetype.startswith('image/') else 'video'
            
            # Note: For a real app, logic to set is_before/is_after would be needed here
            new_media = GoalMedia(
                goal_id=new_goal.id,
                file_path=os.path.join('uploads', 'goals', unique_filename), # Store relative path for URL
                media_type=media_type
            )
            db.session.add(new_media)

    db.session.commit()
    flash('New goal created successfully!', 'success')
    return redirect(url_for('goals'))

@app.route('/goals/delete/<int:goal_id>', methods=['POST'])
def delete_goal(goal_id):
    goal_to_delete = Goal.query.get_or_404(goal_id)

    # Delete associated media files from the server
    for media in goal_to_delete.media:
        try:
            # Construct the full path to the file
            full_path = os.path.join('static', media.file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as e:
            print(f"Error deleting file {media.file_path}: {e}") # Log error

    db.session.delete(goal_to_delete)
    db.session.commit()
    flash('Goal deleted successfully.', 'success')
    return redirect(url_for('goals'))

@app.route('/goals/toggle_status/<int:goal_id>', methods=['POST'])
def toggle_goal_status(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    
    if goal.status == 'completed':
        goal.status = 'in_progress'
        goal.completed_date = None
        flash(f'Goal "{goal.title}" marked as in-progress.', 'info')
    else:
        goal.status = 'completed'
        goal.current_progress = goal.target_progress # Auto-complete progress
        goal.completed_date = datetime.utcnow()
        flash(f'Congratulations on completing "{goal.title}"!', 'success')
        
    db.session.commit()
    return redirect(url_for('goals'))

# --- GOALS SECTION END ---

@app.route('/plan')
def plan():
    # 1. Fetch all training plans from the database
    all_plans = TrainingPlan.query.order_by(TrainingPlan.start_date).all()

    # 2. NEW: Process plans into a dictionary keyed by date for the JS calendar
    plans_by_day = {}
    for plan in all_plans:
        current_date = plan.start_date
        while current_date <= plan.end_date:
            date_str = current_date.isoformat() # 'YYYY-MM-DD'
            # Store the plan details for this specific day
            plans_by_day[date_str] = {
                'title': plan.title,
                'status': plan.status,
                'description': plan.description
            }
            current_date += timedelta(days=1)

    # 3. Calculate overview stats (unchanged)
    total_plans = len(all_plans)
    completed_plans = TrainingPlan.query.filter_by(status='completed').count()
    pending_plans = total_plans - completed_plans
    completion_percentage = round((completed_plans / total_plans) * 100) if total_plans > 0 else 0
    
    # 4. Get current date info for calendar highlighting
    today = date.today()

    # 5. Pass all data to the template
    return render_template(
        'Plan.html',
        active_page='plan',
        all_plans=all_plans,
        total_plans=total_plans,
        completed_plans=completed_plans,
        pending_plans=pending_plans,
        completion_percentage=completion_percentage,
        plans_for_js=json.dumps(plans_by_day), # Pass the new dictionary
        today_iso=today.isoformat()
    )

@app.route('/plans/add', methods=['POST'])
def add_plan():
    title = request.form.get('title')
    description = request.form.get('description')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')

    if not all([title, description, start_date_str, end_date_str]):
        flash('All fields are required.', 'danger')
        return redirect(url_for('plan'))

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Determine status based on dates
    today = date.today()
    status = 'pending'
    if start_date > today:
        status = 'upcoming'
    
    new_plan = TrainingPlan(
        title=title, description=description, 
        start_date=start_date, end_date=end_date, status=status
    )
    db.session.add(new_plan)
    db.session.commit()
    flash('New training plan added successfully!', 'success')
    return redirect(url_for('plan'))

@app.route('/plans/edit/<int:plan_id>', methods=['GET', 'POST'])
def edit_plan(plan_id):
    plan = TrainingPlan.query.get_or_404(plan_id)
    if request.method == 'POST':
        plan.title = request.form.get('title')
        plan.description = request.form.get('description')
        plan.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        plan.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        plan.status = request.form.get('status')
        db.session.commit()
        flash('Training plan updated successfully!', 'success')
        return redirect(url_for('plan'))
    
    return render_template('edit_plan.html', plan=plan, active_page='plan')

@app.route('/plans/delete/<int:plan_id>', methods=['POST'])
def delete_plan(plan_id):
    plan = TrainingPlan.query.get_or_404(plan_id)
    db.session.delete(plan)
    db.session.commit()
    flash('Training plan deleted successfully.', 'success')
    return redirect(url_for('plan'))

#_________________________________

# ------SCHEDULE SECTION -----‐---
@app.route('/schedule')
def schedule():
    all_schedule_items = ScheduleItem.query.order_by(ScheduleItem.time).all()
    all_sticky_notes = StickyNote.query.order_by(StickyNote.id).all()

    # Group schedule items by day for easy rendering in the template
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    schedule_items_by_day = {day: [] for day in days_of_week}
    for item in all_schedule_items:
        schedule_items_by_day[item.day_of_week].append(item)

    # Calculate stats
    total_sessions = len(all_schedule_items)
    completed_sessions = ScheduleItem.query.filter_by(status='completed').count()
    workout_sessions = ScheduleItem.query.filter_by(category='workout').count()
    rest_sessions = ScheduleItem.query.filter_by(category='rest').count()
    completion_percentage = round((completed_sessions / total_sessions) * 100) if total_sessions > 0 else 0
    current_day_name = datetime.now().strftime('%A')

    return render_template(
        'Schedule.html',
        active_page='schedule',
        days_of_week=days_of_week,
        schedule_items_by_day=schedule_items_by_day,
        sticky_notes=all_sticky_notes,
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        workout_sessions=workout_sessions,
        rest_sessions=rest_sessions,
        completion_percentage=completion_percentage,
        current_day_name=current_day_name
    )

@app.route('/schedule/add', methods=['POST'])
def add_schedule_item():
    title = request.form.get('title')
    details = request.form.get('details')
    day = request.form.get('day_of_week')
    time_str = request.form.get('time')
    category = request.form.get('category')

    if not all([title, day, time_str, category]):
        flash('Required fields are missing.', 'danger')
        return redirect(url_for('schedule'))

    # Convert time string from form (HH:MM) to a time object
    item_time = datetime.strptime(time_str, '%H:%M').time()
    
    new_item = ScheduleItem(
        title=title, details=details, day_of_week=day,
        time=item_time, category=category
    )
    db.session.add(new_item)
    db.session.commit()
    flash('Schedule item added successfully!', 'success')
    return redirect(url_for('schedule'))

@app.route('/schedule/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_schedule_item(item_id):
    item = ScheduleItem.query.get_or_404(item_id)
    if request.method == 'POST':
        item.title = request.form.get('title')
        item.details = request.form.get('details')
        item.day_of_week = request.form.get('day_of_week')
        item.time = datetime.strptime(request.form.get('time'), '%H:%M').time()
        item.category = request.form.get('category')
        db.session.commit()
        flash('Schedule item updated successfully!', 'success')
        return redirect(url_for('schedule'))
        
    return render_template('edit_schedule_item.html', item=item, active_page='schedule')

@app.route('/schedule/delete/<int:item_id>', methods=['POST'])
def delete_schedule_item(item_id):
    item = ScheduleItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Schedule item deleted successfully!', 'success')
    return redirect(url_for('schedule'))

@app.route('/schedule/complete/<int:item_id>', methods=['POST'])
def complete_schedule_item(item_id):
    item = ScheduleItem.query.get_or_404(item_id)
    item.status = 'completed'
    db.session.commit()
    flash(f'"{item.title}" marked as complete!', 'success')
    return redirect(url_for('schedule'))

@app.route('/notes/add', methods=['POST'])
def add_note():
    title = request.form.get('title')
    content = request.form.get('content')
    color = request.form.get('color')

    if not all([title, content, color]):
        flash('All note fields are required.', 'danger')
        return redirect(url_for('schedule'))

    new_note = StickyNote(title=title, content=content, color=color)
    db.session.add(new_note)
    db.session.commit()
    flash('Sticky note added successfully!', 'success')
    return redirect(url_for('schedule'))

@app.route('/notes/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    note = StickyNote.query.get_or_404(note_id)
    if request.method == 'POST':
        note.title = request.form.get('title')
        note.content = request.form.get('content')
        note.color = request.form.get('color')
        db.session.commit()
        flash('Sticky note updated successfully!', 'success')
        return redirect(url_for('schedule'))

    return render_template('edit_note.html', note=note, active_page='schedule')

@app.route('/notes/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    note = StickyNote.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    flash('Sticky note deleted successfully!', 'success')
    return redirect(url_for('schedule'))

#---------------------------------

#----- Calandar ----#
@app.route('/calendar')
def calendar():
    # 1. Fetch and format all events for the calendar grid
    events = Event.query.all()
    events_data = {}
    for event in events:
        date_str = event.start_time.strftime('%Y-%m-%d')
        events_data[date_str] = {
            'id': event.id, 'type': event.category, 'name': event.title,
            'time': event.start_time.strftime('%I:%M %p'), 'status': event.status
        }

    # 2. Calculate overview stats (unchanged)
    now = datetime.utcnow()
    current_month, current_year = now.month, now.year
    total_workouts = Event.query.filter(Event.category == 'workout', db.extract('month', Event.start_time) == current_month, db.extract('year', Event.start_time) == current_year).count()
    completed_workouts = Event.query.filter(Event.category == 'workout', Event.status == 'completed', db.extract('month', Event.start_time) == current_month, db.extract('year', Event.start_time) == current_year).count()
    planned_workouts = total_workouts - completed_workouts
    rest_days = Event.query.filter(Event.category == 'rest', db.extract('month', Event.start_time) == current_month, db.extract('year', Event.start_time) == current_year).count()
    completion_percentage = round((completed_workouts / total_workouts) * 100) if total_workouts > 0 else 0

    # 3. NEW: Fetch upcoming events for the next 5 days
    today = now.date()
    five_days_later = today + timedelta(days=5)
    upcoming_events = Event.query.filter(
        Event.start_time >= today,
        Event.start_time < five_days_later,
        Event.status == 'scheduled'
    ).order_by(Event.start_time.asc()).all()

    # 4. Pass all data to the template
    return render_template(
        'calander.html',
        active_page='calendar',
        events_data_json=json.dumps(events_data),
        total_workouts=total_workouts, completed_workouts=completed_workouts,
        planned_workouts=planned_workouts, rest_days=rest_days,
        completion_percentage=completion_percentage,
        upcoming_events=upcoming_events  # Pass the new data
    )

@app.route('/calendar/add', methods=['POST'])
def add_event():
    title = request.form.get('title')
    category = request.form.get('category')
    start_time_str = request.form.get('start_time')

    if not all([title, category, start_time_str]):
        flash('All fields are required.', 'danger')
        return redirect(url_for('calendar'))

    # Convert the string from the form into a Python datetime object
    start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')

    new_event = Event(title=title, category=category, start_time=start_time)
    db.session.add(new_event)
    db.session.commit()

    flash('Plan added successfully!', 'success')
    return redirect(url_for('calendar'))

@app.route('/calendar/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event_to_delete = Event.query.get_or_404(event_id)
    db.session.delete(event_to_delete)
    db.session.commit()
    flash('Plan deleted successfully.', 'success')
    return redirect(url_for('calendar'))

@app.route('/calendar/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        start_time_str = request.form.get('start_time')

        if not all([title, category, start_time_str]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('edit_event', event_id=event.id))
        
        event.title = title
        event.category = category
        event.start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        
        db.session.commit()
        flash('Plan updated successfully!', 'success')
        return redirect(url_for('calendar'))
    
    # For GET request, render the edit page
    return render_template('edit_event.html', event=event, active_page='calendar')

@app.route('/calendar/complete/<int:event_id>', methods=['POST'])
def complete_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.status = 'completed'
    db.session.commit()
    flash(f'Workout "{event.title}" marked as complete!', 'success')
    return redirect(url_for('calendar'))

#--------------------

#-------‐------Health_section------------------# 

@app.route('/health')
def health():
    # --- 1. Fetch Core Data ---
    profile = UserProfile.query.first() or UserProfile()
    all_health_records = HealthRecord.query.order_by(HealthRecord.date.desc()).all()
    health_plan_items = HealthPlanItem.query.order_by(HealthPlanItem.id).all()
    latest_record = all_health_records[0] if all_health_records else None

    # --- 2. Calculate Real-Time Stats ---
    bmi = None
    if profile.height and latest_record and latest_record.weight:
        height_in_meters = profile.height / 100
        bmi = round(latest_record.weight / (height_in_meters ** 2), 1)

    # --- 3. Prepare Data for Weight Chart ---
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    chart_records = HealthRecord.query.filter(HealthRecord.date >= six_months_ago).order_by(HealthRecord.date.asc()).all()
    chart_labels = [record.date.strftime('%b %d, %Y') for record in chart_records]
    chart_data = [record.weight for record in chart_records]

    # --- 4. NEW: Prepare full record data for the interactive calendar ---
    records_by_date = {}
    for record in all_health_records:
        date_str = record.date.strftime('%-d') # Key by day number, e.g., '1', '15', '21'
        # This assumes one record per day for simplicity. For multiple, this would be a list.
        records_by_date[date_str] = {
            'weight': record.weight,
            'body_fat': record.body_fat,
            'notes': record.notes
        }
    
    now = datetime.utcnow()
    # Get just the day numbers for highlighting
    measured_days = list(records_by_date.keys())

    # --- 5. Pass All Data to Template ---
    return render_template(
        'Health.html',
        active_page='health',
        profile=profile,
        latest_record=latest_record,
        bmi=bmi,
        health_plan_items=health_plan_items,
        chart_labels=json.dumps(chart_labels),
        chart_data=json.dumps(chart_data),
        measured_days=json.dumps(measured_days),
        records_by_date_json=json.dumps(records_by_date), # Pass full details
        current_day=now.day
    )


@app.route('/profile/update', methods=['POST'])
def update_profile():
    profile = UserProfile.query.first()
    if not profile:
        profile = UserProfile()
        db.session.add(profile)
    
    profile.height = request.form.get('height', type=float)
    profile.age = request.form.get('age', type=int)
    profile.gender = request.form.get('gender')
    
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('health'))

@app.route('/health/add', methods=['POST'])
def add_health_record():
    date_str = request.form.get('date')
    weight = request.form.get('weight', type=float)
    body_fat = request.form.get('body_fat', type=float)
    notes = request.form.get('notes')

    if not date_str or not weight:
        flash('Date and Weight are required fields.', 'danger')
        return redirect(url_for('health'))

    record_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    new_record = HealthRecord(
        date=record_date, weight=weight,
        body_fat=body_fat, notes=notes
    )
    db.session.add(new_record)
    db.session.commit()
    flash('Health record added successfully!', 'success')
    return redirect(url_for('health'))

# Note: UI for edit/delete is not the focus of this part, but the backend is ready.
@app.route('/health/delete/<int:record_id>', methods=['POST'])
def delete_health_record(record_id):
    record = HealthRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash('Health record deleted.', 'success')
    return redirect(url_for('health'))

@app.route('/health-plan/add', methods=['POST'])
def add_health_plan_item():
    title = request.form.get('title')
    description = request.form.get('description')
    if title:
        new_item = HealthPlanItem(title=title, description=description)
        db.session.add(new_item)
        db.session.commit()
        flash('Health plan item added.', 'success')
    return redirect(url_for('health'))

@app.route('/health-plan/toggle/<int:item_id>', methods=['POST'])
def toggle_health_plan_item(item_id):
    item = HealthPlanItem.query.get_or_404(item_id)
    item.status = 'completed' if item.status == 'pending' else 'pending'
    db.session.commit()
    return redirect(url_for('health'))

@app.route('/health-plan/delete/<int:item_id>', methods=['POST'])
def delete_health_plan_item(item_id):
    item = HealthPlanItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Health plan item deleted.', 'success')
    return redirect(url_for('health'))

@app.route('/health-plan/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_health_plan_item(item_id):
    item = HealthPlanItem.query.get_or_404(item_id)
    if request.method == 'POST':
        item.title = request.form.get('title')
        item.description = request.form.get('description')
        db.session.commit()
        flash('Health plan item updated.', 'success')
        return redirect(url_for('health'))
    return render_template('edit_health_plan_item.html', item=item, active_page='health')

@app.route('/health/export')
def export_health_data():
    # 1. Fetch all data from the database
    profile = UserProfile.query.first()
    records = HealthRecord.query.order_by(HealthRecord.date.desc()).all()

    # 2. Build the text content
    content = "CALISTHENICS APP - HEALTH DATA EXPORT\n"
    content += "========================================\n\n"
    
    if profile:
        content += "USER PROFILE\n"
        content += "-----------------\n"
        content += f"Height: {profile.height or 'N/A'} cm\n"
        content += f"Age: {profile.age or 'N/A'}\n"
        content += f"Gender: {profile.gender or 'N/A'}\n\n"
    
    content += "HEALTH RECORDS\n"
    content += "-----------------\n"
    content += "Date, Weight (kg), Body Fat (%), Notes\n"
    
    if records:
        for record in records:
            content += f"{record.date.strftime('%Y-%m-%d')},{record.weight or 'N/A'},{record.body_fat or 'N/A'},\"{record.notes or ''}\"\n"
    else:
        content += "No records found.\n"

    # 3. Create the response to send the file
    return Response(
        content,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=health_data_{datetime.utcnow().strftime('%Y-%m-%d')}.csv"}
    )

@app.route('/health/edit/<int:record_id>', methods=['GET', 'POST'])
def edit_health_record(record_id):
    record = HealthRecord.query.get_or_404(record_id)
    if request.method == 'POST':
        record.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        record.weight = request.form.get('weight', type=float)
        record.body_fat = request.form.get('body_fat', type=float)
        record.notes = request.form.get('notes')
        
        db.session.commit()
        flash('Health record updated successfully!', 'success')
        return redirect(url_for('health'))
        
    return render_template('edit_health_record.html', record=record, active_page='health')

#________________________________________________


# Helper function to define the XP required for each level (can be placed above the routes)
def xp_for_level(level):
    """Calculates the total XP required to reach a certain level."""
    return int(1000 * (1.1 ** (level - 1)))

#---------TOURNAMENT -------------------------

@app.route('/tournament')
def tournament():
    # 1. Fetch Core Data
    profile = UserProfile.query.first()
    if not profile:
        # Create a default profile if one doesn't exist, to prevent errors on first run
        profile = UserProfile(level=1, experience_points=0)
        db.session.add(profile)
        db.session.commit()
        flash("Welcome! Your user profile has been created.", 'info')

    # 2. Unlock Challenges based on User Level
    unlockable_challenges = UserChallenge.query.join(Challenge).filter(
        UserChallenge.user_id == profile.id,
        UserChallenge.status == 'locked',
        Challenge.level_requirement <= profile.level
    ).all()

    if unlockable_challenges:
        for uc in unlockable_challenges:
            uc.status = 'unlocked'
        db.session.commit()
        flash('New challenges have been unlocked!', 'info')

    # 3. Fetch all data for rendering
    all_user_challenges = UserChallenge.query.filter_by(user_id=profile.id).join(Challenge).order_by(Challenge.level_requirement).all()
    
    # --- THIS IS THE FIX ---
    # Explicitly join with Badge to access its columns for sorting
    earned_badges = UserBadge.query.filter_by(user_id=profile.id).join(Badge).order_by(Badge.challenges_required).all()

    # 4. Calculate Level and XP Bar (unchanged)
    current_level = profile.level
    current_xp = profile.experience_points
    xp_for_current_level = xp_for_level(current_level)
    xp_for_next_level = xp_for_level(current_level + 1)
    xp_in_level = current_xp - xp_for_current_level
    xp_needed_for_level_up = xp_for_next_level - xp_for_current_level
    xp_percentage = round((xp_in_level / xp_needed_for_level_up) * 100) if xp_needed_for_level_up > 0 else 0
    
    # 5. Determine Rank (unchanged)
    rank = "Bronze"
    if current_level >= 10: rank = "Silver"
    if current_level >= 20: rank = "Gold"
    if current_level >= 30: rank = "Platinum"
    sub_rank_tier = (current_level % 10)
    if sub_rank_tier < 3: sub_rank = "III"
    elif sub_rank_tier < 7: sub_rank = "II"
    else: sub_rank = "I"
    full_rank = f"{rank} {sub_rank}"

    # 6. Calculate Stats (placeholders)
    tournaments_participated = 5
    wins = 2
    win_streak = 1

    # 7. Pass all data to the template
    return render_template(
        'Tournament.html',
        active_page='tournament',
        profile=profile,
        xp_percentage=xp_percentage,
        xp_for_next_level=xp_for_next_level,
        full_rank=full_rank,
        tournaments_participated=tournaments_participated,
        wins=wins,
        win_streak=win_streak,
        all_user_challenges=all_user_challenges,
        earned_badges=earned_badges
    )

@app.route('/challenges/start/<int:user_challenge_id>', methods=['POST'])
def start_challenge(user_challenge_id):
    profile = UserProfile.query.first()
    if not profile: # Add this check
        flash("User profile not found. Please run the seed script.", 'danger')
        return redirect(url_for('tournament'))
        
    user_challenge = UserChallenge.query.filter_by(id=user_challenge_id, user_id=profile.id).first_or_404()

    if profile.level >= user_challenge.challenge.level_requirement:
        user_challenge.status = 'active'
        user_challenge.started_at = datetime.utcnow() # Track start time
        db.session.commit()
        flash(f"Challenge '{user_challenge.challenge.title}' started! Good luck!", 'success')
    else:
        flash("You do not meet the level requirement for this challenge.", 'danger')
        
    return redirect(url_for('tournament'))

@app.route('/challenges/complete/<int:user_challenge_id>', methods=['POST'])
def complete_challenge(user_challenge_id):
    profile = UserProfile.query.first()
    if not profile: # Add this check
        flash("User profile not found.", 'danger')
        return redirect(url_for('tournament'))

    user_challenge = UserChallenge.query.filter_by(id=user_challenge_id, user_id=profile.id).first_or_404()

    if user_challenge.status in ['active', 'unlocked']:
        user_challenge.status = 'completed'
        challenge = user_challenge.challenge

        if challenge.is_user_created:
            profile.level += 1
            flash(f"Custom challenge '{challenge.title}' completed! You've been promoted to Level {profile.level}!", 'success')
        else:
            xp_reward = challenge.xp_reward
            profile.experience_points += xp_reward
            flash(f"Challenge '{challenge.title}' completed! You earned {xp_reward} XP!", 'success')

        xp_for_next_level = xp_for_level(profile.level + 1)
        if not challenge.is_user_created and profile.experience_points >= xp_for_next_level:
            profile.level += 1
            flash(f"Congratulations! You've reached Level {profile.level}!", 'info')

        if challenge.is_milestone_challenge and challenge.awards_badge_id:
            already_earned = UserBadge.query.filter_by(user_id=profile.id, badge_id=challenge.awards_badge_id).first()
            if not already_earned:
                new_user_badge = UserBadge(user_id=profile.id, badge_id=challenge.awards_badge_id)
                db.session.add(new_user_badge)
                flash(f"New Badge Unlocked: {challenge.badge_to_award.name}!", 'success')
        
        milestone_challenge = Challenge.query.filter(
            Challenge.is_milestone_challenge == True,
            Challenge.level_requirement == profile.level
        ).first()

        if milestone_challenge:
            existing_link = UserChallenge.query.filter_by(user_id=profile.id, challenge_id=milestone_challenge.id).first()
            if not existing_link:
                new_milestone_link = UserChallenge(user_id=profile.id, challenge_id=milestone_challenge.id, status='unlocked')
                db.session.add(new_milestone_link)
                flash(f"A new Milestone Challenge is available: {milestone_challenge.title}!", 'info')
        
        db.session.commit()
    else:
        flash("This challenge is not currently active.", 'warning')

    return redirect(url_for('tournament'))

@app.route('/challenges/create', methods=['POST'])
def create_challenge():
    profile = UserProfile.query.first()
    if not profile:
        flash("User profile not found.", 'danger')
        return redirect(url_for('tournament'))
    
    title = request.form.get('title')
    task_details = request.form.get('task_details')
    level_req = request.form.get('level_requirement', type=int)
    xp_reward = request.form.get('xp_reward', type=int)

    if not all([title, task_details, level_req, xp_reward]):
        flash('All fields are required to create a challenge.', 'danger')
        return redirect(url_for('tournament'))

    new_challenge = Challenge(
        title=title,
        task_details=task_details,
        level_requirement=level_req,
        xp_reward=xp_reward,
        is_user_created=True,
        user_id=profile.id
    )
    db.session.add(new_challenge)
    db.session.flush() 
    
    user_challenge_link = UserChallenge(user_id=profile.id, challenge_id=new_challenge.id, status='unlocked')
    db.session.add(user_challenge_link)
    
    db.session.commit()
    flash('Your custom challenge has been created!', 'success')
    return redirect(url_for('tournament'))

@app.route('/challenges/edit/<int:challenge_id>', methods=['GET', 'POST'])
def edit_challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    profile = UserProfile.query.first()
    if not profile:
        flash("User profile not found.", 'danger')
        return redirect(url_for('tournament'))

    if not challenge.is_user_created or challenge.user_id != profile.id:
        flash('You do not have permission to edit this challenge.', 'danger')
        return redirect(url_for('tournament'))

    if request.method == 'POST':
        challenge.title = request.form.get('title')
        challenge.task_details = request.form.get('task_details')
        challenge.level_requirement = request.form.get('level_requirement', type=int)
        challenge.xp_reward = request.form.get('xp_reward', type=int)
        db.session.commit()
        flash('Your challenge has been updated.', 'success')
        return redirect(url_for('tournament'))

    return render_template('edit_challenge.html', challenge=challenge, active_page='tournament')

@app.route('/challenges/delete/<int:challenge_id>', methods=['POST'])
def delete_challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    profile = UserProfile.query.first()
    if not profile:
        flash("User profile not found.", 'danger')
        return redirect(url_for('tournament'))

    if not challenge.is_user_created or challenge.user_id != profile.id:
        flash('You do not have permission to delete this challenge.', 'danger')
        return redirect(url_for('tournament'))
    
    UserChallenge.query.filter_by(challenge_id=challenge.id).delete()
    db.session.delete(challenge)
    db.session.commit()
    flash('Your custom challenge has been deleted.', 'success')
    return redirect(url_for('tournament'))

#-----------------------------------------------

# --- ADD THIS CODE TO app.py ---

# --- Add this configuration line with the other app.config settings ---
# This line creates a dedicated upload folder for motivation content
app.config['MOTIVATION_UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads', 'motivation')

# --- Make sure the motivation upload folder exists ---
if not os.path.exists(app.config['MOTIVATION_UPLOAD_FOLDER']):
    os.makedirs(app.config['MOTIVATION_UPLOAD_FOLDER'])


# --- MOTIVATION SECTION START ---

@app.route('/motivation')
def motivation():
    user = UserProfile.query.first()
    if not user:
        flash("User profile not found. Please initialize the application.", 'danger')
        return redirect(url_for('index'))

    # Handle category filtering
    category_filter = request.args.get('category', 'all')
    
    query = MotivationItem.query.filter_by(user_id=user.id)
    
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
        
    all_items = query.order_by(MotivationItem.is_favorite.desc(), MotivationItem.id.desc()).all()
    
    # Get all unique categories for the filter buttons
    all_categories = db.session.query(MotivationItem.category).filter_by(user_id=user.id).distinct().all()
    categories = [cat[0] for cat in all_categories]
    
    return render_template(
        'Motivation.html', 
        active_page='motivation',
        motivation_items=all_items,
        categories=categories,
        active_category=category_filter
    )

@app.route('/motivation/add', methods=['POST'])
def add_motivation_item():
    user = UserProfile.query.first()
    if not user:
        flash('User profile not found.', 'danger')
        return redirect(url_for('motivation'))

    title = request.form.get('title')
    category = request.form.get('category')
    description = request.form.get('description')
    author = request.form.get('author')
    source_url = request.form.get('source_url')

    if not all([title, category]):
        flash('Title and Category are required.', 'danger')
        return redirect(url_for('motivation'))

    new_item = MotivationItem(
        title=title,
        category=category,
        description=description,
        author=author,
        source_url=source_url,
        user_id=user.id
    )

    # Handle file upload
    file = request.files.get('cover_image')
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(app.config['MOTIVATION_UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        # Store the relative path for use in url_for()
        new_item.cover_image_path = os.path.join('uploads', 'motivation', unique_filename)

    db.session.add(new_item)
    db.session.commit()
    flash('New motivational content added!', 'success')
    return redirect(url_for('motivation'))

@app.route('/motivation/delete/<int:item_id>', methods=['POST'])
def delete_motivation_item(item_id):
    item_to_delete = MotivationItem.query.get_or_404(item_id)

    # Delete associated image file from the server if it exists
    if item_to_delete.cover_image_path:
        try:
            full_path = os.path.join('static', item_to_delete.cover_image_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as e:
            print(f"Error deleting file {item_to_delete.cover_image_path}: {e}")

    db.session.delete(item_to_delete)
    db.session.commit()
    flash('Motivational item deleted.', 'success')
    return redirect(url_for('motivation'))

@app.route('/motivation/toggle_favorite/<int:item_id>', methods=['POST'])
def toggle_motivation_favorite(item_id):
    item = MotivationItem.query.get_or_404(item_id)
    item.is_favorite = not item.is_favorite
    db.session.commit()
    
    if item.is_favorite:
        flash(f'"{item.title}" added to favorites.', 'success')
    else:
        flash(f'"{item.title}" removed from favorites.', 'info')
        
    return redirect(request.referrer or url_for('motivation'))

# --- MOTIVATION SECTION END ---

# --- VIDEOS SECTION START ---

@app.route('/videos')
def videos():
    user = UserProfile.query.first()
    if not user:
        flash("User profile not found.", 'danger')
        return redirect(url_for('index'))

    category_filter = request.args.get('category', 'all')
    
    query = Video.query.filter_by(user_id=user.id)
    
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
        
    all_videos = query.order_by(Video.upload_date.desc()).all()
    
    all_categories = db.session.query(Video.category).filter_by(user_id=user.id).distinct().all()
    categories = [cat[0] for cat in all_categories]
    
    return render_template(
        'videos.html', 
        active_page='videos',
        videos=all_videos,
        categories=categories,
        active_category=category_filter
    )

@app.route('/videos/upload', methods=['POST'])
def upload_video():
    user = UserProfile.query.first()
    if not user:
        flash('User profile not found.', 'danger')
        return redirect(url_for('videos'))

    title = request.form.get('title')
    category = request.form.get('category')
    description = request.form.get('description')
    file = request.files.get('video_file')

    if not all([title, category, file]):
        flash('Title, Category, and a video file are required.', 'danger')
        return redirect(url_for('videos'))

    if file.filename == '':
        flash('No selected file.', 'danger')
        return redirect(url_for('videos'))

    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    video_full_path = os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], unique_filename)
    
    try:
        file.save(video_full_path)

        # --- Video Processing using ffmpeg-python ---
        
        # 1. Probe video to get metadata
        probe = ffmpeg.probe(video_full_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        duration_in_seconds = video_stream['duration']
        duration_str = format_duration(duration_in_seconds)

        # 2. Generate Thumbnail (at the 1-second mark)
        unique_thumbnail_name = f"{os.path.splitext(unique_filename)[0]}.jpg"
        thumbnail_full_path = os.path.join(app.config['THUMBNAIL_UPLOAD_FOLDER'], unique_thumbnail_name)
        
        (
            ffmpeg
            .input(video_full_path, ss=1)
            .output(thumbnail_full_path, vframes=1)
            .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        )
        relative_thumbnail_path = os.path.join('uploads', 'thumbnails', unique_thumbnail_name)

        # 3. Get File Size
        size_in_bytes = os.path.getsize(video_full_path)
        size_in_mb = round(size_in_bytes / (1024 * 1024), 2)

    except Exception as e:
        # Clean up the saved video file if processing fails
        if os.path.exists(video_full_path):
            os.remove(video_full_path)
        print(f"FFmpeg Error: {e}") # Log the actual error for debugging
        flash(f'An error occurred during video processing. Please ensure FFmpeg is installed and the video format is supported.', 'danger')
        return redirect(url_for('videos'))

    new_video = Video(
        title=title,
        category=category,
        description=description,
        file_path=os.path.join('uploads', 'videos', unique_filename),
        thumbnail_path=relative_thumbnail_path,
        duration=duration_str,
        size_mb=size_in_mb,
        user_id=user.id
    )

    db.session.add(new_video)
    db.session.commit()
    flash('Video uploaded and processed successfully!', 'success')
    return redirect(url_for('videos'))


@app.route('/videos/delete/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    video_to_delete = Video.query.get_or_404(video_id)

    # Delete the video and thumbnail files
    for file_path in [video_to_delete.file_path, video_to_delete.thumbnail_path]:
        if file_path:
            try:
                full_path = os.path.join('static', file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

    db.session.delete(video_to_delete)
    db.session.commit()
    flash('Video deleted successfully.', 'success')
    return redirect(url_for('videos'))

@app.route('/videos/data/<int:video_id>')
def get_video_data(video_id):
    video = Video.query.get_or_404(video_id)
    return {
        'title': video.title,
        'description': video.description,
        'file_url': url_for('static', filename=video.file_path)
    }

# --- VIDEOS SECTION END ---

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
