import os
import sys
import time
import random
import logging
from datetime import datetime, timedelta
from threading import Thread

import discord
from discord.ext import commands, tasks
from discord import app_commands, Embed
from flask import Flask

# Your imported data modules (make sure these are correct)
from files import files_data
from pro_file_info import pro_file_info
from paid_id import paid_id_data
from licence import license_descriptions

# ----------- Setup Logging (Better than print for production) -----------
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# ----------- Cooldown Check to Avoid Rapid Restarts -----------
def check_restart_limit():
    path = "last_restart.txt"
    current_time = time.time()

    if os.path.exists(path):
        with open(path, "r") as f:
            last_time = float(f.read().strip())
        if current_time - last_time < 1200:  # 20 minutes cooldown (you had 10)
            logging.error("⛔ Too soon to restart. Exiting to avoid rate-limit.")
            sys.exit()

    with open(path, "w") as f:
        f.write(str(current_time))
    logging.info("✅ Passed cooldown check. Starting bot.")

check_restart_limit()

# ----------- Utility Functions -----------

def generate_code():
    """Generate unique 8-char alphanumeric code like epic0001."""
    random_number = random.randint(1, 9999)
    return f"epic{random_number:04d}"

def check_code_exists(code: str) -> bool:
    if os.path.exists("generated_codes.txt"):
        with open("generated_codes.txt", "r") as file:
            codes = [line.strip() for line in file.readlines()]
            return code in codes
    return False

# ----------- Discord Bot Setup -----------

intents = discord.Intents.default()
intents.message_content = True  # Required for commands reading message content

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ----------- Autocomplete Functions -----------

async def model_autocomplete(interaction: discord.Interaction, current: str):
    choices = [
        app_commands.Choice(name=model, value=model)
        for model in files_data if current.lower() in model.lower()
    ][:25]
    return choices

async def code_autocomplete(interaction: discord.Interaction, current: str):
    choices = [
        app_commands.Choice(name=code, value=code)
        for code in paid_id_data if current.lower() in code.lower()
    ][:25]
    return choices

async def fid_autocomplete(interaction: discord.Interaction, current: str):
    choices = [
        app_commands.Choice(name=fid, value=fid)
        for fid in pro_file_info if current.lower() in fid.lower()
    ][:25]
    return choices

# ----------- Commands -----------

