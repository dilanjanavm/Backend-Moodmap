import pytest
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
from flask import Flask


@pytest.fixture
def client():
    app = create_app('TestingConfig')
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create all tables

            # Add a sample user to the database for login tests
            user = User(username='testuser', email='testuser@example.com', password=generate_password_hash('testpass'))
            db.session.add(user)
            db.session.commit()

        yield client

        # Teardown: Clean up the database after each test
        with app.app_context():
            db.drop_all()


#TC001
def test_register_user(client):
    response = client.post('/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpassword'
    })

    # Check that the registration was successful
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'User registered successfully'

    # Check that the new user exists in the database
    user = User.query.filter_by(email='newuser@example.com').first()
    assert user is not None
    assert user.username == 'newuser'


#TC002
def test_register_existing_user(client):
    # Try registering a user with an existing email
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })

    # Check that the registration fails
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'User already exists'


#TC003
def test_login_success(client):
    response = client.post('/login', json={
        'email': 'testuser@example.com',
        'password': 'testpass'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data['data']
    assert data['message'] == 'Login successful'


#TC004
def test_login_invalid_password(client):
    response = client.post('/login', json={
        'email': 'testuser@example.com',
        'password': 'wrongpassword'
    })

    assert response.status_code == 401
    data = response.get_json()
    assert data['message'] == 'Invalid email or password'


def test_protected_route_without_token(client):
    response = client.get('/diary-reports')  # Replace with an actual protected route

    assert response.status_code == 401
    data = response.get_json()
    assert data['message'] == 'Unauthorized'

