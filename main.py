import time
import os
import discord
from discord.ext import commands
from discord import Embed
import random
import string

# Setup Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Command to generate a random code
def generate_code():
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(random.choices(characters, k=8))

# /paid_id Command to input user data and save to file
@bot.command()
async def paid_id(ctx):
    # Check if the user has the required role
    required_role = "ROOT"  # Replace with the role name you want to check
    if not any(role.name == required_role for role in ctx.author.roles):
        await ctx.send("You do not have permission to use this command.")
        return

    # Ask for the details
    await ctx.send("Please enter the Discord ID:")
    discord_id = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    discord_id = discord_id.content.strip()

    await ctx.send("Please enter the file name:")
    file_name = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    file_name = file_name.content.strip()

    # Generate a unique code
    code = generate_code()

    await ctx.send(f"Generated code: {code}. Please enter the code again to confirm:")

    confirmed_code = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    confirmed_code = confirmed_code.content.strip()

    if confirmed_code != code:
        await ctx.send("Code confirmation failed. Please try again.")
        return

    # Get current date and time
    current_date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    # Save to paid_id.txt
    with open("paid_id.txt", "a") as file:
        file.write(f"CODE: {code} {{DISCORD ID: {discord_id} FILE: {file_name} DATE: {current_date_time}}}\n")

    await ctx.send(f"Data saved successfully for CODE: {code}.")

# /get_code_d Command to get details related to a code
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

# Bot ready event
@bot.event
async def on_ready():
    print(f"✅ Bot ready as {bot.user}")

# Run the bot
bot.run("YOUR_DISCORD_TOKEN")
