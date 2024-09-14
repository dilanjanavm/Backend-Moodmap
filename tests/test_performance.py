import time


# TC015 - Test API Response Time Under Normal Load
def test_predict_details_performance(client):
    # Step 1: Perform a login to get a JWT token
    login_response = client.post('/login', json={'email': 'testuser@example.com', 'password': 'testpass'})
    assert login_response.status_code == 200
    token = login_response.get_json()['data']['access_token']

    headers = {'Authorization': f'Bearer {token}'}

    # Step 2: Start timer and send a request to /predict_details
    start_time = time.time()
    response = client.post('/predict_details', headers=headers,
                           json={'text': 'I am feeling great today!', 'selected_dairy_date': '2024-09-17'})
    end_time = time.time()

    # Step 3: Assert response status and time
    assert response.status_code == 200
    response_time = end_time - start_time
    assert response_time < 0.5


# TC016 - Test System Performance With Large Payloads
def test_predict_details_large_payload(client):
    # Step 1: Perform a login to get a JWT token
    login_response = client.post('/login', json={'email': 'testuser@example.com', 'password': 'testpass'})
    assert login_response.status_code == 200
    token = login_response.get_json()['data']['access_token']

    headers = {'Authorization': f'Bearer {token}'}

    # Step 2: Send a large payload to /predict_details
    large_text = "I am feeling great today! " * 1000  # Large payload
    response = client.post('/predict_details', headers=headers,
                           json={'text': large_text, 'selected_dairy_date': '2024-09-17'})

    # Step 3: Assert response
    assert response.status_code == 200
