from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
from flask_cors import CORS
import hashlib
import jwt
import os
from ml_service import ml_service

# Initialize the Flask app and enable CORS for React development
app = Flask(__name__, static_folder='dist', static_url_path='')
CORS(app)

# Set secret key for JWT tokens
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# --- User Data Store (In production, use a proper database) ---
users_db = {
    'admin@bhoomisense.com': {
        'password': hashlib.sha256('admin123'.encode()).hexdigest(),
        'name': 'Admin User',
        'city': 'Delhi',
        'phone': '+91 98765 43210'
    }
}

# --- Global Data Stores ---

# A dictionary to hold the most recent sensor reading for quick access.
latest_sensor_data = {
    'nitrogen': 'N/A',
    'phosphorus': 'N/A',
    'potassium': 'N/A',
    'ph': 'N/A',
    'moisture': 'N/A',
    'ec': 'N/A', # Added from your second example
    'temperature': 'N/A' # Added for completeness
}

# A list to store a history of readings, perfect for creating charts.
sensor_history = []

# --- API Endpoint for the ESP32 Device ---

@app.route('/data', methods=['POST'])
def receive_data():
    """Receives sensor data from the ESP32 and updates the server's state."""
    global latest_sensor_data, sensor_history
    
    if not request.is_json:
        return jsonify(message="Error: Request must be JSON"), 400

    data = request.get_json()
    
    # Safely update all sensor values from the incoming JSON data.
    # .get(key, default) prevents errors if a key is missing.
    for key in latest_sensor_data:
        latest_sensor_data[key] = data.get(key, latest_sensor_data[key])

    # Create a timestamped record for the history log.
    historical_record = latest_sensor_data.copy()
    historical_record['time'] = datetime.now().strftime('%H:%M:%S')
    sensor_history.append(historical_record)

    # To save memory, we only keep the last 200 historical readings.
    if len(sensor_history) > 200:
        sensor_history.pop(0) # Removes the oldest entry

    print(f"Received Data: {latest_sensor_data}")
    return jsonify(message="Data received successfully!"), 200

# --- Authentication Endpoints ---

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        city = data.get('city')
        phone = data.get('phone')
        
        if not all([email, password, name, city, phone]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if email in users_db:
            return jsonify({'error': 'User already exists'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Store user
        users_db[email] = {
            'password': hashed_password,
            'name': name,
            'city': city,
            'phone': phone
        }
        
        # Generate JWT token
        token = jwt.encode({
            'email': email,
            'name': name,
            'city': city,
            'exp': datetime.utcnow().timestamp() + 86400  # 24 hours
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'name': name,
                'city': city,
                'email': email
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if email not in users_db:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if users_db[email]['password'] != hashed_password:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'email': email,
            'name': users_db[email]['name'],
            'city': users_db[email]['city'],
            'exp': datetime.utcnow().timestamp() + 86400  # 24 hours
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'name': users_db[email]['name'],
                'city': users_db[email]['city'],
                'email': email
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/verify', methods=['POST'])
def verify_token():
    """Verify JWT token"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        
        return jsonify({
            'valid': True,
            'user': {
                'name': payload['name'],
                'city': payload['city'],
                'email': payload['email']
            }
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- ML Prediction Endpoint ---

@app.route('/predict', methods=['POST'])
def predict_crops():
    """
    Predict top 5 crops and their yields based on sensor data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate and clean input data
        validated_data = ml_service.validate_input_data(data)
        
        # Get crop type mapping
        crop_type_mapping = ml_service.get_crop_type_mapping()
        
        # Convert crop type if it's a string
        if isinstance(validated_data.get('Crop_Type'), str):
            crop_type_str = validated_data['Crop_Type'].lower()
            validated_data['Crop_Type'] = crop_type_mapping.get(crop_type_str, 0)
        
        # Make predictions
        predictions = ml_service.predict_top_5_crops_and_yields(validated_data)
        
        return jsonify(predictions), 200
        
    except Exception as e:
        print(f"Error in crop prediction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml-status', methods=['GET'])
def get_ml_status():
    """
    Check if ML models are loaded and ready
    """
    model_info = ml_service.get_model_info()
    return jsonify(model_info), 200

# --- API Endpoint for the React Frontend ---

@app.route('/api/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """
    Provides all necessary data for the React dashboard in a single API call.
    This includes the latest readings and a recent history for charts.
    """
    return jsonify({
        'latest': latest_sensor_data,
        'history': sensor_history[-50:]  # Send the last 50 readings for charts
    })

# --- Routes for Serving the React Application ---

@app.route('/')
def serve_react_app():
    """Serves the main index.html file of the React application."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def catch_all(path):
    """
    This catch-all route ensures that refreshing on any page (e.g., /charts)
    within your React app works correctly by always serving the main index.html.
    React Router will then handle displaying the correct component.
    """
    return send_from_directory(app.static_folder, 'index.html')

# --- Main Execution ---

if __name__ == '__main__':
    print("Flask server starting...")
    print(" - Serving React app from the 'dist' folder.")
    print(" - ESP32 should POST data to: http://<your_ip_address>:5000/data")
    print(" - React app will fetch from: http://<your_ip_address>:5000/api/dashboard-data")
    # Set host='0.0.0.0' to make the server accessible on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)

    