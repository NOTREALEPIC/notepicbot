import time
import os
import random
import string
from discord import app_commands, Embed
from discord.ext import commands
import discord
from flask import Flask
from threading import Thread

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

# Function to generate a random code
def generate_code():
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(random.choices(characters, k=8))

# Function to check if the code already exists
def check_code_exists(code):
    if os.path.exists("generated_codes.txt"):
        with open("generated_codes.txt", "r") as file:
            codes = file.readlines()
            codes = [line.strip() for line in codes]
            return code in codes
    return False

# Command to generate a unique code
@bot.command()
async def code(ctx):
    # Generate a new unique code
    while True:
        new_code = generate_code()
        if not check_code_exists(new_code):
            break
    
    # Save the code to the file to track it
    with open("generated_codes.txt", "a") as file:
        file.write(f"{new_code}\n")

    # Send the generated code to the user
    await ctx.send(f"Generated Code: {new_code}")

# Command to add details to paid_id.txt
@bot.command()
async def paid_id(ctx):
    # Check if the user has the ROOT role
    required_role = "ROOT"
    if not any(role.name == required_role for role in ctx.author.roles):
        await ctx.send("You do not have permission to use this command.")
        return

    # Ask for details
    await ctx.send("Please enter the Discord ID:")
    discord_id = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    discord_id = discord_id.content.strip()

    await ctx.send("Please enter the file name:")
    file_name = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    file_name = file_name.content.strip()

    await ctx.send("Please enter the code:")
    code = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    code = code.content.strip()

    # Get current date and time
    current_date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    # Save to paid_id.txt
    with open("paid_id.txt", "a") as file:
        file.write(f"CODE: {code} {{DISCORD ID: {discord_id} FILE: {file_name} DATE: {current_date_time}}}\n")

    await ctx.send(f"Data saved successfully for CODE: {code}.")

# Command to get details for a specific code
@bot.command()
async def get_code_d(ctx, code: str):
    # Read the paid_id.txt file to find the details for the code
    found = False
    with open("paid_id.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            if f"CODE: {code}" in line:
                found = True
                discord_id = line.split("DISCORD ID:")[1].split(" FILE:")[0].strip()
                file_name = line.split("FILE:")[1].split(" DATE:")[0].strip()
                date_time = line.split("DATE:")[1].strip().strip("}")
                
                # Create an embed with the details
                embed = Embed(title=f"Details for CODE: {code}", color=0x2ecc71)
                embed.add_field(name="| Code", value=code, inline=False)
                embed.add_field(name="| Discord ID", value=discord_id, inline=True)
                embed.add_field(name="| File Name", value=file_name, inline=True)
                embed.add_field(name="| Date", value=date_time, inline=True)
                await ctx.send(embed=embed)
                break
    
    if not found:
        await ctx.send("Code not found.")

# Error handling for permission-based commands
@paid_id.error
async def paid_id_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You don't have the required role to use this command.")

# Bot ready event
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot ready as {bot.user}")

# Flask server (keeps the bot alive)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!", 200

def run():
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 if PORT is not set
    app.run(host='0.0.0.0', port=port)

Thread(target=run).start()

# Run the bot
bot.run(os.environ["asmr"])
