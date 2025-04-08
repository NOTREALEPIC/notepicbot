import discord
from discord.ext import commands
from discord import app_commands
import re
import os  # ✅ Added to access environment variables

# ✅ Get your token securely from environment variables
TOKEN = os.environ["asmr"]

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Slash Command Tree
tree = bot.tree

# 👮‍♂️ SCAM LINK BLOCKER
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    scam_keywords = ["free nitro", "nude", ".xyz", "airdrop", "porn"]
    if any(word in message.content.lower() for word in scam_keywords):
        try:
            await message.delete()
            await message.author.timeout(
                discord.utils.utcnow() + discord.timedelta(days=30),
                reason="Scam detected"
            )
            await message.channel.send(
                f"⚠️ {message.author.mention} has been timed out for posting scam links."
            )
        except Exception as e:
            print(f"Error: {e}")
    await bot.process_commands(message)

#- 🔐 SLASH COMMAND: /zmodpass
#-  @tree.command(name="zmodpass", description="Get the secret password.")
#-  @app_commands.checks.has_role("Z-Mod")  # Replace with your role name
#-  async def zmodpass(interaction: discord.Interaction):
#-     await interaction.response.send_message(
#-          "🔑 Your password is: `ASU-ZMOD-777`", ephemeral=True
#-      )

model_files = [
    "BMW_M5", "Lamborghini_Aventador", "Tesla_ModelS",
    "Supra_JDM", "Dodge_Challenger", "Nissan_GTR", "ASU_Mods_Pack"
]

# 🔐 Optional: password or file map (static demo)
passwords = {
    "BMW_M5": "bmwpass123",
    "Lamborghini_Aventador": "lambo456",
    "Tesla_ModelS": "tesla789",
    "Supra_JDM": "jdm420",
    "Dodge_Challenger": "challenger007",
    "Nissan_GTR": "gtrgodzilla",
    "ASU_Mods_Pack": "asu-modpack-v2"
}

# ⚙️ Autocomplete function
async def model_autocomplete(
    interaction: discord.Interaction, current: str
):
    return [
        app_commands.Choice(name=model, value=model)
        for model in model_files if current.lower() in model.lower()
    ][:25]  # Max 25 options

# 🔧 SLASH COMMAND: /pass
@tree.command(name="pass", description="Get password for a specific model")
@app_commands.describe(modelname="Choose a model or file name")
@app_commands.autocomplete(modelname=model_autocomplete)
@app_commands.checks.has_role("Z-Mod")
async def pass_command(interaction: discord.Interaction, modelname: str):
    password = passwords.get(modelname, "No password found for this model.")
    await interaction.response.send_message(
        f"📦 Model: **{modelname}**\n🔑 Password: `{password}`",
        ephemeral=True
    )

# ❌ Handle unauthorized users
@pass_command.error
async def pass_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message(
            "❌ You must verify your account to use this command.",
            ephemeral=True
        )

# 🚀 Sync slash commands
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot ready as {bot.user}")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="the whole server 👁️‍🗨️"
        )
    )
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()
bot.run(TOKEN)
