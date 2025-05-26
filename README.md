# Calorie Counter Desktop App

This is a desktop application built with **Tauri v2** that allows users to upload an image of food and get calorie analysis. The backend, built with Python and Flask, sends images to the Google Gemini API for analysis, which returns estimated calorie counts and identified food items. The application stores analysis results in a PostgreSQL database with Redis caching for improved performance.

## 🎥 Demo

Watch the application in action:

<video src="https://github.com/user-attachments/assets/d1545a09-a26d-4f83-8d29-35bfc93c95c4" controls width="100%"></video>

## Project Structure

```
calorie-counter/
├── backend/
│   ├── app.py            # Flask backend logic
│   ├── requirements.txt  # Python dependencies
│   ├── .env.example      # Example for environment variables (API key)
│   └── .env              # Actual environment variables (you need to create this)
├── frontend/
│   ├── index.html        # Main HTML page
│   ├── style.css         # CSS for styling
│   ├── main.ts           # TypeScript for frontend logic
│   ├── tsconfig.json     # TypeScript compiler options
│   └── dist/             # Compiled JavaScript (main.js will be here after compilation)
├── src-tauri/            # Tauri desktop app configuration
│   ├── src/main.rs       # Rust application entry point
│   ├── Cargo.toml        # Rust dependencies
│   └── tauri.conf.json   # Tauri configuration
├── package.json          # Node.js dependencies for Tauri
└── README.md             # This file
```

## Prerequisites

- Python 3.7+
- Node.js 16+
- Rust (for Tauri)
- PostgreSQL database
- Redis server (optional, for caching)

## Setup Instructions

### 1. Clone the Repository (if applicable)

If you haven't already, clone the project to your local machine.

```bash
# git clone <repository-url>
cd calorie-counter
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Set up your environment variables:

1.  Rename `.env.example` to `.env`.
2.  Open the `.env` file and update the following variables:

    ```
    GEMINI_API_KEY=your_actual_api_key_goes_here
    DATABASE_URL=postgresql://user:password@localhost/calorie_counter
    REDIS_URL=redis://localhost:6379/0
    ADMIN_TOKEN=your_secure_admin_token_here
    ```

    **Important**: 
    - You can obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    - The REDIS_URL should point to your Redis server instance.
    - The ADMIN_TOKEN is used for accessing admin endpoints like cache clearing.

### 3. Frontend Setup

Navigate to the frontend directory:

```bash
cd ../frontend  # If you are in the backend directory
# or cd frontend if you are in the root calorie-counter directory
```

Install TypeScript and a simple HTTP server (if you don't have one globally):

```bash
npm install typescript --save-dev
npm install http-server -g # Or use any other local server you prefer
```

Compile the TypeScript code:

```bash
npx tsc
```

This will compile `main.ts` and output `main.js` into a `dist` folder within the `frontend` directory, as specified in `tsconfig.json`.

### 4. Tauri Setup

Navigate to the root directory:

```bash
cd ..
```

Install Tauri dependencies:

```bash
npm install @tauri-apps/cli @tauri-apps/api
```

### 5. Running the Application

#### 1. Start the Backend Server

Navigate to the `backend` directory and run the Flask app:

```bash
cd backend # if not already there
python app.py
```

The backend server will start, usually on `http://127.0.0.1:5001`.

#### 2. Start the Tauri App

Open a **new terminal window/tab**.

Navigate to the root directory:

```bash
cd ..
```

Run the Tauri app:

```bash
npm run tauri dev
```

This will start the Tauri app in development mode.

## How to Use

1. Click the "Choose File" button to select an image of food from your computer.
2. A preview of the image will be displayed.
3. Click the "Analyze Image" button.
4. Wait for the Gemini API to process the image.
5. The estimated calorie count and identified food items will be displayed below the button.
6. The analysis results and additional metadata are automatically saved to the database.

## Database and Caching Features

The application uses a PostgreSQL database to store analysis results and additional metadata, and Redis for caching to improve performance. 

### Redis Caching

The application uses Redis for the following caching purposes:

* **Image Analysis Caching**: Previously analyzed images are cached to avoid redundant API calls to Gemini
* **API Response Caching**: Frequently accessed endpoints like `/analyses` are cached for faster response times
* **Individual Analysis Caching**: Specific analysis results are cached for quicker retrieval

### PostgreSQL Database

The database schema includes:

### Core Analysis Data

* **Analysis ID**: Unique identifier for each analysis
* **Image Filename**: Name of the uploaded image file
* **Analysis Result**: Full text response from the Gemini API
* **Created At**: Timestamp when the analysis was performed

### Food-Specific Data

* **Food Items**: Automatically extracted list of food items identified in the image

### User Device Information

* **IP Address**: User's IP address
* **User Agent**: Browser and device information
* **Device Type**: Categorized as 'web', 'mobile', 'tablet', or 'other'

### Location Data (with user permission)

* **Location**: Text description of the user's location
* **Latitude/Longitude**: Geographic coordinates

### API Endpoints

The application provides the following API endpoints for database interaction and cache management:

* `POST /upload`: Upload and analyze an image, saving results to the database and cache
* `GET /analyses`: Retrieve all past analyses (cached for improved performance)
* `GET /analyses/<analysis_id>`: Retrieve a specific analysis by ID (cached for improved performance)
* `PUT /analyses/<analysis_id>/location`: Update location data for a specific analysis (requires user permission)
* `POST /admin/clear-cache`: Admin endpoint to clear the Redis cache (requires admin token)
* `GET /admin/cache-stats`: Admin endpoint to get Redis cache statistics (requires admin token)

## Important Notes

* **API Key Security**: Never commit your actual `.env` file with the API key to a public repository.
* **CORS**: The Flask backend has `Flask-CORS` enabled to allow requests from the frontend (which will be on a different port).
* **Error Handling**: Basic error handling is in place. Check the browser console and backend terminal for more detailed error messages if something goes wrong.
* **Database Integration**: The application uses PostgreSQL to store analysis results and additional metadata.
* **Redis Caching**: Redis is used to cache API responses and image analysis results for improved performance.
* **Data Privacy**: Location data is only collected with explicit user permission.
* **Admin Features**: The application includes admin endpoints for cache management, protected by an admin token.