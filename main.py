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

# 🔐 SLASH COMMAND: /zmodpass
@tree.command(name="zmodpass", description="Get the secret password.")
@app_commands.checks.has_role("Z-Mod")  # Replace with your role name
async def zmodpass(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🔑 Your password is: `ASU-ZMOD-777`", ephemeral=True
    )

# ❌ Handle unauthorized users
@zmodpass.error
async def zmodpass_error(interaction: discord.Interaction, error):
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

bot.run(TOKEN)
