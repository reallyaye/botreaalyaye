from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app, db, login_manager
from app.models import User, UserData, Workout, WorkoutHistory, Goal, Achievement
import os
import random
from datetime import datetime, timedelta

# Мотивационные цитаты
MOTIVATION_QUOTES = [
    {"text": "Сила не приходит от физических возможностей. Она приходит от несгибаемой воли.", "author": "Махатма Ганди"},
    {"text": "Неважно, как медленно ты идешь, главное — не останавливаться.", "author": "Конфуций"},
    {"text": "Самая тяжелая атлетика в мире — это поднять свою задницу с дивана.", "author": "Неизвестный автор"},
    {"text": "Если ты хочешь добиться успеха, которого никогда не имел, тебе придется делать то, что никогда не делал.", "author": "Коко Шанель"},
    {"text": "Боль временна. Результат — навсегда.", "author": "Неизвестный автор"}
]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Получение данных для панели управления
    user_activities = WorkoutHistory.query.filter_by(user_id=current_user.id).order_by(WorkoutHistory.date.desc()).limit(5).all()
    user_goals = Goal.query.filter_by(user_id=current_user.id).all()
    
    # Статистика пользователя
    stats = {
        'workouts_completed': WorkoutHistory.query.filter_by(user_id=current_user.id).count(),
        'calories_burned': sum(wh.calories for wh in WorkoutHistory.query.filter_by(user_id=current_user.id).all()),
        'workout_minutes': sum(wh.duration for wh in WorkoutHistory.query.filter_by(user_id=current_user.id).all())
    }
    
    # Случайная мотивационная цитата
    motivation_quote = random.choice(MOTIVATION_QUOTES)
    
    return render_template('dashboard.html', 
                          user_activities=user_activities,
                          user_goals=user_goals,
                          stats=stats,
                          motivation_quote=motivation_quote)

@app.route('/workouts')
@login_required
def workouts():
    # Получение всех доступных тренировок
    available_workouts = Workout.query.all()
    return render_template('workouts.html', workouts=available_workouts)

@app.route('/stats')
@login_required
def stats():
    # Статистика пользователя
    stats = {
        'workouts_completed': WorkoutHistory.query.filter_by(user_id=current_user.id).count(),
        'calories_burned': sum(wh.calories for wh in WorkoutHistory.query.filter_by(user_id=current_user.id).all()),
        'workout_minutes': sum(wh.duration for wh in WorkoutHistory.query.filter_by(user_id=current_user.id).all()),
        'achievements': Achievement.query.filter_by(user_id=current_user.id, unlocked=True).count()
    }
    
    # История тренировок
    workout_history = WorkoutHistory.query.filter_by(user_id=current_user.id).order_by(WorkoutHistory.date.desc()).all()
    
    return render_template('stats.html', stats=stats, workout_history=workout_history)

