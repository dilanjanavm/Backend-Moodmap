from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.prediction import predict_emotions, get_prediction_proba
from app.utils import create_response, create_error

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, EmotionReport, DiaryEntry  # Import db from models, not directly from app
from datetime import datetime
from openai import OpenAI
from datetime import timedelta
from collections import defaultdict
import json
import re
import os
from dotenv import load_dotenv

main = Blueprint('main', __name__)
load_dotenv()
users_db = {}

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@main.route('/register', methods=['POST'])
def register():
    print(request.json)
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Username, email, and password are required'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)

    # Create a new user instance
    new_user = User(username=username, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@main.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    print('loged')
    # Query the user from the database
    user = User.query.filter_by(email=email).first()

    if not user:
        return create_error(message='Invalid email or password', status=401)

    print(user.password, password)
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity={'email': user.email}, expires_delta=timedelta(hours=24))
        return create_response(data={'access_token': access_token}, message='Login successful', status=200)
    else:
        return create_error(message='Invalid email or password', status=401)



@main.route('/predict_details', methods=['POST'])
@jwt_required()
def predict():
    data = request.get_json()
    text = data.get('text', '')
    selected_dairy_date = data.get('selected_dairy_date', '')  # Date from the frontend

    if not text:
        return create_error(message='Text input is required', status=400)

    if not selected_dairy_date:
        return create_error(message='Selected dairy date is required', status=400)

    # Parse the selected diary date
    try:
        diary_date = datetime.strptime(selected_dairy_date, '%Y-%m-%d').date()
    except ValueError:
        return create_error(message='Invalid date format. Use YYYY-MM-DD.', status=400)

    # Perform emotion prediction
    prediction = predict_emotions(text)
    probability = get_prediction_proba(text)

    # Identify the main emotion and its percentage
    main_emotion = max(probability, key=probability.get)
    main_emotion_percentage = probability[main_emotion]

    # Get the current user from the JWT token
    current_user_email = get_jwt_identity()['email']
    user = User.query.filter_by(email=current_user_email).first()

    # Create a new DiaryEntry instance
    new_entry = DiaryEntry(user_id=user.id, content=text, main_emotion=main_emotion,
                           main_emotion_percentage=main_emotion_percentage, created_at=diary_date
                           # Save the selected diary date
                           )
    db.session.add(new_entry)
    db.session.commit()

    # Save the emotion reports
    for emotion_name, emotion_percentage in probability.items():
        new_emotion_report = EmotionReport(diary_id=new_entry.id, emotion_name=emotion_name,
                                           emotion_percentage=emotion_percentage)
        db.session.add(new_emotion_report)

    db.session.commit()

    # Prepare the response data
    response_data = {'id': new_entry.id, 'prediction': main_emotion, 'probability': probability}

    return create_response(data=response_data, message='Prediction successful', status=200)


@main.route('/diary-reports', methods=['GET'])
@jwt_required()
def get_diary_reports():
    current_user_email = get_jwt_identity()['email']

    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return create_error(message="User not found", status=404)

    diary_entries = DiaryEntry.query.filter_by(user_id=user.id).all()

    reports = []
    for entry in diary_entries:
        emotion_reports = EmotionReport.query.filter_by(diary_id=entry.id).all()
        report = {'id': entry.id, 'content': entry.content, 'main_emotion': entry.main_emotion,
                  'main_emotion_percentage': entry.main_emotion_percentage,
                  'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M:%S'), 'emotion_reports': [
                {'emotion_name': emotion.emotion_name, 'emotion_percentage': emotion.emotion_percentage} for emotion in
                emotion_reports]}
        reports.append(report)

    return create_response(data=reports, message="Diary reports fetched successfully", status=200)




# @main.route('/get_recommendations', methods=['POST'])
# def get_recommendations():
#     # Extract the user input from the request
#     user_input = request.json.get('user_input')
#
#     if not user_input:
#         return jsonify({"message": "User input is required"}), 400
#
#     # Define your OpenAI GPT API request using the new `openai.ChatCompletion.create()` method
#     chat_completion = client.chat.completions.create(
#         messages=[{"role": "user", "content": "give a introduction about New York", }], max_tokens=100, temperature=0.7,
#         model="gpt-3.5-turbo", )
#
#     # Extract the text from the API response
#     print(chat_completion)
#
#     return jsonify({"recommendation": ''})
#


def generate_gpt_description(data_type, data):
    prompt_created = convert_emotion_data_to_prompt(data)

    prompt = f"Here is the {data_type} data about emotions: {prompt_created}. Can you provide a summary or description of the emotional state in a paragraph?write using simple english.and limit your pargaph into 800 words. "

    try:

        completion = client.chat.completions.create(model="gpt-4o", messages=[
            {"role": "system", "content": f"Summarize the given {data_type} emotion data."},
            {"role": "user", "content": prompt}])

        print(completion)
        return completion.choices[0].message.content

    except KeyError as e:
        return f"Error generating description: Key {str(e)} missing in response"
    except Exception as e:
        return f"Error generating description: {str(e)}"


