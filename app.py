import os
import time
import json
from flask import Flask, render_template, request, jsonify, Response
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, LoginRequired

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Configuration ---
TARGET_ACCOUNT = "nasa"
MAX_ACTIONS = 5

# This will hold the client session for a user during the login process.
cl = None

# --- Helper Function (no changes) ---
def save_followed_users(username, user_list):
    with open(f"{username}_followed_users.json", 'w') as f:
        json.dump(user_list, f)

# --- Web Routes ---

@app.route('/')
def index():
    """Serves the main HTML user interface."""
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Receives login credentials from the web UI and attempts to log in."""
    global cl
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400
    
    cl = Client()
    session_file = f"{username}.json"

    # ==========================================================================
    # THIS IS THE CRITICAL FIX
    # We tell the client from the start how to handle a 2FA challenge.
    # By providing an empty string, we prevent it from calling input() and force
    # it to raise the ChallengeRequired exception, which is what we want.
    cl.challenge_code_handler = lambda username, choice: ""
    # ==========================================================================
    
    try:
        if os.path.exists(session_file):
            cl.load_settings(session_file)
            cl.login(username, password)
        else:
            cl.login(username, password)
        
        cl.dump_settings(session_file)
        return jsonify({"success": True, "message": "Login successful! Starting bot actions..."})
        
    except ChallengeRequired:
        # Now, this exception will be caught correctly without the server crashing.
        return jsonify({
            "success": False, 
            "challenge_required": True, 
            "message": "Two-factor authentication required. Please enter the code sent to your email."
        })
    except LoginRequired:
        return jsonify({"error": "Login failed. Please check credentials."}), 401
    except Exception as e:
        return jsonify({"error": f"An unexpected login error occurred: {e}"}), 500

@app.route('/verify', methods=['POST'])
def verify():
    """Receives the 2FA code from the web UI and verifies it."""
    global cl
    data = request.get_json()
    code = data.get('code')
    username = data.get('username')

    if not code:
        return jsonify({"error": "Verification code is required."}), 400
    
    try:
        # The challenge_code function uses the code provided by the user from the web form.
        cl.challenge_code(code)
        cl.dump_settings(f"{username}.json")
        return jsonify({"success": True, "message": "Verification successful! Starting bot actions..."})
    except Exception as e:
        return jsonify({"error": f"Verification failed: {e}"}), 400

@app.route('/start-bot-actions')
def start_bot_actions():
    """This 'streaming' route runs the bot's logic and sends live log updates."""
    # (This function does not need to be changed. It is correct as is.)
    def generate_logs():
        global cl
        if not cl or not cl.user_id:
            yield "data: ERROR: Not logged in. Please start over.\n\n"
            return
        try:
            # ... (The rest of your bot logic) ...
            yield "data: BOT FINISHED.\n\n"
        except Exception as e:
            yield f"data: AN UNEXPECTED ERROR OCCURRED: {e}\n\n"
    return Response(generate_logs(), mimetype='text/event-stream')

# NOTE: REMOVE the if __name__ == '__main__': block for Render deployment
# Gunicorn will be used to run the app.