@tree.command(
    name="pass",
    description="Get info & password for Mod file",
    guilds=[discord.Object(id=1232208366735196283), discord.Object(id=1358758393300648126)]
)
@app_commands.describe(modelname="File")
@app_commands.autocomplete(modelname=model_autocomplete)
@app_commands.checks.has_role("LEGIT")
@app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
async def pass_command(interaction: discord.Interaction, modelname: str):
    if modelname not in files_data:
        await interaction.response.send_message("Model not found!", ephemeral=True)
        return

    data = files_data[modelname]
    license_desc = license_descriptions.get(data["license"], "No description available.")

    embed = Embed(title=f"Access: {modelname}", color=0x2ecc71)
    embed.add_field(name="```|``` FILE NAME", value=f"```{modelname}```", inline=False)
    embed.add_field(name="```|``` FILE SIZE", value=f"```{data['size']}```", inline=True)
    embed.add_field(name="```|``` VERSION", value=f"```{data['version']}```", inline=True)
    embed.add_field(name="```|``` FOR", value=f"```{data['for']}```", inline=True)
    embed.add_field(name="```|``` LAST UPDATE", value=f"```{data['last_update']}```", inline=True)
    embed.add_field(name="```|``` LICENSE", value=f"```{data['license']}```", inline=True)
    embed.add_field(name="```|``` LICENSE DETAILS", value=f"```{license_desc}```", inline=False)
    embed.add_field(name="```|``` PASSWORD", value=f"```{data['password']}```", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@pass_command.error
async def pass_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message(
            "Access denied. Verify in <#1233843778754838679> to continue.", ephemeral=True
        )
    else:
        logging.error(f"Error in pass_command: {error}")

# Code generation command
@tree.command(
    name="code",
    description="Generate code",
    guild=discord.Object(id=1232208366735196283)
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_role("ROOT")
@app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
async def code_command(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    new_code = None
    for _ in range(100):  # Try 100 times max
        candidate = generate_code()
        if not check_code_exists(candidate):
            new_code = candidate
            break

    if new_code is None:
        await interaction.followup.send("Failed to generate a unique code. Try again later.")
        return

    # Ensure file exists
    if not os.path.exists("generated_codes.txt"):
        with open("generated_codes.txt", "w"): pass

    with open("generated_codes.txt", "a") as f:
        f.write(f"{new_code}\n")

    logging.info(f"Code generated and saved: {new_code}")
    await interaction.followup.send(f"Generated Code: {new_code}")

@code_command.error
async def code_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    else:
        logging.error(f"Error in code_command: {error}")
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)

# Paid ID command
@tree.command(
    name="paid_id",
    description="Customer info",
    guild=discord.Object(id=1232208366735196283)
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_role("ROOT")
@app_commands.describe(code="Enter the customer's code")
@app_commands.autocomplete(code=code_autocomplete)
@app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
async def paid_id_command(interaction: discord.Interaction, code: str):
    try:
        await interaction.response.defer(thinking=True)

        if code not in paid_id_data:
            await interaction.edit_original_response(content="Code not found")
            return

        data = paid_id_data[code]

        embed = Embed(title=f"Access: {code}", color=0x2ecc71)
        embed.add_field(name="```|``` DISCORD ID", value=f"```{data['Discord_id']}```", inline=False)
        embed.add_field(name="```|``` FILE NAME", value=f"```{data['File_Name']}```", inline=False)
        embed.add_field(name="```|``` FOR", value=f"```{data['For_']}```", inline=True)
        embed.add_field(name="```|``` DATE", value=f"```{data['Date']}```", inline=True)
        embed.add_field(name="```|``` PAYMENT VIA", value=f"```{data['Via']}```", inline=True)

        await interaction.edit_original_response(embed=embed)

    except Exception as e:
        logging.error(f"Error in paid_id_command: {e}")
        await interaction.edit_original_response(content=f"Error: {e}")

@paid_id_command.error
async def paid_id_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    else:
        logging.error(f"Error in paid_id_command: {error}")

# Pro file info command
@tree.command(
    name="proinfo",
    description="Get info about paid files",
    guild=discord.Object(id=1232208366735196283)
)
@app_commands.checks.has_role("LEGIT")
@app_commands.describe(fid="Enter the file or select from the list.")
@app_commands.autocomplete(fid=fid_autocomplete)
@app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
async def proinfo_command(interaction: discord.Interaction, fid: str):
    try:
        allowed_category_id = 1369408086967844924  # Replace with your Category ID
        if interaction.channel.category_id != allowed_category_id:
            await interaction.response.send_message("ONLY WORK IN TICKET", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        if fid not in pro_file_info:
            await interaction.edit_original_response(content="No file named this. Please check the spelling.")
            return

        data = pro_file_info[fid]
        await interaction.edit_original_response(content=data["FIRST"])
        # Send other parts without pings
        await interaction.channel.send(content=data["SEC"], allowed_mentions=discord.AllowedMentions.none())
        await interaction.channel.send(content=data["THIRD"], allowed_mentions=discord.AllowedMentions.none())
        await interaction.channel.send(content=data["FOUR"], allowed_mentions=discord.AllowedMentions.none())

    except Exception as e:
        logging.error(f"Error in proinfo_command: {e}")
        await interaction.edit_original_response(content=f"Error: {e}")

@proinfo_command.error
async def proinfo_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message(
            "<a:epic_skull:1369682573726453846> Verify in <#1233843778754838679> to continue.",
            ephemeral=True
        )
    else:
        logging.error(f"Error in proinfo_command: {error}")

# ----------- Run Bot -----------

# Get token securely from environment variable or file (never hardcode tokens!)
TOKEN = os.getenv("asmr")
if not TOKEN:
    logging.error("Discord token not found in environment variable DISCORD_BOT_TOKEN.")
    sys.exit()

# ----------- Flask Uptime -----------

app = Flask("")

@app.route("/")
def home():
    return "Bot is running and alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Run Flask in a separate thread
flask_thread = Thread(target=run_flask)
flask_thread.start()

# ----------- Run the bot -----------

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logging.info("------")
    await tree.sync()
    logging.info("Commands synced!")

bot.run(TOKEN)
