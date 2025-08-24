from flask import Flask, render_template_string, request
from instagrapi import Client
import os, time, json

app = Flask(__name__)

# Simple HTML template with username/password form and a console box
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Instagram Bot UI</title>
  <style>
    body { font-family: monospace; background: #111; color: #0f0; padding: 20px; }
    .console { background: black; padding: 15px; height: 400px; overflow-y: scroll; border: 1px solid #0f0; }
    input { padding: 6px; margin: 6px; }
    button { padding: 8px; }
  </style>
</head>
<body>
  <h2>Instagram Follow/Unfollow Bot</h2>
  <form method="post">
    <input type="text" name="username" placeholder="Username" required><br>
    <input type="password" name="password" placeholder="Password" required><br>
    <button type="submit">Run Bot</button>
  </form>

  {% if logs %}
  <h3>Console Output</h3>
  <div class="console">
    {% for line in logs %}
      {{line}}<br>
    {% endfor %}
  </div>
  {% endif %}
</body>
</html>
"""

# Helper: save/load user ids
FOLLOWED_USERS_FILE = "followed_users.json"
def save_followed_users(user_list):
    with open(FOLLOWED_USERS_FILE, 'w') as f:
        json.dump(user_list, f)

def load_followed_users():
    if not os.path.exists(FOLLOWED_USERS_FILE):
        return []
    try:
        with open(FOLLOWED_USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    logs = []
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cl = Client()
        try:
            logs.append(f"Logging in as {username}...")
            cl.login(username, password)
            logs.append("✅ Login successful!")

            target = "nasa"
            max_actions = 3
            logs.append(f"Fetching followers of {target}...")

            user_id = cl.user_id_from_username(target)
            followers = cl.user_followers_v1(user_id, amount=max_actions)

            followed = []
            for user in followers:
                try:
                    logs.append(f"Following {user.username}...")
                    cl.user_follow(user.pk)
                    followed.append(user.pk)
                    time.sleep(3)
                    logs.append(f"✅ Followed {user.username}")
                except Exception as e:
                    logs.append(f"❌ Error following {user.username}: {e}")

            save_followed_users(followed)
            logs.append("Done! Followed users saved.")

        except Exception as e:
            logs.append(f"ERROR: {e}")

    return render_template_string(HTML_TEMPLATE, logs=logs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
