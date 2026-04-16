from app.models.user import *
from app.db import db
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.validator import validate_required

def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

def create_user():
    data = request.get_json()
    error = validate_required(data, ["name", "email", "password"])
    if error:
        return error
    user = User(
        name=data['name'],
        email=data['email'],
        password=generate_password_hash(data['password']),
    )

    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

def update_user():
    data = request.get_json()
    user = User.query.get(data['id'])
    user.name = data['name']
    user.email = data['email']
    user.password = data['password']
    db.session.commit()
    return jsonify(user.json()), 200

def delete_user():
    data = request.get_json()
    user = User.query.get(data['id'])
    db.session.delete(user)
    db.session.commit()
    return jsonify(user.json()), 200