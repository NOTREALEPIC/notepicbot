# ==================================================================================
# Instagram Follow/Unfollow Bot - A Python Learning Project (Version 4)
#
# PURPOSE: To teach Python concepts like API interaction, loops, and file handling.
# WARNING: This is for educational use ONLY. Using this on your main account
#          with high limits WILL get your account banned by Instagram.
#          ALWAYS use a new, disposable test account.
# ==================================================================================

import os
import time
import json
from instagrapi import Client
from getpass import getpass # To securely ask for your password

# --- Configuration ---
# Use a brand new, disposable test account.
# TEST_USERNAME = input("Enter your TEST Instagram username: ")
# TEST_PASSWORD = getpass("Enter your TEST Instagram password (typing will be invisible): ")

TEST_USERNAME = "jasser_vk"
TEST_PASSWORD = "POthan1312"

# We will find followers of this large, public account to be safe.
TARGET_ACCOUNT = "nasa"
MAX_ACTIONS = 5000 # The number of people to follow and then unfollow. Keep this low!

# The file where we'll save the user IDs we've followed.
FOLLOWED_USERS_FILE = "followed_users.json"


# --- Helper Functions ---
def save_followed_users(user_list):
    """Saves a list of user IDs to our JSON file."""
    with open(FOLLOWED_USERS_FILE, 'w') as f:
        json.dump(user_list, f)

def load_followed_users():
    """Loads the list of user IDs from our JSON file."""
    if not os.path.exists(FOLLOWED_USERS_FILE):
        return []
    try:
        with open(FOLLOWED_USERS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


# --- Main Bot Logic ---
cl = Client()

try:
    # --- Login ---
    session_file = f"{TEST_USERNAME}.json"
    if os.path.exists(session_file):
        cl.load_settings(session_file)
        print(f"Loaded existing session for {TEST_USERNAME}")
        cl.login(TEST_USERNAME, TEST_PASSWORD)
    else:
        cl.login(TEST_USERNAME, TEST_PASSWORD)

    cl.dump_settings(session_file)
    print(f"Login successful for {TEST_USERNAME}!")

    # ==========================================================================
    # PART 1: Find and Follow Users
    # ==========================================================================
    print("\n--- Starting Part 1: Following Users ---")

    print(f"Finding target account '{TARGET_ACCOUNT}'...")
    target_user_id = cl.user_id_from_username(TARGET_ACCOUNT)
    print(f"Found! User ID is {target_user_id}")

    print(f"Fetching the last {MAX_ACTIONS} followers of '{TARGET_ACCOUNT}'...")
    # The 'user_followers' function now returns a list of user ID strings.
    followers_ids = cl.user_followers_v1(target_user_id, amount=MAX_ACTIONS)

    followed_user_ids = []

    # THIS IS THE FIX: We loop through the list of IDs directly.
            # THIS IS THE NEW, WORKING LOOP
    for user in followers_ids:
                try:
                    # We now correctly access the .pk and .username attributes from the user object
                    user_id = user.pk
                    username = user.username

                    print(f"  -> Attempting to follow user: {username} (ID: {user_id})")

                    # We pass ONLY the user_id (the number) to the follow function
                    cl.user_follow(user_id)

                    print(f"  ✅ Successfully followed {username}!")

                    # We append ONLY the user_id to our list for unfollowing later
                    followed_user_ids.append(user_id)

                    # Wait a random, human-like time
                    delay = 10 + (5 * (os.urandom(1)[0] / 255))
                    print(f"     ... Waiting for {delay:.2f} seconds...")
                    time.sleep(delay)

                except Exception as e:
                    # We use 'username' here for a more readable error message
                    print(f"  ❌ Could not follow {username}. Reason: {e}")

    save_followed_users(followed_user_ids)
    print(f"\nFinished following. Followed {len(followed_user_ids)} users. Their IDs are saved.")

    # ==========================================================================
    # PART 2: Unfollow the Users We Just Followed
    # ==========================================================================
    # print("\n--- Starting Part 2: Unfollowing Users ---")

    # print("Simulating a 1-day wait... (waiting for 30 seconds)")
    # time.sleep(30)

    # users_to_unfollow = load_followed_users()

    # if not users_to_unfollow:
    #     print("No users found in our list to unfollow.")
    # else:
    #     print(f"Found {len(users_to_unfollow)} users to unfollow from our list.")
    #     for user_id in users_to_unfollow:
    #         try:
    #             print(f"  -> Attempting to unfollow user ID: {user_id}")
    #             cl.user_unfollow(user_id)
    #             print(f"  ✅ Successfully unfollowed user ID: {user_id}!")

    #             delay = 10 + (5 * (os.urandom(1)[0] / 255))
    #             print(f"     ... Waiting for {delay:.2f} seconds...")
    #             time.sleep(delay)

    #         except Exception as e:
    #             print(f"  ❌ Could not unfollow user ID: {user_id}. Reason: {e}")

    # save_followed_users([])
    # print("\nFinished unfollowing. The list is now empty.")

except Exception as e:
    print(f"\nAN ERROR OCCURRED: {e}")
finally:
    print("\nScript finished.")
