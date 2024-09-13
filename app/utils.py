from flask import jsonify


def create_response(data=None, message='', status=200):
    response = {
        'status': status,
        'message': message,
        'data': data
    }
    return jsonify(response), status


def create_error(message='', status=400):

    response = {
        'status': status,
        'message': message,
        'data': None
    }
    return jsonify(response), status





