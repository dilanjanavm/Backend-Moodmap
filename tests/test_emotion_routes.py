import pytest
from unittest.mock import patch
from datetime import datetime

# TC005: Test Emotion Prediction Success
# tests/test_emotion_prediction.py
def test_predict_emotion_success(client):
    # Step 1: Perform a login to get a JWT token
    login_response = client.post('/login', json={'email': 'testuser@example.com', 'password': 'testpass'})

    # Debugging: Print the login response to see the issue
    print(login_response.get_json())
    assert login_response.status_code == 200

    token = login_response.get_json()['data']['access_token']

    # Step 2: Use the token in the headers to authenticate the /predict_details request
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Step 3: Send the request to predict emotions
    response = client.post('/predict_details', headers=headers, json={
        'text': 'I am feeling very happy today!',
        'selected_dairy_date': '2024-09-15'
    })


def test_predict_emotion_invalid_text(client):
    # Step 1: Perform a login to get a JWT token
    login_response = client.post('/login', json={'email': 'testuser@example.com', 'password': 'testpass'})
    assert login_response.status_code == 200

    token = login_response.get_json()['data']['access_token']

    # Step 2: Use the token in the headers to authenticate the /predict_details request
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Step 3: Send the request with missing 'text' field
    response = client.post('/predict_details', headers=headers, json={
        'text': '',  # Invalid empty text
        'selected_dairy_date': '2024-09-15'
    })

    # Assert that the response returned an error
    assert response.status_code == 400

    # Extract response data
    data = response.get_json()

    # Check the error message for missing text input
    assert data['message'] == 'Text input is required'


def test_predict_emotion_missing_jwt(client):
    response = client.post('/predict_details', json={
        'text': 'I am feeling very happy today!',
        'selected_dairy_date': '2024-09-15'
    })

    assert response.status_code == 401

    data = response.get_json()

    assert data['message'] == 'Unauthorized'


