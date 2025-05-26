import os
import pathlib
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from PIL import Image
import io
import uuid
import json
import re
from user_agents import parse

load_dotenv()

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Configure PostgreSQL database
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Use the URL from environment variable
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback to a default URL - this is just for development
    print("Warning: DATABASE_URL not found in environment variables. Using default connection.")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://soheilhosseini@localhost/calorie_counter'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Log SQL queries for debugging
db = SQLAlchemy(app)

# Define database models
class Analysis(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    image_filename = db.Column(db.String(255), nullable=True)
    analysis_result = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Food-specific data
    food_items = db.Column(db.Text, nullable=True)  # JSON string of identified food items
    
    # User device information
    ip_address = db.Column(db.String(50), nullable=True)  # User's IP address
    user_agent = db.Column(db.Text, nullable=True)  # Browser/device info
    device_type = db.Column(db.String(20), nullable=True)  # web, mobile, tablet, etc.
    
    # Location data
    location = db.Column(db.String(255), nullable=True)  # Location info (with permission)
    latitude = db.Column(db.Float, nullable=True)  # Latitude coordinate
    longitude = db.Column(db.Float, nullable=True)  # Longitude coordinate
    
    def to_dict(self):
        return {
            'id': self.id,
            'analysis_result': self.analysis_result,
            'created_at': self.created_at.isoformat(),
            'food_items': self.food_items,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'device_type': self.device_type,
            'location': self.location,
            'coordinates': {'lat': self.latitude, 'lng': self.longitude} if self.latitude and self.longitude else None
        }


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

@app.route('/upload', methods=['POST'])
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
            
            # Extract food items from the analysis result
            food_items = None
            try:
                # Use regex to extract food items from the response
                # Try different patterns since the response format might vary
                food_match = re.search(r'Identified food:\s*\[(.+?)\]', analysis_result)
                
                if not food_match:
                    # Try alternative pattern without brackets
                    food_match = re.search(r'Identified food:\s*(.+?)\.\s*Estimated', analysis_result)
                
                if food_match:
                    food_items_text = food_match.group(1).strip()
                    # Remove any brackets if they exist
                    food_items_text = food_items_text.strip('[]')
                    # Convert to list and clean up
                    food_items_list = [item.strip() for item in food_items_text.split(',')]
                    food_items = json.dumps(food_items_list)  # Store as JSON string
                    print(f"Extracted food items: {food_items}")
                else:
                    print("Could not extract food items using regex patterns")
            except Exception as e:
                print(f"Error extracting food items: {e}")
            
            # Get user device information
            ip_address = request.remote_addr
            user_agent_string = request.headers.get('User-Agent', '')
            device_type = 'unknown'
            
            # Parse user agent to determine device type
            try:
                user_agent = parse(user_agent_string)
                if user_agent.is_mobile:
                    device_type = 'mobile'
                elif user_agent.is_tablet:
                    device_type = 'tablet'
                elif user_agent.is_pc:
                    device_type = 'web'
                else:
                    device_type = 'other'
            except Exception as e:
                print(f"Error parsing user agent: {e}")
            
            # Get image dimensions
            image_dimensions = f"{img.width}x{img.height}" if img else None
            
            # Save the analysis result to the database
            try:
                # Create a new Analysis record with additional information
                new_analysis = Analysis(
                    image_filename=file.filename,
                    analysis_result=analysis_result,
                    food_items=food_items,
                    ip_address=ip_address,
                    user_agent=user_agent_string,
                    device_type=device_type
                    # Note: location, latitude, and longitude would be populated
                    # when the user explicitly provides permission and location data
                )
                
                # Add to database and commit
                db.session.add(new_analysis)
                db.session.commit()
                
                print(f"Analysis saved to database with ID: {new_analysis.id}")
                
                # Return the analysis result along with the database ID and extracted food items
                return jsonify({
                    'analysis': analysis_result,
                    'id': new_analysis.id,
                    'created_at': new_analysis.created_at.isoformat(),
                    'food_items': json.loads(food_items) if food_items else None,
                    'device_info': {
                        'type': device_type,
                        'ip': ip_address
                    }
                })
                
            except Exception as db_error:
                print(f"Error saving to database: {db_error}")
                # If database save fails, still return the analysis to the user
                return jsonify({'analysis': analysis_result, 'warning': 'Result not saved to database'})

        except Exception as e:
            print(f"Error processing image or calling Gemini API: {e}")
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Unknown error'}), 500

# Endpoint to get all past analyses
@app.route('/analyses', methods=['GET'])
def get_analyses():
    try:
        # Get all analyses ordered by creation date (newest first)
        analyses = Analysis.query.order_by(Analysis.created_at.desc()).all()
        
        # Convert to list of dictionaries
        analyses_list = [analysis.to_dict() for analysis in analyses]
        
        return jsonify({
            'analyses': analyses_list,
            'count': len(analyses_list)
        })
    except Exception as e:
        print(f"Error retrieving analyses: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoint to get a specific analysis by ID
@app.route('/analyses/<analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    try:
        # Find the analysis by ID
        analysis = Analysis.query.get(analysis_id)
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        return jsonify(analysis.to_dict())
    except Exception as e:
        print(f"Error retrieving analysis: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoint to update location data for an analysis
@app.route('/analyses/<analysis_id>/location', methods=['POST'])
def update_location(analysis_id):
    try:
        # Find the analysis by ID
        analysis = Analysis.query.get(analysis_id)
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Get location data from request
        data = request.json
        if not data:
            return jsonify({'error': 'No location data provided'}), 400
            
        # Update location fields
        if 'location' in data:
            analysis.location = data['location']
        if 'latitude' in data and 'longitude' in data:
            analysis.latitude = data['latitude']
            analysis.longitude = data['longitude']
            
        # Save changes
        db.session.commit()
        
        return jsonify({
            'message': 'Location data updated successfully',
            'analysis': analysis.to_dict()
        })
    except Exception as e:
        print(f"Error updating location data: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Make sure to create a .env file in this directory with your GEMINI_API_KEY
    # e.g., GEMINI_API_KEY=YOUR_ACTUAL_API_KEY
    if not os.getenv("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY is not set. The application will run but API calls will fail.")
        print("Please create a .env file in the 'backend' directory with your GEMINI_API_KEY.")
        print("Example .env file content: GEMINI_API_KEY=YOUR_API_KEY_HERE")
    
    # Check database connection and create tables
    try:
        with app.app_context():
            # Test connection
            db.session.execute(db.text("SELECT 1"))
            print("Successfully connected to the PostgreSQL database.")
            
            # Check if we need to add new columns to the analysis table
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('analysis')] if 'analysis' in inspector.get_table_names() else []
            
            # If table exists but new columns are missing, alter the table
            if 'analysis' in inspector.get_table_names() and 'food_items' not in columns:
                print("Migrating database schema to add new columns...")
                # Add new columns to the existing table
                with db.engine.connect() as conn:
                    # Add food_items column
                    if 'food_items' not in columns:
                        conn.execute(db.text("ALTER TABLE analysis ADD COLUMN food_items TEXT"))
                    # Add device info columns
                    if 'ip_address' not in columns:
                        conn.execute(db.text("ALTER TABLE analysis ADD COLUMN ip_address VARCHAR(50)"))
                    if 'user_agent' not in columns:
                        conn.execute(db.text("ALTER TABLE analysis ADD COLUMN user_agent TEXT"))
                    if 'device_type' not in columns:
                        conn.execute(db.text("ALTER TABLE analysis ADD COLUMN device_type VARCHAR(20)"))
                    # Add location columns
                    if 'location' not in columns:
                        conn.execute(db.text("ALTER TABLE analysis ADD COLUMN location VARCHAR(255)"))
                    if 'latitude' not in columns:
                        conn.execute(db.text("ALTER TABLE analysis ADD COLUMN latitude FLOAT"))
                    if 'longitude' not in columns:
                        conn.execute(db.text("ALTER TABLE analysis ADD COLUMN longitude FLOAT"))
                    conn.commit()
                print("Database schema migration completed successfully.")
            else:
                # Create tables if they don't exist
                db.create_all()
                print("Database tables created successfully.")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Database tables: {tables}")
            
            # Verify columns in analysis table
            if 'analysis' in tables:
                columns = [col['name'] for col in inspector.get_columns('analysis')]
                print(f"Columns in analysis table: {columns}")
            
            
    except Exception as e:
        print(f"\nError with database: {e}")
        print("\nPlease check that:")
        print("1. PostgreSQL is running")
        print("2. The database 'calorie_counter' exists")
        print("3. Your user has permission to access the database")
        print("4. The DATABASE_URL in your .env file is correct")
        print("\nYou might need to modify your connection string to include your username and password.")
        print("Example: DATABASE_URL=\"postgresql://username:password@localhost/calorie_counter\"")
        print("\nThe application will start, but database functionality will not work.")
    
    app.run(debug=True, port=5001) # Changed port to 5001 to avoid common conflicts