@app.route('/profile')
@login_required
def profile():
    # Данные пользователя
    user_data = UserData.query.filter_by(user_id=current_user.id).first()
    if not user_data:
        user_data = UserData(user_id=current_user.id)
        db.session.add(user_data)
        db.session.commit()
    
    # Цели пользователя
    user_goals = Goal.query.filter_by(user_id=current_user.id).all()
    
    # Достижения пользователя
    achievements = Achievement.query.filter_by(user_id=current_user.id).all()
    
    # Статистика пользователя
    stats = {
        'workouts_completed': WorkoutHistory.query.filter_by(user_id=current_user.id).count(),
        'achievements': Achievement.query.filter_by(user_id=current_user.id, unlocked=True).count()
    }
    
    # Настройки пользователя
    user_settings = {
        'email_notifications': True,
        'push_notifications': False,
        'language': 'ru',
        'theme': 'light'
    }
    
    return render_template('profile.html', 
                          user_data=user_data,
                          user_goals=user_goals,
                          achievements=achievements,
                          stats=stats,
                          user_settings=user_settings)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Неверное имя пользователя или пароль', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=remember)
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return redirect(url_for('register'))
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Пользователь с таким именем уже существует', 'danger')
            return redirect(url_for('register'))
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Пользователь с таким email уже существует', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='sha256'),
            created_at=datetime.now()
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти в систему.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username')
    email = request.form.get('email')
    weight = request.form.get('weight')
    height = request.form.get('height')
    age = request.form.get('age')
    gender = request.form.get('gender')
    activity_level = request.form.get('activity_level')
    
    # Обновление основных данных пользователя
    current_user.username = username
    current_user.email = email
    
    # Обновление дополнительных данных пользователя
    user_data = UserData.query.filter_by(user_id=current_user.id).first()
    if not user_data:
        user_data = UserData(user_id=current_user.id)
        db.session.add(user_data)
    
    if weight:
        user_data.weight = float(weight)
    if height:
        user_data.height = int(height)
    if age:
        user_data.age = int(age)
    if gender:
        user_data.gender = gender
    if activity_level:
        user_data.activity_level = float(activity_level)
    
    # Обработка загрузки аватара
    if 'avatar' in request.files:
        avatar_file = request.files['avatar']
        if avatar_file.filename != '':
            filename = secure_filename(avatar_file.filename)
            avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            avatar_file.save(avatar_path)
            current_user.avatar = filename
    
    db.session.commit()
    flash('Профиль успешно обновлен', 'success')
    return redirect(url_for('profile'))

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not check_password_hash(current_user.password, current_password):
        flash('Неверный текущий пароль', 'danger')
        return redirect(url_for('profile'))
    
    if new_password != confirm_password:
        flash('Новые пароли не совпадают', 'danger')
        return redirect(url_for('profile'))
    
    current_user.password = generate_password_hash(new_password, method='sha256')
    db.session.commit()
    
    flash('Пароль успешно изменен', 'success')
    return redirect(url_for('profile'))

@app.route('/update_settings', methods=['POST'])
@login_required
def update_settings():
    # Обновление настроек пользователя
    # В реальном приложении здесь будет сохранение в базу данных
    flash('Настройки успешно обновлены', 'success')
    return redirect(url_for('profile'))

@app.route('/add_goal', methods=['GET', 'POST'])
@login_required
def add_goal():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        target_value = request.form.get('target_value')
        target_date = request.form.get('target_date')
        
        new_goal = Goal(
            user_id=current_user.id,
            name=name,
            description=description,
            target_value=float(target_value) if target_value else 0,
            current_value=0,
            target_date=datetime.strptime(target_date, '%Y-%m-%d') if target_date else None,
            created_at=datetime.now()
        )
        
        db.session.add(new_goal)
        db.session.commit()
        
        flash('Цель успешно добавлена', 'success')
        return redirect(url_for('profile'))
    
    return render_template('add_goal.html')

@app.route('/edit_goal/<int:goal_id>', methods=['GET', 'POST'])
@login_required
def edit_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    
    if goal.user_id != current_user.id:
        abort(403)
    
    if request.method == 'POST':
        goal.name = request.form.get('name')
        goal.description = request.form.get('description')
        goal.target_value = float(request.form.get('target_value')) if request.form.get('target_value') else 0
        goal.current_value = float(request.form.get('current_value')) if request.form.get('current_value') else 0
        goal.target_date = datetime.strptime(request.form.get('target_date'), '%Y-%m-%d') if request.form.get('target_date') else None
        
        db.session.commit()
        
        flash('Цель успешно обновлена', 'success')
        return redirect(url_for('profile'))
    
    return render_template('edit_goal.html', goal=goal)

@app.route('/delete_goal/<int:goal_id>', methods=['POST'])
@login_required
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    
    if goal.user_id != current_user.id:
        abort(403)
    
    db.session.delete(goal)
    db.session.commit()
    
    flash('Цель успешно удалена', 'success')
    return redirect(url_for('profile'))

@app.route('/workout_details/<int:workout_id>')
@login_required
def workout_details(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    return render_template('workout_details.html', workout=workout)

@app.route('/start_workout/<int:workout_id>')
@login_required
def start_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    return render_template('start_workout.html', workout=workout)

@app.route('/create_workout', methods=['GET', 'POST'])
@login_required
def create_workout():
    if request.method == 'POST':
        # Логика создания новой тренировки
        flash('Тренировка успешно создана', 'success')
        return redirect(url_for('workouts'))
    
    return render_template('create_workout.html')

@app.route('/reset_password')
def reset_password():
    return render_template('reset_password.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
