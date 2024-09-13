from flask import Blueprint, request, jsonify

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/login', methods=['POST'])
def login():
    # Authentication logic here
    return jsonify({'message': 'Logged in successfully'})