def convert_emotion_data_to_prompt(emotion_data):
    """Converts detailed or overall emotion data into a readable prompt format for GPT."""
    prompt = "Here is the emotion data over a period of time:\n\n"

    for emotion, entries in emotion_data.items():
        prompt += f"Emotion: {emotion.capitalize()}\n"

        # Handle detailed reports (list of date-value pairs)
        if isinstance(entries, list):
            for entry in entries:
                date = entry['date']
                value = entry['value']
                prompt += f"- On {date}, the value was {value:.5f}.\n"
        # Handle overall report (float values)
        elif isinstance(entries, float):
            prompt += f"- The average value was {entries:.5f}.\n"

        prompt += "\n"

    return prompt


def generate_gpt_suggestions(main_emotions):
    """Generates suggestions for managing emotions based on the main detected emotions."""
    global suggestions_temp
    print(main_emotions)
    prompt = f"""
        Act like an expert psychologist with 20 years of experience in emotional well-being and mental health. You specialize in creating practical, evidence-based strategies for managing emotions and promoting mental health.

        Objective: You are provided with the following emotions: {', '.join(main_emotions)}. Your task is to create 10 highly actionable and detailed suggestions that individuals can use to improve their emotional well-being and manage the listed emotions effectively. 

        Instructions:
        1. Each suggestion should focus on real-world application, providing clear steps that individuals can follow.
        2. Use simple language to ensure accessibility for all audiences, but ensure depth and detail to offer meaningful solutions.
        
        can you give this suggestion as a array object
         Output Format (JSON):
    [
       {{
          "topic": "Practice Mindfulness Meditation",
          "explanation": "Mindfulness meditation allows you to become more aware of your emotions in a non-judgmental way. This practice helps manage emotions like anxiety or sadness by focusing on the present moment.",
          "steps": "Start with 5 minutes a day, focusing on your breath."
       }},
       {{
          "topic": "Engage in Creative Expression",
          "explanation": "Creative activities such as drawing or journaling can provide an emotional outlet and help reduce stress by externalizing your emotions in a constructive way.",
          "steps": "Set aside 30 minutes for drawing or journaling daily."
       }},
       ...other suggestions
    ]
        """
    try:
        completion = client.chat.completions.create(model="gpt-4o", messages=[
            {"role": "system", "content": "You are an expert in mental health and well-being."},
            {"role": "user", "content": prompt}])

        print(completion)
        response_text = completion['choices'][0]['message']['content']

        # Log the raw response for debugging purposes
        print('=======================================')
        print(response_text)
        print('=======================================')

        json_array_match = re.search(r'(\[\s*{.*}\s*\])', response_text, re.DOTALL)
        if json_array_match:
            json_array_str = json_array_match.group(1)

            # Parse the JSON string into a Python list
            suggestions_temp = json.loads(json_array_str)
            print('=======================================')
            print(suggestions_temp)
            print('=======================================')

        return suggestions_temp



    except Exception as e:
        return f"Error generating suggestions: {str(e)}"


@main.route('/emotion-reports', methods=['POST'])
@jwt_required()
def get_emotion_reports_by_date_range():
    data = request.get_json()

    # Get date range from the request
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')

    if not start_date_str or not end_date_str:
        return jsonify({'message': 'Start date and end date are required'}), 400

    # Parse the dates
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    current_user_email = get_jwt_identity()

    if not current_user_email:
        return jsonify({'message': 'Unauthorized access'}), 401

    # Get current user from the JWT token
    current_user_email = get_jwt_identity()['email']
    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Query diary entries within the specified date range for the current user
    diary_entries = DiaryEntry.query.filter(DiaryEntry.user_id == user.id, DiaryEntry.created_at >= start_date,
                                            DiaryEntry.created_at <= end_date).all()

    if not diary_entries:
        return jsonify({'message': 'No diary entries found for the given date range'}), 404

    # Initialize a dictionary to store emotions and their corresponding values
    emotions_data = defaultdict(list)
    overall_emotions = defaultdict(float)
    entry_count = defaultdict(int)  # Track how many times each emotion appears for averaging

    # Loop through each diary entry and its associated emotion reports
    for entry in diary_entries:
        emotion_reports = EmotionReport.query.filter_by(diary_id=entry.id).all()

        for report in emotion_reports:
            # Add to detailed emotion data
            emotions_data[report.emotion_name].append(
                {'date': entry.created_at.strftime('%Y-%m-%d'), 'value': report.emotion_percentage})

            # Add to overall emotion totals
            overall_emotions[report.emotion_name] += report.emotion_percentage
            entry_count[report.emotion_name] += 1

    # Calculate the average percentage for each emotion (overall report)
    overall_report = {}
    for emotion, total_value in overall_emotions.items():
        if entry_count[emotion] > 0:
            average_value = total_value / entry_count[emotion]
            overall_report[emotion] = average_value

    main_emotions = sorted(overall_report, key=overall_report.get, reverse=True)[:3]

    detailed_reports_desc = generate_gpt_description("detailed reports", emotions_data)
    overall_report_desc = generate_gpt_description("overall report", overall_report)
    suggestions = generate_gpt_suggestions(main_emotions)

    return jsonify({'detailed_reports': emotions_data, 'overall_report': overall_report,
                    'detailed_reports_desc': detailed_reports_desc, 'overall_report_desc': overall_report_desc,
                    'suggestions': suggestions}), 200
