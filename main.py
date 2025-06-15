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


statuses = [
    "Orchestrating silent backend chaos.",
    "Playing with forbidden syscalls.",
    "Exploiting glitches for science.",
    "Refactoring the matrix, one bug at a time.",
    "Executing covert backend maneuvers.",
    "Tuning servers to borderline insanity.",
    "Harvesting logs like a shadow gardener.",
    "Playing chess with corrupted data.",
    "Compiling secrets under NDA.",
    "Automating the art of subtle sabotage.",
    "Running dirty scripts professionally.",
    "Silent guardian of digital entropy.",
    "Injecting controlled chaos discreetly.",
    "Playing with firewalls like a pyromaniac.",
    "Hijacking processes with surgical precision.",
    "Operating in the backend black market.",
    "Refining errors into features.",
    "Testing exploits with clinical detachment.",
    "Playing behind the scenes — no witnesses.",
    "Synchronizing with your worst nightmares."
]

user_activity = {}
TARGET_ROLE_NAME = "LEGIT"
BAN_DURATION_DAYS = 30
TIME_LIMIT_MINUTES = 180



# ----------- Cooldown Check to Avoid Rapid Restarts -----------

def check_restart_limit():
    path = "last_restart.txt"
    current_time = time.time()

    if os.path.exists(path):
        with open(path, "r") as f:
            last_time = float(f.read().strip())
        if current_time - last_time < 1200:  # 20 minutes cooldown
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
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ----------- Uptime Tracking -----------

start_time = datetime.utcnow()

# Channel ID where uptime embed will be posted (change this)
UPTIME_CHANNEL_ID = 1369435929604784262  # <-- Replace with your channel ID

# Message ID for uptime embed, will be set after first send
status_message_id = None

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
    for _ in range(100):
        candidate = generate_code()
        if not check_code_exists(candidate):
            new_code = candidate
            break

    if new_code is None:
        await interaction.followup.send("Failed to generate a unique code. Try again later.")
        return

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
        # Check if in correct category
        allowed_category_id = 1369408086967844924
        if interaction.channel.category_id != allowed_category_id:
            await interaction.response.send_message(
                "❌ This command only works in the PROFILES category!",
                ephemeral=True
            )
            return

        if fid not in pro_file_info:
            await interaction.response.send_message(
                "❌ File not found in database!",
                ephemeral=True
            )
            return

        data = pro_file_info[fid]
        
        # Build the full message
        full_message = ""
        for part in ['FIRST', 'SEC', 'THIRD', 'FOUR']:
            if part in data and data[part]:
                full_message += f"{data[part]}\n\n"
        
        # Smart splitting to avoid 2000 char limit
        if len(full_message) <= 2000:
            await interaction.response.send_message(full_message, ephemeral=True)
        else:
            # If too long, send as a text file
            await interaction.response.send_message(
                content="Here's the file info:",
                ephemeral=True,
                file=discord.File(
                    io.StringIO(full_message),
                    filename=f"{fid}_info.txt"
                )
            )

    except Exception as e:
        logging.error(f"Error in proinfo_command: {e}")
        await interaction.response.send_message(
            "⚠️ An error occurred while fetching file info!",
            ephemeral=True
        )



@tree.command(
    name="spread",
    description="Send a message to a specific channel by ID",
    guild=discord.Object(id=1232208366735196283)
)
@app_commands.describe(channel_id="The ID of the channel", message="Message to send")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_role("ROOT")  # Optional: permission check
@app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
async def spread(interaction: discord.Interaction, channel_id: str, message: str):
    try:
        channel = bot.get_channel(int(channel_id))
        if channel:
            await channel.send(message)
            await interaction.response.send_message(f"✅ Message sent to {channel.mention}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Channel not found.", ephemeral=True)
    except Exception as e:
        logging.error(f"Error in /spread: {e}")
        await interaction.response.send_message("⚠️ Failed to send message.", ephemeral=True)

