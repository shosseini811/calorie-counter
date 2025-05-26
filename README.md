# Calorie Counter Web App

This is a simplified web application that allows users to upload an image of food. The backend, built with Python and Flask, sends this image to the Google Gemini API for analysis, which then returns an estimated calorie count and identified food items. The frontend is built with TypeScript and basic HTML/CSS.

The application now features Google account authentication, allowing users to sign in with their Google accounts before using the calorie counter service.

## 🎥 Demo

Watch the application in action:

<video src="https://github.com/user-attachments/assets/d1545a09-a26d-4f83-8d29-35bfc93c95c4" controls width="100%"></video>

## Project Structure

```
calorie-counter/
├── backend/
│   ├── app.py            # Flask backend logic
│   ├── requirements.txt  # Python dependencies
│   ├── .env.example      # Example for environment variables (API keys and secrets)
│   └── .env              # Actual environment variables (you need to create this)
├── frontend/
│   ├── index.html        # Main HTML page
│   ├── login.html        # Login page with Google authentication
│   ├── style.css         # CSS for styling
│   ├── main.ts           # TypeScript for main app logic
│   ├── login.ts          # TypeScript for login functionality
│   ├── tsconfig.json     # TypeScript compiler options
│   └── dist/             # Compiled JavaScript (main.js and login.js will be here after compilation)
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

Set up your API Keys and Secrets:

1.  Rename `.env.example` to `.env`.
2.  Open the `.env` file and add the following:

    ```
    GEMINI_API_KEY=your_actual_gemini_api_key_goes_here
    GOOGLE_CLIENT_ID=your_google_oauth_client_id
    GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
    SECRET_KEY=a_random_secret_key_for_flask_sessions
    ```

    **Important**: 
    - You can obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    - For Google OAuth credentials (CLIENT_ID and CLIENT_SECRET), set up a project in the [Google Cloud Console](https://console.cloud.google.com/) and create OAuth 2.0 credentials.

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

1.  When you first access the application, you'll be directed to the login page.
2.  Click the "Sign in with Google" button to authenticate using your Google account.
3.  After successful authentication, you'll be redirected to the main application.
4.  Click the "Choose File" button to select an image of food from your computer.
5.  A preview of the image will be displayed.
6.  Click the "Analyze Image" button.
7.  Wait for the Gemini API to process the image.
8.  The estimated calorie count and identified food items will be displayed below the button.
9.  You can log out using the logout button in the user profile section.

## Important Notes

*   **API Key Security**: Never commit your actual `.env` file with API keys and secrets to a public repository.
*   **CORS**: The Flask backend has `Flask-CORS` enabled to allow requests from the frontend (which will be on a different port).
*   **Error Handling**: Basic error handling is in place. Check the browser console and backend terminal for more detailed error messages if something goes wrong.
*   **Authentication**: The application uses Google OAuth 2.0 for user authentication. In a production environment, you would want to implement additional security measures.
*   **Session Management**: User sessions are managed using Flask-Login and browser cookies. The session configuration is set for development purposes and should be enhanced for production use.
*   **Redirect URIs**: Make sure your Google OAuth client has the correct redirect URIs configured (http://localhost:5001/login/callback for development).