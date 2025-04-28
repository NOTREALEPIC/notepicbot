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

# Command to generate a unique code
def generate_code():
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(random.choices(characters, k=8))

# /code command to generate unique code
@bot.command()
async def code(ctx):
    # Check if the user has the required role (Replace 'ROOT' with your actual role name)
    required_role = "ROOT"
    if not any(role.name == required_role for role in ctx.author.roles):
        await ctx.send("You do not have permission to use this command.")
        return

    # Generate and send the unique code
    new_code = generate_code()
    await ctx.send(f"Generated Code: {new_code}")

# /paid_id command to input and save data
@bot.command()
async def paid_id(ctx):
    # Check if the user has the required role
    required_role = "ROOT"
    if not any(role.name == required_role for role in ctx.author.roles):
        await ctx.send("You do not have permission to use this command.")
        return

    # Ask for the details
    await ctx.send("Please enter the Discord ID:")
    discord_id_msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    discord_id = discord_id_msg.content.strip()

    await ctx.send("Please enter the file name:")
    file_name_msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    file_name = file_name_msg.content.strip()

    await ctx.send("Please enter the code:")
    code_msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    code = code_msg.content.strip()

    # Get current date and time
    current_date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    # Save to paid_id.txt
    with open("paid_id.txt", "a") as file:
        file.write(f"CODE: {code} {{DISCORD ID: {discord_id} FILE: {file_name} DATE: {current_date_time}}}\n")

    await ctx.send(f"Data saved successfully for CODE: {code}.")

# /get_code_d command to get details related to a code
@bot.command()
async def get_code_d(ctx, code: str):
    # Check if the user has the required role
    required_role = "ROOT"
    if not any(role.name == required_role for role in ctx.author.roles):
        await ctx.send("You do not have permission to use this command.")
        return

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