@tree.command(
    name="epicembed",
    description="Send an embed message to a specific channel by ID",
    guild=discord.Object(id=1232208366735196283)
)
@app_commands.describe(
    channel_id="The ID of the channel",
    title="Embed title (optional)",
    description="Embed description",
    color="Embed color in HEX (e.g. #3498db, optional)"
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_role("ROOT")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
async def epicembed(
    interaction: discord.Interaction,
    channel_id: str,
    description: str,
    title: str = None,
    color: str = "#3498db"
):
    try:
        channel = bot.get_channel(int(channel_id))
        if not channel:
            await interaction.response.send_message("❌ Channel not found.", ephemeral=True)
            return
        
        # Parse color hex code, default to blue if invalid
        try:
            color_value = int(color.lstrip("#"), 16)
            embed_color = discord.Color(color_value)
        except:
            embed_color = discord.Color.blue()
        
        embed = discord.Embed(title=title, description=description, color=embed_color)
        await channel.send(embed=embed)
        
        await interaction.response.send_message(f"✅ Embed sent to {channel.mention}", ephemeral=True)
    except Exception as e:
        logging.error(f"Error in /epicembed: {e}")
        await interaction.response.send_message("⚠️ Failed to send embed.", ephemeral=True)




# ----------- Events -----------

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logging.info("------")
    try:
        guild = discord.Object(id=1232208366735196283)
        synced = await tree.sync(guild=guild)  # Only guild sync
        logging.info(f"Synced {len(synced)} commands.")
    except Exception as e:
        logging.error(f"Error syncing commands: {e}")
    chosen_status = random.choice(statuses)
    activity = discord.Activity(type=discord.ActivityType.playing, name=chosen_status)
    await bot.change_presence(status=discord.Status.online, activity=activity)


@bot.event
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"Slow down! Try again in {error.retry_after:.2f} seconds.", ephemeral=True
        )
    else:
        logging.error(f"Unhandled app command error: {error}")

@bot.event
async def on_member_join(member):
    user_activity[member.id] = {"joined": datetime.utcnow(), "got_role": False}
    try:
        await member.send("Thank you for joining the server!")
        print(f"Sent welcome DM to {member}")
    except Exception as e:
        print(f"Failed to send DM: {e}")

@bot.event
async def on_member_update(before, after):
    if not user_activity.get(after.id):
        return
    before_roles = set(before.roles)
    after_roles = set(after.roles)
    for role in after.roles:
        if role.name == TARGET_ROLE_NAME and role not in before_roles:
            user_activity[after.id]["got_role"] = True

@bot.event
async def on_member_remove(member):
    activity = user_activity.get(member.id)
    if not activity:
        return

    if activity["got_role"]:
        time_spent = datetime.utcnow() - activity["joined"]
        if time_spent < timedelta(minutes=TIME_LIMIT_MINUTES):
            try:
                # Ban for 30 days
                await member.ban(reason="Accessed file and left within short time.", delete_message_days=0)

                # Send DM
                try:
                    await member.send(
                                "<a:lightning:1369441281264189601> {user}, welcome to the NOTTHEREALEPIC Discord server.\n\n"
                                "<a:animetedrule:1234044425496428545> Read the rules and verify to get the LEGIT <a:animetedverify:1234049755844448329> role.\n\n"
                                "https://cdn.discordapp.com/attachments/1233831270866227271/1379393664962527292/nre_animated_low_mb.gif?ex=6842b6f5&is=68416575&hm=74ad849bb664592ec36bc71b9b8ebfed5b030cd6b9d14d18fe629c50ad6fbd58&"
                            )
                except:
                    print(f"Could not DM {member}")
            except:
                print(f"Could not ban {member}")
    # Cleanup
    user_activity.pop(member.id, None)

# ----------- Flask App for Uptime -----------

app = Flask("")

@app.route("/")
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# ----------- Main Entrypoint -----------

if __name__ == "__main__":
    # Start flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Run the bot
    TOKEN = os.getenv("asmr")  # Or replace with your token string here
    if not TOKEN:
        logging.error("DISCORD_TOKEN environment variable not set!")
        sys.exit(1)

    bot.run(TOKEN)
