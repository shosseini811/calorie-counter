import os
import pathlib
import json
import google.generativeai as genai
from flask import Flask, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from dotenv import load_dotenv
from PIL import Image
import io
import secrets
from datetime import timedelta
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from requests_oauthlib import OAuth2Session
from werkzeug.middleware.proxy_fix import ProxyFix

# Set environment variable to allow OAuth over HTTP (for development only)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

load_dotenv()

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(16)
# Set session cookie parameters for better security and persistence
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
CORS(app, supports_credentials=True) # Enable CORS for all routes with credentials support

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_AUTH_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email, name, picture):
        self.id = id
        self.email = email
        self.name = name
        self.picture = picture

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    if 'users' not in session:
        return None
    users = session['users']
    if user_id in users:
        user_data = users[user_id]
        return User(user_id, user_data['email'], user_data['name'], user_data['picture'])
    return None

# Configure the Gemini API key
try:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file or environment variables.")
    genai.configure(api_key=gemini_api_key)
except ValueError as e:
    print(f"Error: {e}")
    # You might want to exit or handle this more gracefully in a production app
    # For this simplified version, we'll let it proceed but API calls will fail.

# Initialize the Gemini model
# Using gemini-2.5-flash-preview-05-20 for improved image analysis capabilities
# This is a newer model with better performance for food image analysis
model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

# Google OAuth routes
@app.route('/login')
def login():
    # Create a new OAuth2Session with an exact redirect URI
    redirect_uri = url_for('login_callback', _external=True)
    google = OAuth2Session(GOOGLE_CLIENT_ID, redirect_uri=redirect_uri,
                           scope=['openid', 'email', 'profile'])
    
    # Get authorization URL
    authorization_url, state = google.authorization_url(GOOGLE_AUTH_BASE_URL,
                                                       access_type="offline",
                                                       prompt="select_account")
    
    # Store the state for later validation and make session permanent
    session.permanent = True
    session['oauth_state'] = state
    print("Authorization URL:", authorization_url)
    print("Redirect URI:", redirect_uri)  # Log the redirect URI for debugging
    print("OAuth State:", state)  # Log the state for debugging
    return jsonify({
        'authorization_url': authorization_url
    })

@app.route('/login/callback')
def login_callback():
    # Get the authorization code
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Validate state
    if state != session.get('oauth_state'):
        return jsonify({'error': 'Invalid state parameter'}), 401
    
    # Create OAuth2Session with the same exact redirect URI as in login
    redirect_uri = url_for('login_callback', _external=True)
    google = OAuth2Session(GOOGLE_CLIENT_ID, redirect_uri=redirect_uri)
    
    # Log for debugging
    print("Callback URL:", request.url)
    print("Redirect URI:", redirect_uri)
    
    try:
        # Fetch token
        token = google.fetch_token(
            GOOGLE_TOKEN_URL,
            client_secret=GOOGLE_CLIENT_SECRET,
            authorization_response=request.url
        )
        
        # Get user info
        resp = google.get(GOOGLE_USERINFO_URL)
        user_info = resp.json()
        
        # Initialize users dict in session if not exists
        if 'users' not in session:
            session['users'] = {}
        
        # Create or update user
        user_id = user_info['sub']
        user = User(
            id=user_id,
            email=user_info.get('email'),
            name=user_info.get('name'),
            picture=user_info.get('picture')
        )
        
        # Store user in session
        session['users'][user_id] = {
            'email': user.email,
            'name': user.name,
            'picture': user.picture
        }
        
        # Log in the user
        login_user(user)
        
        # Redirect to the frontend application
        return redirect('http://localhost:8081/index.html')
        
    except Exception as e:
        print(f"Error processing OAuth callback: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/user')
def get_user():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name,
                'picture': current_user.picture
            }
        })
    else:
        return jsonify({
            'authenticated': False
        })

@app.route('/logout')
def logout():
    logout_user()
    return jsonify({'success': True})

@app.route('/upload', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            # Read image bytes
            img_bytes = file.read()
            img = Image.open(io.BytesIO(img_bytes))

            # Prepare the image for the Gemini API
            # The API expects a list of parts, where each part can be text or image data.
            image_parts = [
                {
                    "mime_type": f"image/{img.format.lower()}" if img.format else "image/jpeg", # Ensure format is always 'image/format'
                    "data": img_bytes
                }
            ]

            # Create the prompt for Gemini
            prompt_parts = [
                image_parts[0],
                "\n\nAnalyze this image and provide an estimated calorie count for the food items visible. "
                "Also, list the food items you identify. Be concise. "
                "Format your response as: 'Identified food: [list of items]. Estimated calories: [number] kcal.'"
            ]

            # Configure generation parameters
            generation_config = {
                "temperature": 0,  # Lower temperature for more deterministic responses
                "top_p": 0.95,
                "top_k": 0,
                "max_output_tokens": 1024,
            }
            
            # Call the Gemini API with streaming enabled
            print("Sending request to Gemini API...")
            response_stream = model.generate_content(
                prompt_parts,
                generation_config=generation_config,
                stream=True  # Enable streaming
            )
            
            # Collect the streamed response
            analysis_result = ""
            print("Receiving streamed response from Gemini API:")
            for chunk in response_stream:
                if chunk.text:
                    analysis_result += chunk.text
                    print(chunk.text, end="")
            
            print("\nCompleted receiving response from Gemini API.")
            
            # If we somehow got an empty response, provide a fallback message
            if not analysis_result:
                analysis_result = "Could not extract text from Gemini response."
                print("Warning: Empty response received from Gemini API.")
                # Log more details for debugging
                print(f"Response stream details: {response_stream}")

            return jsonify({'analysis': analysis_result})

        except Exception as e:
            print(f"Error processing image or calling Gemini API: {e}")
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Unknown error'}), 500

if __name__ == '__main__':
    # Make sure to create a .env file in this directory with your GEMINI_API_KEY
    # e.g., GEMINI_API_KEY=YOUR_ACTUAL_API_KEY
    if not os.getenv("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY is not set. The application will run but API calls will fail.")
        print("Please create a .env file in the 'backend' directory with your GEMINI_API_KEY.")
        print("Example .env file content: GEMINI_API_KEY=YOUR_API_KEY_HERE")
    app.run(debug=True, port=5001) # Changed port to 5001 to avoid common conflicts
