# test_diary_entry_routes.py
# TC008 - Create a diary entry with valid data
def test_create_diary_entry_success(client):
    login_response = client.post('/login', json={'email': 'testuser@example.com', 'password': 'testpass'})
    assert login_response.status_code == 200

    token = login_response.get_json()['data']['access_token']

    headers = {'Authorization': f'Bearer {token}'}

    response = client.post('/predict_details', headers=headers,
                           json={'text': 'Today was a productive day, I felt great!',
                               'selected_dairy_date': '2024-09-15'})

    assert response.status_code == 200

    data = response.get_json()

    assert 'data' in data
    assert 'prediction' in data['data']
    assert 'probability' in data['data']
    assert isinstance(data['data']['probability'], dict)


#TC009 - Get a list of all diary entries for the user
def test_get_all_diary_entries(client):
    # Step 1: Perform a login to get a JWT token
    login_response = client.post('/login', json={'email': 'testuser@example.com', 'password': 'testpass'})
    assert login_response.status_code == 200

    token = login_response.get_json()['data']['access_token']

    # Step 2: Use the token in the headers for authenticated requests
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Step 3: Create a couple of diary entries for testing
    client.post('/predict_details', headers=headers, json={
        'text': 'Today was a productive day!',
        'selected_dairy_date': '2024-09-15'
    })
    client.post('/predict_details', headers=headers, json={
        'text': 'I felt very anxious today.',
        'selected_dairy_date': '2024-09-16'
    })

    # Step 4: Retrieve all diary entries
    response = client.get('/diary-reports', headers=headers)

    # Assert that the request was successful
    assert response.status_code == 200

    # Extract and validate the data
    data = response.get_json()
    assert 'data' in data
    assert isinstance(data['data'], list)  # Ensure the response contains a list of entries
    assert len(data['data']) >= 2
