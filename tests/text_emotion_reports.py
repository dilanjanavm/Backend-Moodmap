from datetime import datetime, timedelta


# Test Case for /emotion-reports endpoint
# TC010 - Get Emotion Reports for a Valid Date Range (JWT required)
def test_get_emotion_reports_success(client):
    # Step 1: Perform a login to get a JWT token
    login_response = client.post('/login', json={'email': 'testuser@example.com', 'password': 'testpass'})

    # Debugging: Print the login response to see the JWT token
    print(login_response.get_json())
    assert login_response.status_code == 200

    token = login_response.get_json()['data']['access_token']

    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Step 2: Create a diary entry in the database (since /emotion-reports relies on diary data)
    diary_entry_response = client.post('/predict_details', headers=headers, json={
        'text': 'I am feeling very happy today!',
        'selected_dairy_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # Yesterday's date
    })

    # Ensure the diary entry creation was successful
    assert diary_entry_response.status_code == 200

    # Step 3: Send the request to get emotion reports by a valid date range
    response = client.post('/emotion-reports', headers=headers, json={
        'start_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),  # Two days ago
        'end_date': datetime.now().strftime('%Y-%m-%d')  # Today's date
    })

    # Step 4: Assert that the request was successful
    assert response.status_code == 200
    data = response.get_json()

    # Step 5: Validate that the response contains the detailed and overall reports
    assert 'detailed_reports' in data
    assert 'overall_report' in data
    assert 'suggestions' in data

    # Ensure that the detailed reports contain at least one entry
    assert len(data['detailed_reports']) > 0
    assert len(data['overall_report']) > 0
    assert len(data['suggestions']) > 0


# TC011: Test Emotion Reports - Missing Start and End Date
def test_get_emotion_reports_missing_dates(client):
    # Step 1: Perform a login to get a JWT token
    login_response = client.post('/login', json={'email': 'testuser@example.com', 'password': 'testpass'})
    assert login_response.status_code == 200

    token = login_response.get_json()['data']['access_token']

    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Step 2: Send the request to /emotion-reports without providing start and end date
    response = client.post('/emotion-reports', headers=headers, json={})

    # Step 3: Assert that the request returns a 400 error for missing dates
    assert response.status_code == 400
    data = response.get_json()

    # Step 4: Validate the error message
    assert 'message' in data
    assert data['message'] == 'Start date and end date are required'


# TC012: Test Emotion Reports - Invalid Date Format
def test_get_emotion_reports_invalid_date_format(client):
    # Step 1: Perform a login to get a JWT token
    login_response = client.post('/login', json={'email': 'testuser@example.com', 'password': 'testpass'})
    assert login_response.status_code == 200

    token = login_response.get_json()['data']['access_token']

    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Step 2: Send the request to /emotion-reports with invalid date format
    response = client.post('/emotion-reports', headers=headers, json={
        'start_date': '15-09-2024',  # Wrong date format
        'end_date': '2024/09/15'  # Another wrong format
    })

    # Step 3: Assert that the request returns a 400 error for invalid date format
    assert response.status_code == 400
    data = response.get_json()

    # Step 4: Validate the error message
    assert 'message' in data
    assert data['message'] == 'Invalid date format. Use YYYY-MM-DD.'


# TC013: Test Emotion Reports - No Diary Entries Found
def test_get_emotion_reports_no_entries_found(client):
    # Step 1: Perform a login to get a JWT token
    login_response = client.post('/login', json={'email': 'testuser@example.com', 'password': 'testpass'})
    assert login_response.status_code == 200

    token = login_response.get_json()['data']['access_token']

    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Step 2: Send the request to /emotion-reports with a date range where no entries exist
    response = client.post('/emotion-reports', headers=headers, json={
        'start_date': '2020-01-01',  # Date far in the past
        'end_date': '2020-01-31'
    })

    # Step 3: Assert that the request returns a 404 error for no diary entries found
    assert response.status_code == 404
    data = response.get_json()

    # Step 4: Validate the error message
    assert 'message' in data
    assert data['message'] == 'No diary entries found for the given date range'


# TC014: Test Emotion Reports - Unauthorized Access (Missing JWT)
def test_get_emotion_reports_unauthorized(client):
    # Step 1: Send the request to /emotion-reports without a JWT token
    response = client.post('/emotion-reports', json={
        'start_date': '2024-09-01',
        'end_date': '2024-09-15'
    })

    assert response.status_code == 401
    data = response.get_json()

    assert 'message' in data
    assert data['message'] == 'Unauthorized'
