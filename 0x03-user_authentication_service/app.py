#!/usr/bin/env python3
"""
This Is The User Authentication Service Application
"""
from flask import Flask
from flask import (
    abort, jsonify,
    request, make_response, redirect
)

from auth import Auth

AUTH = Auth()

app = Flask(__name__)


@app.errorhandler(401)
def unauthorized(error) -> str:
    """
    the unauthorized error handler
    """
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def unauthorized(error) -> str:
    """
    the forbidden error handler
    """
    return jsonify({"error": "Forbidden"}), 403


@app.route("/")
def home() -> str:
    """
    home route
    """
    return jsonify({"message": "Bienvenue"})


@app.route('/users', methods=['POST'], strict_slashes=False)
def users() -> str:
    """registers a new user route
    """
    email, password = request.form.get('email'), request.form.get('password')
    try:
        user = AUTH.register_user(email, password)
    except ValueError:
        return jsonify({"message": "email already registered"}), 400
    return jsonify({"email": "%s" % email, "message": "user created"})


@app.route("/sessions", methods=["POST"], strict_slashes=False)
def login():
    """
    logs in a valid user and set a session ID
    """
    email, password = request.form.get('email'), request.form.get('password')
    if AUTH.valid_login(email=email, password=password):
        res = make_response(
            jsonify({"email": "%s" % email, "message": "logged in"}))
        res.set_cookie("session_id", AUTH.create_session(email))
        return res
    abort(401)


@app.route("/sessions", methods=["DELETE"], strict_slashes=False)
def logout():
    """
    logs out a login user
    """
    session_id = request.cookies.get("session_id")
    user = AUTH.get_user_from_session_id(session_id)
    if user is not None:
        AUTH.destroy_session(user.id)
        return redirect("/")
    abort(403)


@app.route("/profile", strict_slashes=False)
def profile():
    """
    gets and returns json data of user profile
    """
    session_id = request.cookies.get("session_id")
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        return jsonify({"email": user.email})
    abort(403)


@app.route("/reset_password", methods=["POST"], strict_slashes=False)
def get_reset_password_token():
    """
    resets password route
    """
    email = request.form.get("email")
    try:
        reset_token = AUTH.get_reset_password_token(email)
    except ValueError:
        abort(403)
    return jsonify({"email": "%s" % email, "reset_token": "%s" % reset_token})


@app.route("/reset_password", methods=["PUT"], strict_slashes=False)
def update_password():
    """
    updates password route
    """
    email = request.form.get("email")
    reset_token = request.form.get("reset_token")
    new_password = request.form.get("new_password")
    try:
        AUTH.update_password(reset_token, new_password)
        return jsonify({"email": "%s" % email, "message": "Password updated"})
    except Exception:
        pass
    abort(403)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")
