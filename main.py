import time
import os
import random
import string
from discord import app_commands, Embed
from discord.ext import commands
import discord
from flask import Flask
from threading import Thread
from files import files_data
from pro_file_info import pro_file_info
from paid_id import paid_id_data
from licence import license_descriptions
from discord.ext import tasks
from datetime import datetime, timedelta

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

# Function to generate a unique 8-character alphanumeric code
def generate_code():
    # Generate a random number between 1 and 9999
    random_number = random.randint(1, 9999)
    # Return the formatted code with leading zeros
    return f"epic{random_number:04d}"  # 4 digits, padded with leading zeros

# Check if the generated code already exists in the file
def check_code_exists(code):
    if os.path.exists("generated_codes.txt"):
        with open("generated_codes.txt", "r") as file:
            pass
            codes = file.readlines()
            codes = [line.strip() for line in codes]
            return code in codes
    return False


# Setup Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Autocomplete list for the pass command
async def model_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=model, value=model)
        for model in files_data if current.lower() in model.lower()
    ][:25]

@tree.command(name="pass", description="Get info & password for Mod file",guilds=[discord.Object(id=1232208366735196283), discord.Object(id=1358758393300648126)])
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


#################-------CODE-CMD--------#################
@tree.command(name="code", description="genarate code ",guild=discord.Object(id=1232208366735196283))
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_role("ROOT")
@commands.cooldown(1, 10, commands.BucketType.user)
async def code(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    while True:
        new_code = generate_code()
        if not check_code_exists(new_code):
            break
    
    # Ensure the file exists and create it if necessary
    if not os.path.exists("generated_codes.txt"):
        with open("generated_codes.txt", "w") as file:
            pass  # Create the file if it doesn't exist
            
    # Save the generated code to the file
    with open("generated_codes.txt", "a") as file:
        file.write(f"{new_code}\n")
    print(f"Code generated and saved: {new_code}")
    await interaction.followup.send(f"Generated Code: {new_code}") 


# Error handler
@code.error
async def code_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)

#################-------PAID-ID-CMD--------#################
async def code_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=code, value=code)
        for code in paid_id_data if current.lower() in code.lower()
    ][:25]

@tree.command(name="paid_id", description="customer",guild=discord.Object(id=1232208366735196283))
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_role("ROOT")
@app_commands.describe(code="Enter the customer's code")
@app_commands.autocomplete(code=code_autocomplete)
@commands.cooldown(1, 10, commands.BucketType.user)
async def paid_id(interaction: discord.Interaction, code: str):
    try:
        await interaction.response.defer(thinking=True)
        if code not in paid_id_data:
            await interaction.edit_original_response(content="code not found")
            return
    
        data = paid_id_data[code]
        Discord_id = data["Discord_id"]
        File_Name = data["File_Name"]
        For_ = data["For_"]
        Date = data["Date"]
        Via = data["Via"]
    
        # Embed with formatted block content
        embed = Embed(title=f" Access: {code}", color=0x2ecc71)
    
        embed.add_field(name="```|``` DISCORD ID", value=f"```{Discord_id}```", inline=False)
        embed.add_field(name="```|``` FILE NAME", value=f"```{File_Name}```", inline=False)
        embed.add_field(name="```|``` FOR", value=f"```{For_}```", inline=True)
        embed.add_field(name="```|``` DATE", value=f"```{Date}```", inline=True)
        embed.add_field(name="```|``` PAYMENT VIA", value=f"```{Via}```", inline=True)
    
        
    
        await interaction.edit_original_response(embed=embed)
    except Exception as e:
        await interaction.edit_original_response(content=f"Error: {e}")

# Error handler
@paid_id.error
async def paid_id_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)


#################-------TEST-CMD--------#################

#---@tree.command(
#---    name="test",
#---    description="A simple test command",
#---)
#---async def test_command(interaction: discord.Interaction):
#---    await interaction.response.send_message(" <a:size:1359124194130001931> hey  ")



#################-------pro-file-info-CMD--------#################
async def fid_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=fid, value=fid)
        for fid in pro_file_info if current.lower() in fid.lower()
    ][:25]

@tree.command(name="proinfo", description="Get info about paid files",guild=discord.Object(id=1232208366735196283))
@app_commands.checks.has_role("LEGIT")
@app_commands.describe(fid="Enter the file or select from the list.")
@app_commands.autocomplete(fid=fid_autocomplete)
@commands.cooldown(1, 10, commands.BucketType.user)
async def proinfo(interaction: discord.Interaction, fid: str):
    try:
        allowed_category_id = 1369408086967844924  # <-- Replace with your Category ID
        if interaction.channel.category_id != allowed_category_id:
            await interaction.response.send_message("ONLY WORK IN TICKET", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        if fid not in pro_file_info:
            await interaction.edit_original_response(content="No file named this. Please check the spelling.")
            return
    
        data = pro_file_info[fid]
        FIRST = data["FIRST"]
        SEC = data["SEC"]
        THIRD = data["THIRD"]
        FOUR = data["FOUR"]

        await interaction.edit_original_response(content=f"{FIRST}")
        await interaction.channel.send(content=SEC, allowed_mentions=discord.AllowedMentions.none())
        await interaction.channel.send(content=THIRD, allowed_mentions=discord.AllowedMentions.none())
        await interaction.channel.send(content=FOUR, allowed_mentions=discord.AllowedMentions.none())
    except Exception as e:
        await interaction.edit_original_response(content=f"Error: {e}")

# Error handler
@proinfo.error
async def proinfo_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message(" <a:epic_skull:1369682573726453841> You do not have permission to use this command.", ephemeral=True)
#################-------UPTIME--------#################
start_time = datetime.utcnow()
status_message = None  # to hold the live status message
bot_info_channel_id = 123456789012345678  # replace with your bot-info channel ID
status_message_id_path = "status_msg_id.txt"

@tasks.loop(minutes=5)
async def update_status_embed():
    global status_message

    now = datetime.utcnow()
    uptime = str(now - start_time).split('.')[0]  # clean HH:MM:SS

    # Check if /ping works
    try:
        synced = await tree.sync()
        command_status = "🟢 Working"
    except Exception as e:
        command_status = "🔴 Not Working"

    embed = discord.Embed(
        title="🤖 Bot Status Monitor",
        color=0x00ff00 if command_status == "🟢 Working" else 0xff0000
    )
    embed.add_field(name="Status", value="🟢 Online", inline=True)
    embed.add_field(name="Uptime", value=f"`{uptime}`", inline=True)
    embed.add_field(name="Command Check", value=command_status, inline=True)
    embed.set_footer(text="Last update")

    channel = bot.get_channel(bot_info_channel_id)
    if not channel:
        print("❌ Bot info channel not found!")
        return

    try:
        # Update the same message every time
        if os.path.exists(status_message_id_path):
            with open(status_message_id_path, "r") as f:
                msg_id = int(f.read())
                msg = await channel.fetch_message(msg_id)
                await msg.edit(embed=embed)
        else:
            msg = await channel.send(embed=embed)
            with open(status_message_id_path, "w") as f:
                f.write(str(msg.id))
    except Exception as e:
        print(f"❌ Error updating bot status message: {e}")


# Bot ready event
@bot.event
async def on_ready():
    await tree.sync()
    await tree.sync(guild=discord.Object(id=1232208366735196283)) 
    await tree.sync(guild=discord.Object(id=1358758393300648126)) # Add this line with your server ID
    print(f"✅ Bot ready as {bot.user}")
    update_status_embed.start()


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
