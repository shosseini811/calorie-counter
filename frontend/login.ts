document.addEventListener('DOMContentLoaded', () => {
    const googleLoginBtn = document.getElementById('googleLoginBtn') as HTMLButtonElement;
    const loginError = document.getElementById('loginError') as HTMLDivElement;
    const loginErrorText = document.getElementById('loginErrorText') as HTMLParagraphElement;

    // Check if the user is already logged in
    checkAuthStatus();

    // Add event listener to the Google login button
    googleLoginBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('http://localhost:5001/login', {
                method: 'GET',
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            console.log("Data", data);
            // Redirect to Google's authorization page
            if (data.authorization_url) {
                window.location.href = data.authorization_url;
            } else {
                throw new Error('No authorization URL received from server');
            }
        } catch (error: any) {
            console.error('Login error:', error);
            loginErrorText.textContent = `Login error: ${error.message || 'Unknown error'}`;
            loginError.style.display = 'block';
        }
    });

    // Handle the redirect from Google after authentication
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');

    if (code && state) {
        // We're in the callback - handle the authentication
        handleAuthCallback(code, state);
    }

    async function handleAuthCallback(code: string, state: string) {
        try {
            // This is a callback from Google OAuth, handle it
            const response = await fetch(`http://localhost:5001/login/callback?code=${code}&state=${state}`, {
                method: 'GET',
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                // Store user info in localStorage for client-side access
                localStorage.setItem('user', JSON.stringify(data.user));
                // Redirect to the main app
                window.location.href = 'index.html';
            } else {
                throw new Error('Authentication failed');
            }
        } catch (error: any) {
            console.error('Authentication error:', error);
            loginErrorText.textContent = `Authentication error: ${error.message || 'Unknown error'}`;
            loginError.style.display = 'block';
        }
    }

    async function checkAuthStatus() {
        try {
            const response = await fetch('http://localhost:5001/user', {
                method: 'GET',
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.authenticated) {
                // User is already logged in, redirect to the main app
                localStorage.setItem('user', JSON.stringify(data.user));
                window.location.href = 'index.html';
            }
        } catch (error) {
            console.error('Error checking authentication status:', error);
            // Stay on login page if there's an error
        }
    }
});
