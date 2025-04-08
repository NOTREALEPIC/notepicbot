from discord import app_commands, Embed
from discord.ext import commands
import discord
import os

from files import files_data
from licence import license_descriptions

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Autocomplete list
async def model_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=model, value=model)
        for model in files_data if current.lower() in model.lower()
    ][:25]

@tree.command(name="pass", description="Get info & password for a model")
@app_commands.describe(modelname="Choose a model")
@app_commands.autocomplete(modelname=model_autocomplete)
@app_commands.checks.has_role("Z-Mod")
async def pass_command(interaction: discord.Interaction, modelname: str):
    if modelname not in files_data:
        await interaction.response.send_message("❌ Model not found!", ephemeral=True)
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
    embed = Embed(title=f"Access: {modelname}", color=0x2ecc71)

    info = f"""``FILE NAME`` {modelname}
``FILE SIZE`` {file_size:<15} ``VERSION`` {version}
``FOR`` {for_:<15} ``LAST UPDATE`` {last_update}
``LICENSE`` {license_type}
``LICENSE DETAILS`` {license_desc}
``PASSWORD`` {password}"""

    embed.description = info

    await interaction.response.send_message(embed=embed, ephemeral=True)

# Error handler
@pass_command.error
async def pass_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message("❌ You must verify your account.", ephemeral=True)

# Bot ready
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot ready as {bot.user}")

# Flask server (Don't remove)
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# Run the bot
bot.run(os.environ["asmr"])
