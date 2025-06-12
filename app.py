from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
import numpy as np
from google import genai
from google.genai import types
from joblib import load
from dotenv import load_dotenv
import os
import json
import zipfile
from ulid import ULID
import csv
from collections import defaultdict
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from symptoms import symptom_dict
from config import config

# Load symptom dictionary 
symptoms_list=symptom_dict.keys()

# Define User class - kept outside create_app
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

def create_app(config_name='default'):
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration from config.py
    app.config.from_object(config[config_name])
    
    # Initialize Flask-Bcrypt
    bcrypt = Bcrypt(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    
    # Set up logging
    if not app.debug and not app.testing:
        # Ensure log directory exists
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/drishti-dps.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('DRISHTI-DPS startup')
    
    # Configure MongoDB
    try:
        client = MongoClient(app.config['MONGO_URI'])
        db = client['dps']
        user_collection = db.dps_collection
        app.logger.info('MongoDB connection established')
    except Exception as e:
        app.logger.error(f'MongoDB connection error: {str(e)}')
        client = None
        db = None
        user_collection = None
    
    # Initialize Google Generative AI
    try:
        genai_client = genai.Client(api_key=app.config['GOOGLE_API_KEY'])
        app.logger.info('Google Generative AI client initialized')
    except Exception as e:
        app.logger.error(f'Google Generative AI initialization error: {str(e)}')
        genai_client = None
    
    # Load your model
    try:
        # Extracting model 
        zip_file = 'Model_Compressed.zip'
        extract_to = './data'
        os.makedirs(extract_to, exist_ok=True)
        
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            
        model = load('./data/DRISHTI_DPS.joblib')
        app.logger.info('Model loaded successfully')
    except Exception as e:
        app.logger.error(f'Error loading model: {str(e)}')
        model = None
    
    # Store key objects in app context for access in routes
    app.config['MODEL'] = model
    app.config['GENAI_CLIENT'] = genai_client
    app.config['USER_COLLECTION'] = user_collection
    app.config['DB'] = db
    app.config['MONGO_CLIENT'] = client
    
    # Define session_id as None initially
    session_id = None
    
    # Load user callback
    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)
    
    # Add health check endpoint
    @app.route('/health')
    def health_check():
        health = {
            'status': 'ok',
            'model_loaded': app.config['MODEL'] is not None,
            'database_connected': app.config['MONGO_CLIENT'] is not None,
            'genai_client_initialized': app.config['GENAI_CLIENT'] is not None
        }
        return jsonify(health)
    
    # Define utility functions
    def generate_full_prompt(user_input, context):
        system_prompt = f"You are a NER model which will understand a patient's ailments and categorise it into the following symptoms: {list(symptom_dict.keys())}.\n\nMake sure to analyse the entire list instead of assuming anything initially. Only display the observed symptoms with no explanations. Output symptoms should be a single line string separated by commas"
        
        full_prompt = f"{system_prompt}\n\nPatient: {user_input}\nAI:"
        return full_prompt

    def get_response(user_input):
        full_prompt = generate_full_prompt(user_input, [])
        
        try:
            response = app.config['GENAI_CLIENT'].models.generate_content(
                model="gemini-2.0-flash", 
                contents=full_prompt
            )
            app.logger.info('Successfully received response from Gemini')
            response_text = response.text
            return response_text
        except Exception as e:
            app.logger.error(f'Error getting response from Gemini: {str(e)}')
            return "Error processing your request"

    def get_predicted_value(patient_symptoms, model):
        input_vector = np.zeros(len(symptom_dict.keys()))
        for userSymptom in patient_symptoms:
            cleaned_symptom = userSymptom.lower().strip()
            if cleaned_symptom in symptom_dict:
                input_vector[symptom_dict[cleaned_symptom]] = 1
        predicted_disease = model.predict([input_vector])[0]
        return predicted_disease

    def append_to_csv(user_prompt, model_output, userID):
        try :
            # Ensure directory exists
            os.makedirs("./data/users", exist_ok=True)

            file_path = f"./data/users/{userID}.csv"

            # Open the CSV file in append mode
            with open(file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                
                # Write the header if the file is empty
                file.seek(0, 2)  # Move to the end of the file
                if file.tell() == 0:
                    writer.writerow(['Session ID', 'Date', 'User Prompt', 'Model Output'])
                current_date = datetime.now().strftime('%Y-%m-%d')
                # Write the new row
                writer.writerow([str(session_id), current_date, user_prompt, model_output])
            app.logger.info(f'Appended entry for user {userID} to {file_path}')
        except Exception as e:
            app.logger.error(f'Error appending to CSV: {str(e)}')

    def group_entries_by_session(csv_file_path):
        grouped_entries = defaultdict(list)
        
        if(os.path.exists(csv_file_path) == False):
            return []
        
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                session_id = row['Session ID']
                user_prompt = row['User Prompt']
                model_output = row['Model Output']
                date = row['Date']
                
                # Append the entry to the list for the corresponding session ID
                grouped_entries[session_id].append([date, user_prompt, model_output])
        
        # Convert the grouped entries to a list of lists
        grouped_list = list(grouped_entries.values())
        
        return grouped_list

    # Define routes
    @app.route('/')
    def home():
        if 'user_id' not in session:
            return redirect('/login')
        
        # Fetch user details
        user_id = session['user_id']
        user_name = session['user']

        return render_template('index.html', user_name=user_name)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        nonlocal session_id
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            user = app.config['USER_COLLECTION'].find_one({'email': email})
            if user and bcrypt.check_password_hash(user['password'], password):
                session['user_id'] = str(user['_id'])
                session['user'] = str(user['username'])
                # Generate a new ULID
                session_id = str(ULID())
                login_user(User(str(user['_id'])))
                flash('Login successful!', 'success')
                return redirect('/')  # Redirect to homepage
            else:
                flash('Incorrect email or password', 'error')

        return render_template('login.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            repassword = request.form.get('repassword')

            # Basic validation
            if not (username and email and password and repassword):
                flash('Please fill all fields')
                return render_template('signup.html')

            if password != repassword:
                flash('Passwords do not match')
                return render_template('signup.html')

            existing_user = app.config['USER_COLLECTION'].find_one({'username': username})
            if existing_user:
                flash('Username already exists')
                return render_template('signup.html')

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            app.config['USER_COLLECTION'].insert_one({
                'username': username, 
                'email': email, 
                'password': hashed_password
            })
            flash('Account created successfully! Please login.')
            return redirect('/login')

        return render_template('signup.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        session.clear()
        return redirect('/login')
        

    @app.route('/predict', methods=['POST'])
    def predict():
        if 'user_id' not in session:
            return redirect('/login')

        try:
            userID = session['user_id']
            user_input = request.form.get('prompt')
            if not user_input:
                return jsonify({'error': 'No input provided'}), 400
            
            response = get_response(user_input)
            app.logger.info(f'Generated response for user {userID}')
            
            response = response.split("\n")[0]
            userSymptoms = response.split(",")
            
            disease = get_predicted_value(userSymptoms, app.config['MODEL'])

            output = "You may have " + disease
            append_to_csv(user_input, output, userID)

            return output
        
        except Exception as e:
            app.logger.error(f'Error in prediction: {str(e)}')
            return jsonify({'error': str(e)}), 500

    @app.route('/get_user_data', methods=['GET'])
    def get_user_data():
        if 'user_id' in session:
            user_id = session['user_id']
            csv_file_path = f'./data/users/{user_id}.csv'
            
            # Group entries by session ID
            grouped_entries = group_entries_by_session(csv_file_path)
            
            # Return the grouped entries as JSON
            return jsonify(grouped_entries)
        else:
            return jsonify({"error": "User not logged in"}), 401
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f'Server error: {str(e)}')
        return render_template('500.html'), 500
        
    return app

# Create the app instance
app = create_app(os.getenv('FLASK_ENV', 'default'))

if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'production':
        # Use Waitress for Windows production
        from waitress import serve
        serve(app, host='0.0.0.0', port=8080)
    else:
        # Development server
        app.run(debug=True, host='0.0.0.0', port=8080)