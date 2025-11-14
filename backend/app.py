from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_cors import CORS
import jwt
import time
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskly.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

db = SQLAlchemy(app)

# Модели
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#6c757d')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=1)
    deadline = db.Column(db.DateTime, nullable=True)
    reminder = db.Column(db.DateTime, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Создаем таблицы
with app.app_context():
    db.create_all()
    print("✅ База данных создана")

# JWT функции
def create_token(user_id):
    payload = {'user_id': user_id, 'exp': time.time() + 24 * 3600}
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

def get_user_from_token():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token:
        user_id = verify_token(token)
        if user_id:
            return User.query.get(user_id)
    return None

@app.route('/')
def home():
    return jsonify({'message': 'Taskly API is running!'})

# Аутентификация
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        hashed_password = generate_password_hash(data.get('password'))
        user = User(username=data.get('username'), password_hash=hashed_password)
        
        db.session.add(user)
        db.session.commit()
        
        # Создаем стандартные категории для нового пользователя
        categories = [
            {'name': 'Работа', 'color': '#dc3545'},
            {'name': 'Личное', 'color': '#198754'},
            {'name': 'Здоровье', 'color': '#0dcaf0'},
            {'name': 'Обучение', 'color': '#ffc107'},
            {'name': 'Дом', 'color': '#6f42c1'}
        ]
        
        for cat_data in categories:
            category = Category(
                name=cat_data['name'],
                color=cat_data['color'],
                user_id=user.id
            )
            db.session.add(category)
        
        db.session.commit()
        
        token = create_token(user.id)
        return jsonify({
            'token': token, 
            'user_id': user.id,
            'username': user.username,
            'message': 'Registration successful'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration error: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        user = User.query.filter_by(username=data.get('username')).first()
        
        if user and check_password_hash(user.password_hash, data.get('password')):
            token = create_token(user.id)
            return jsonify({
                'token': token, 
                'user_id': user.id,
                'username': user.username,
                'message': 'Login successful'
            })
        
        return jsonify({'error': 'Invalid username or password'}), 401
    
    except Exception as e:
        return jsonify({'error': f'Login error: {str(e)}'}), 500

# Категории
@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        categories = Category.query.filter_by(user_id=user.id).all()
        categories_data = []
        
        for category in categories:
            task_count = Task.query.filter_by(category_id=category.id, user_id=user.id).count()
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'color': category.color,
                'task_count': task_count,
                'created_at': category.created_at.isoformat()
            })
        
        return jsonify(categories_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['POST'])
def create_category():
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Category name is required'}), 400
        
        category = Category(
            name=data['name'],
            color=data.get('color', '#6c757d'),
            user_id=user.id
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category created',
            'category': {
                'id': category.id,
                'name': category.name,
                'color': category.color,
                'task_count': 0,
                'created_at': category.created_at.isoformat()
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Задачи
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Параметры фильтрации
        category_id = request.args.get('category_id', type=int)
        priority = request.args.get('priority', type=int)
        completed = request.args.get('completed', type=str)
        search = request.args.get('search', '')
        
        query = Task.query.filter_by(user_id=user.id)
        
        # Применяем фильтры
        if category_id:
            query = query.filter_by(category_id=category_id)
        if priority:
            query = query.filter_by(priority=priority)
        if completed:
            if completed.lower() == 'true':
                query = query.filter_by(is_completed=True)
            elif completed.lower() == 'false':
                query = query.filter_by(is_completed=False)
        if search:
            query = query.filter(Task.title.ilike(f'%{search}%') | Task.description.ilike(f'%{search}%'))
        
        tasks = query.order_by(Task.created_at.desc()).all()
        
        tasks_data = []
        for task in tasks:
            category = Category.query.get(task.category_id) if task.category_id else None
            tasks_data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'is_completed': task.is_completed,
                'priority': task.priority,
                'deadline': task.deadline.isoformat() if task.deadline else None,
                'reminder': task.reminder.isoformat() if task.reminder else None,
                'category_id': task.category_id,
                'category_name': category.name if category else None,
                'category_color': category.color if category else None,
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat()
            })
        
        return jsonify(tasks_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        if not data or not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        # Парсим даты
        deadline = None
        reminder = None
        
        if data.get('deadline'):
            try:
                deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
            except:
                return jsonify({'error': 'Invalid deadline format'}), 400
        
        if data.get('reminder'):
            try:
                reminder = datetime.fromisoformat(data['reminder'].replace('Z', '+00:00'))
            except:
                return jsonify({'error': 'Invalid reminder format'}), 400
        
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 1),
            deadline=deadline,
            reminder=reminder,
            category_id=data.get('category_id'),
            user_id=user.id
        )
        
        db.session.add(task)
        db.session.commit()
        
        category = Category.query.get(task.category_id) if task.category_id else None
        
        return jsonify({
            'message': 'Task created', 
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'is_completed': task.is_completed,
                'priority': task.priority,
                'deadline': task.deadline.isoformat() if task.deadline else None,
                'reminder': task.reminder.isoformat() if task.reminder else None,
                'category_id': task.category_id,
                'category_name': category.name if category else None,
                'category_color': category.color if category else None,
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat()
            }
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        task = Task.query.filter_by(id=task_id, user_id=user.id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'is_completed' in data:
            task.is_completed = data['is_completed']
        if 'priority' in data:
            task.priority = data['priority']
        if 'category_id' in data:
            task.category_id = data['category_id']
        
        # Обновляем даты
        if 'deadline' in data:
            task.deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00')) if data['deadline'] else None
        if 'reminder' in data:
            task.reminder = datetime.fromisoformat(data['reminder'].replace('Z', '+00:00')) if data['reminder'] else None
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        category = Category.query.get(task.category_id) if task.category_id else None
        
        return jsonify({
            'message': 'Task updated',
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'is_completed': task.is_completed,
                'priority': task.priority,
                'deadline': task.deadline.isoformat() if task.deadline else None,
                'reminder': task.reminder.isoformat() if task.reminder else None,
                'category_id': task.category_id,
                'category_name': category.name if category else None,
                'category_color': category.color if category else None,
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        task = Task.query.filter_by(id=task_id, user_id=user.id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Task deleted'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)