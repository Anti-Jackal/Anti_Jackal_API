from flask import Blueprint, request, jsonify
from models import db, User
from jose import jwt
from datetime import datetime, timedelta
from flask import current_app

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    print(username, password)
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = jwt.encode({
        'sub': user.id,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({"token": token, "is_admin": user.is_admin}), 200


@auth_bp.route('/admin/users', methods=['GET'])
def get_users():
    token = request.headers.get('Authorization').split()[1]
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.get(payload['sub'])

        if not user.is_admin:
            return jsonify({"message": "Access denied"}), 403

        users = User.query.all()
        users_data = [{"id": u.id, "username": u.username, "balance": u.balance} for u in users]

        return jsonify(users_data), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.JWTError:
        return jsonify({"message": "Invalid token"}), 401


@auth_bp.route('/admin/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    token = request.headers.get('Authorization').split()[1]
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.get(payload['sub'])

        if not user.is_admin:
            return jsonify({"message": "Access denied"}), 403

        user_to_delete = User.query.get(user_id)
        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()
            return jsonify({"message": "User deleted successfully"}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.JWTError:
        return jsonify({"message": "Invalid token"}), 401
