# Calorie Counter Web App

This is a web application that allows users to upload an image of food. The backend, built with Python and Flask, sends this image to the Google Gemini API for analysis, which then returns an estimated calorie count and identified food items. The application stores analysis results in a PostgreSQL database along with user device information and food details. The frontend is built with TypeScript and basic HTML/CSS.

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
└── README.md           # This file
```

## Prerequisites

*   Python 3.7+
*   Node.js and npm (for TypeScript compilation and serving frontend)
*   A Google Gemini API Key

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

Set up your Gemini API Key:

1.  Rename `.env.example` to `.env`.
2.  Open the `.env` file and replace `YOUR_GEMINI_API_KEY_HERE` with your actual Google Gemini API key.

    ```
    GEMINI_API_KEY=your_actual_api_key_goes_here
    ```

    **Important**: You can obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

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

## Running the Application

### 1. Start the Backend Server

Navigate to the `backend` directory and run the Flask app:

```bash
cd backend # if not already there
python app.py
```

The backend server will start, usually on `http://127.0.0.1:5001`.

### 2. Start the Frontend Server

Open a **new terminal window/tab**.

Navigate to the `frontend` directory:

```bash
cd frontend # if not already there
```

Serve the `index.html` file using a simple HTTP server:

```bash
http-server .
```

This will typically serve the frontend on `http://127.0.0.1:8080` (or another port if 8080 is busy). The server will show you the exact URL.

### 3. Access the Application

Open your web browser and go to the URL provided by your frontend HTTP server (e.g., `http://127.0.0.1:8080`).

## How to Use

1. Click the "Choose File" button to select an image of food from your computer.
2. A preview of the image will be displayed.
3. Click the "Analyze Image" button.
4. Wait for the Gemini API to process the image.
5. The estimated calorie count and identified food items will be displayed below the button.
6. The analysis results and additional metadata are automatically saved to the database.

## Database Features

The application uses a PostgreSQL database to store analysis results and additional metadata. The database schema includes:

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

The application provides the following API endpoints for database interaction:

* `POST /upload`: Upload and analyze an image, saving results to the database
* `GET /analyses`: Retrieve all past analyses
* `GET /analyses/<analysis_id>`: Retrieve a specific analysis by ID
* `POST /analyses/<analysis_id>/location`: Update location data for a specific analysis (requires user permission)

## Important Notes

* **API Key Security**: Never commit your actual `.env` file with the API key to a public repository.
* **CORS**: The Flask backend has `Flask-CORS` enabled to allow requests from the frontend (which will be on a different port).
* **Error Handling**: Basic error handling is in place. Check the browser console and backend terminal for more detailed error messages if something goes wrong.
* **Database Integration**: The application uses PostgreSQL to store analysis results and additional metadata.
* **Data Privacy**: Location data is only collected with explicit user permission.