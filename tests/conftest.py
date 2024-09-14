import pytest
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User


@pytest.fixture
def client():
    # Create the application with the testing configuration
    app = create_app('TestingConfig')
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create all tables

            # Add a sample user to the database for login tests
            user = User(username='testuser', email='testuser@example.com', password=generate_password_hash('testpass'))
            db.session.add(user)
            db.session.commit()

            # Debugging: Print user info to verify
            print(f"User created: {user.username}, {user.email}")

        yield client

        # Teardown: Clean up the database after each test
        with app.app_context():
            db.drop_all()
