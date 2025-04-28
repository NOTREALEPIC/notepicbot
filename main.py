import time
import os
from discord import app_commands, Embed
from discord.ext import commands
import discord
from flask import Flask
from threading import Thread
from files import files_data
from licence import license_descriptions
import random
import string
import json

# Cooldown check to prevent rapid restarts
def check_restart_limit():
    path = "last_restart.txt"
    current_time = time.time()

    if os.path.exists(path):
        with open(path, "r") as f:
            last_time = float(f.read().strip())
        if current_time - last_time < 1200:  # 10 minutes
            print("⛔ Too soon to restart. Exiting to avoid rate-limit.")
            exit()

    with open(path, "w") as f:
        f.write(str(current_time))
    print("✅ Passed cooldown check. Starting bot.")

check_restart_limit()

# Setup Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Path to the user data file
USER_DATA_FILE = "user_data.json"

# Function to load the data from the JSON file
def load_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Function to save data to the JSON file
def save_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Function to generate random 8-character alphanumeric code
def generate_code():
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(random.choices(characters, k=8))

# Define the /code command
@bot.command()
async def code(ctx):
    # Check if the user has the required role
    required_role = "ROOT"  # Replace with the role name you want to check

    # Check if user has the role
    if any(role.name == required_role for role in ctx.author.roles):
        # Generate the code
        code = generate_code()
        await ctx.send(f'Your generated code is: **{code}**')
    else:
        # User doesn't have the required role
        await ctx.send('You do not have permission to use this command.')

# Define the /paid_id command to save user data
@bot.command()
async def paid_id(ctx, discord_id: str, file: str, date: str, code: str):
    # Load existing data
    data = load_data()

    # Save the new user data
    user_data = {
        "DISCORD ID": discord_id,
        "FILE": file,
        "DATE": date,
        "CODE": code
    }

    # Store it using discord ID as the key
    data[discord_id] = user_data

    # Save the updated data back to the file
    save_data(data)

    await ctx.send(f"Data for {discord_id} has been saved successfully.")

# Define the /get_data command to retrieve saved user data
@bot.command()
async def get_data(ctx, discord_id: str):
    # Load existing data
    data = load_data()

    # Check if data for the user exists
    if discord_id in data:
        user_data = data[discord_id]
        await ctx.send(f"Data for {discord_id}: {user_data}")
    else:
        await ctx.send(f"No data found for {discord_id}.")

# Autocomplete list for the pass command
async def model_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=model, value=model)
        for model in files_data if current.lower() in model.lower()
    ][:25]

@tree.command(name="pass", description="Get info & password for Mod file",guild=discord.Object(id=1232208366735196283))
@app_commands.describe(modelname="File")
@app_commands.autocomplete(modelname=model_autocomplete)
@app_commands.checks.has_role("LEGIT")
@commands.cooldown(1, 10, commands.BucketType.user)
async def pass_command(interaction: discord.Interaction, modelname: str):
    if modelname not in files_data:
        await interaction.response.send_message(" Model not found!", ephemeral=True)
        return

    data = files_data[modelname]
    file_size = data["size"]
    version = data["version"]
    for_ = data["for"]
    last_update = data["last_update"]
    license_type = data["license"]
    password = data["password"]
    license_desc = license_descriptions.get(license_type, "No description available.")

    # Embed with formatted block content
    embed = Embed(title=f" Access: {modelname}", color=0x2ecc71)

    embed.add_field(name="```|``` FILE NAME", value=f"```{modelname}```", inline=False)
    embed.add_field(name="```|``` FILE SIZE", value=f"```{file_size}```", inline=True)
    embed.add_field(name="```|``` VERSION", value=f"```{version}```", inline=True)
    embed.add_field(name="```|``` FOR", value=f"```{for_}```", inline=True)
    embed.add_field(name="```|``` LAST UPDATE", value=f"```{last_update}```", inline=True)
    embed.add_field(name="```|``` LICENSE", value=f"```{license_type}```", inline=True)
    embed.add_field(name="```|``` LICENSE DETAILS", value=f"```{license_desc}```", inline=False)
    embed.add_field(name="```|``` PASSWORD", value=f"```{password}```", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# Error handler
@pass_command.error
async def pass_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message("Access denied. Verify in <#1233843778754838679> to continue.", ephemeral=True)

# Bot ready event
@bot.event
async def on_ready():
    await tree.sync()
    await tree.sync(guild=discord.Object(id=1232208366735196283))  # Add this line with your server ID
    print(f"✅ Bot ready as {bot.user}")


# Flask server (keeps the bot alive)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!", 200

def run():
    # Use the port specified by Render (or any platform you're using)
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 if PORT is not set
    app.run(host='0.0.0.0', port=port)

Thread(target=run).start()

# Run the bot
bot.run(os.environ["asmr"])
