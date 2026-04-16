from flask import Blueprint
from app.controllers.user_controller import *
from app.middleware.is_auth import is_auth

user_bp = Blueprint("users", __name__)

@user_bp.route("/", methods=["GET"])
def getUsers():
    return get_users()

@user_bp.route("/", methods=["POST"])
def createUsers():
    return create_user()

@user_bp.route("/", methods=["PUT"])
def updateUsers():
    return update_user()

@user_bp.route("/", methods=["DELETE"])
def deleteUsers():
    return delete_user()