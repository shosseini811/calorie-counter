// Prevents additional console window on Windows in release, DO NOT REMOVE!!
// This line makes sure that when you build the final version of your app for Windows users, it doesn't show an unnecessary command window.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// This imports the Manager trait from the tauri library.
use tauri::Manager;

// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
// - tauri::command specifically tells Tauri that the following Rust function ( greet or get_backend_url in this case) should be callable from your JavaScript frontend.

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn get_backend_url() -> String {
    "http://localhost:5001".to_string()
}
// - tauri::mobile_entry_point tells Tauri (the framework you're using to build the app) that this run function is the starting point for the mobile app.
// If this is a mobile app, mark this function as the main starting place for mobile.
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![greet, get_backend_url])
        .setup(|app| {
            #[cfg(debug_assertions)] // only include this code on debug builds
            {
                let window = app.get_webview_window("main").unwrap();
                window.open_devtools();
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

fn main() {
    run();
}
