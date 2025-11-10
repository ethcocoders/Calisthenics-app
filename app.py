import json
from datetime import datetime, time, timedelta
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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

# --- Initialize Extensions ---
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# --- Define Database Model ---
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


# --- Define StickyNote Model ---
class StickyNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    color = db.Column(db.String(20), nullable=False, default='yellow')

    def __repr__(self):
        return f'<StickyNote {self.title}>'

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


# --- Placeholder Routes for Other Pages ---

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', active_page='index')

@app.route('/goals')
def goals():
    return render_template('Goals.html', active_page='goals')

@app.route('/plan')
def plan():
    return render_template('Plan.html', active_page='plan')


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

@app.route('/health')
def health():
    return render_template('Health.html', active_page='health')

@app.route('/motivation')
def motivation():
    return render_template('Motivation.html', active_page='motivation')

@app.route('/tournament')
def tournament():
    return render_template('Tournament.html', active_page='tournament')

@app.route('/videos')
def videos():
    return render_template('videos.html', active_page='videos')


# --- Run the Application ---
if __name__ == '__main__':
    app.run(debug=True)
