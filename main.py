import os
import time
import json
from flask import Flask, render_template, request, jsonify, Response
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, LoginRequired

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Configuration ---
# These are now just constants; the actual user/pass will come from the web form.
TARGET_ACCOUNT = "nasa"
MAX_ACTIONS = 5

# This will hold the client session for a user.
# In a real multi-user app, you'd manage this differently (e.g., with user sessions).
cl = None

# --- Helper Functions for saving the list of followed users ---
def save_followed_users(username, user_list):
    """Saves the list of followed users to a file named after the user."""
    with open(f"{username}_followed_users.json", 'w') as f:
        json.dump(user_list, f)

# --- Web Routes ---

@app.route('/')
def index():
    """Serves the main HTML user interface."""
    return render_template('index.html')

@app.route('/run-bot', methods=['POST'])
def run_bot():
    """Receives login credentials from the web form and attempts to log in."""
    global cl
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400
    
    cl = Client()
    session_file = f"{username}.json"
    
    try:
        if os.path.exists(session_file):
            cl.load_settings(session_file)
            cl.login(username, password)
        else:
            cl.login(username, password)
        
        cl.dump_settings(session_file)
        return jsonify({"success": True, "message": "Login successful! Starting bot actions..."})
        
    except ChallengeRequired:
        # If 2FA is needed, tell the front-end to ask for the code.
        return jsonify({
            "success": False, 
            "challenge_required": True, 
            "message": "Two-factor authentication required. Please enter the 6-digit code."
        })
    except LoginRequired:
        return jsonify({"error": "Login failed. Please check your username and password."}), 401
    except Exception as e:
        return jsonify({"error": f"An unexpected login error occurred: {e}"}), 500

@app.route('/verify-challenge', methods=['POST'])
def verify_challenge():
    """Receives the 2FA code from the web form and verifies it."""
    global cl
    data = request.get_json()
    code = data.get('code')
    username = data.get('username')

    if not code:
        return jsonify({"error": "Verification code is required."}), 400
    
    try:
        cl.challenge_code(code)
        cl.dump_settings(f"{username}.json")
        return jsonify({"success": True, "message": "Verification successful! Starting bot actions..."})
    except Exception as e:
        return jsonify({"error": f"Verification failed: {e}"}), 400

@app.route('/start-actions')
def start_actions():
    """This is a special 'streaming' route that runs the bot's follow logic
       and sends live updates back to the webpage's console."""
    def generate_logs():
        global cl
        if not cl or not cl.user_id:
            yield "data: ERROR: Not logged in. Please refresh and try again.\n\n"
            return

        try:
            username = cl.username
            yield f"data: ✅ Login successful for {username}!\n\n"
            time.sleep(1)

            yield f"data: --- Starting to Follow Users ---\n\n"
            time.sleep(1)
            
            yield f"data: Finding target account '{TARGET_ACCOUNT}'...\n\n"
            target_user_id = cl.user_id_from_username(TARGET_ACCOUNT)
            yield f"data: Found! User ID is {target_user_id}\n\n"
            time.sleep(1)

            yield f"data: Fetching followers of '{TARGET_ACCOUNT}'...\n\n"
            followers = cl.user_followers_v1(target_user_id, amount=MAX_ACTIONS)
            
            followed_user_ids = []
            for user in followers:
                try:
                    user_id = user.pk
                    user_name = user.username
                    yield f"data:   -> Attempting to follow: {user_name} (ID: {user_id})\n\n"
                    cl.user_follow(user_id)
                    yield f"data:   ✅ Successfully followed {user_name}!\n\n"
                    followed_user_ids.append(user_id)
                    
                    delay = 5 # Keep delay short for testing
                    yield f"data:      ... Waiting for {delay} seconds...\n\n"
                    time.sleep(delay)
                except Exception as e:
                    yield f"data:   ❌ Could not follow. Reason: {e}\n\n"
            
            save_followed_users(username, followed_user_ids)
            yield f"data: --- Finished following {len(followed_user_ids)} users. ---\n\n"
            yield f"data: BOT FINISHED. You can close this page.\n\n"

        except Exception as e:
            yield f"data: AN UNEXPECTED ERROR OCCURRED: {e}\n\n"

    return Response(generate_logs(), mimetype='text/event-stream')
