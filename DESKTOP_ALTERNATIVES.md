# Calorie Counter Desktop App

## Current Status: ✅ SOLVED with Tauri

The calorie counter app now has a fully functional desktop application using **Tauri v2**.

## Features

- Native desktop window with proper OS integration
- Smaller bundle size and better performance than Electron
- Secure architecture with Rust backend
- Full access to all web app features
- Cross-platform compatibility

## Running the Application

### Prerequisites

1. **Flask Backend** (port 5001):
   ```bash
   cd backend && source venv/bin/activate && python app.py
   ```

2. **Frontend Server** (port 3000):
   ```bash
   cd frontend && npx http-server -p 3000 -c-1
   ```

### Start Desktop App

```bash
npx tauri dev
```

### Build for Production

```bash
npx tauri build
```

## Technical Details

### Tauri Configuration
- `src-tauri/tauri.conf.json` - Main configuration
- `src-tauri/src/main.rs` - Rust application entry point  
- `src-tauri/Cargo.toml` - Rust dependencies

### Benefits of Tauri
- **Performance**: Uses system webview instead of bundling Chromium
- **Security**: Rust backend with fine-grained permissions
- **Size**: Significantly smaller bundle size than Electron
- **Memory**: Lower memory usage
- **Native**: Better OS integration and feel

## Alternative Access Methods

### PWA (Progressive Web App)
The web version supports installation as a desktop app:

1. Open <http://127.0.0.1:3000> in Chrome/Edge
2. Look for "Install" button in the address bar
3. Click to install as desktop app

## Project Structure

```
calorie-counter/
├── backend/           # Flask API server
├── frontend/          # Web interface
├── src-tauri/         # Tauri desktop app
├── package.json       # Node.js dependencies
└── README.md          # Main documentation
