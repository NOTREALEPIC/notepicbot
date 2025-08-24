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
    
    try:
        if os.path.exists(session_file):
            cl.load_settings(session_file)
            cl.login(username, password)
        else:
            cl.login(username, password)
        
        cl.dump_settings(session_file)
        return jsonify({"success": True, "message": "Login successful! Starting bot actions..."})
        
    except ChallengeRequired:
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
        cl.challenge_code(code)
        cl.dump_settings(f"{username}.json")
        return jsonify({"success": True, "message": "Verification successful! Starting bot actions..."})
    except Exception as e:
        return jsonify({"error": f"Verification failed: {e}"}), 400

@app.route('/start-bot-actions')
def start_bot_actions():
    """This 'streaming' route runs the bot's logic and sends live log updates."""
    def generate_logs():
        global cl
        if not cl or not cl.user_id:
            yield "data: ERROR: Not logged in. Please start over.\n\n"
            return

        try:
            username = cl.username
            yield f"data: ✅ Logged in as {username}!\n\n"
            time.sleep(1)

            yield f"data: --- Starting to Follow Users ---\n\n"
            yield f"data: Finding target: '{TARGET_ACCOUNT}'...\n\n"
            target_user_id = cl.user_id_from_username(TARGET_ACCOUNT)
            yield f"data: Found! User ID is {target_user_id}\n\n"
            
            yield f"data: Fetching followers...\n\n"
            followers = cl.user_followers_v1(target_user_id, amount=MAX_ACTIONS)
            
            followed_user_ids = []
            for user in followers:
                try:
                    user_id = user.pk
                    user_name = user.username
                    yield f"data:   -> Following: {user_name}\n\n"
                    cl.user_follow(user_id)
                    yield f"data:   ✅ Success!\n\n"
                    followed_user_ids.append(user_id)
                    time.sleep(5)
                except Exception as e:
                    yield f"data:   ❌ Could not follow. Reason: {e}\n\n"
            
            save_followed_users(username, followed_user_ids)
            yield f"data: --- Finished following {len(followed_user_ids)} users. ---\n\n"
            yield f"data: BOT FINISHED.\n\n"

        except Exception as e:
            yield f"data: AN UNEXPECTED ERROR OCCURRED: {e}\n\n"

    return Response(generate_logs(), mimetype='text/event-stream')
