import discord
import time
import psutil
#import pyfactorybridge
from discord.ext import commands
from discord import app_commands
import subprocess
import os
import signal
from pyfactorybridge import API
from scraping import *
import random
import json
import sqlite3
from datetime import datetime, timedelta
import math

COOLDOWN_PERIOD = timedelta(hours=24)
COOLDOWN_PERIOD = timedelta(seconds=5)

# Connect to the database for the inventory tracking
conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

# Modify inventory table to store items as JSON strings
cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    user_id INTEGER PRIMARY KEY,
                    items TEXT,
                    doggos REAL DEFAULT 1.0,
                    last_claim TIMESTAMP
                )''')



try: #this is used to ensure the server is running whenever the discord bot is online, important for the api calls to function properly
    satisfactory = API(address = "127.0.0.1:7777", password ="=XXXX")  #replace this with your IP and port, 7777 is the default port for the API and use 127.0.0.1 if the server is hosted on the same device as the Bot
except Exception as e:
    subprocess.Popen("C:\Program Files (x86)\Steam\steamapps\common\SatisfactoryDedicatedServer\start.bat", shell=True) #replace with your path to your server's start.bat file
    satisfactory = API(address = "127.0.0.1:7777", password ="=XXXX")

# This is a loot table for the lizard doggo function, not fully implemented in this version
daily_items = {
    "SAM Ore": {"rarity": 1, "amount_range": (1, 1)},
    "Beryl Nut": {"rarity": 1, "amount_range": (1, 6)},
    "Biomass": {"rarity": 1, "amount_range": (1, 23)},
    "Solid Biofuel": {"rarity": 1, "amount_range": (1, 6)},
    "Blue Power Slug": {"rarity": 1, "amount_range": (1, 1)},
    "Yellow Power Slug": {"rarity": 1, "amount_range": (1, 1)},
    "Purple Power Slug": {"rarity": 1, "amount_range": (1, 1)},
    "Hog Remains": {"rarity": 1, "amount_range": (1, 1)},
    "Plasma Spitter Remains": {"rarity": 1, "amount_range": (1, 1)},
    "Alclad Aluminum Sheet": {"rarity": 1, "amount_range": (1, 14)}

}

#basic Discord bot definitions
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


server_process = None

def find_server_process():
    """Find the running FactoryServer.exe process and relink it to server_process."""
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'FactoryServer.exe' or proc.info['name'] == 'FactoryServer-Win64-Shipping-Cmd.exe':
            return psutil.Process(proc.info['pid'])  # Return the process object
    return None  # Return None if the process is not found


# Command to start the server
@bot.tree.command(name='start_server', description='Starts the server') #to ensure other users cannot access this make sure to configure it on the discord application end who all has access to it
async def start_server(interaction: discord.Interaction):
    num = False
    try:
        num = satisfactory.query_server_state()['serverGameState']['isGameRunning'] #API call to check if the server is running
        if num:
            await interaction.response.send_message("Server is already running.")
            return
    except Exception as e: #starts the server
        await interaction.response.send_message("Starting the Factory Server...")
        subprocess.Popen("C:\Program Files (x86)\Steam\steamapps\common\SatisfactoryDedicatedServer\start.bat", shell=True)
        num = None
        while num is None: #waits until the API returns the server is running to display that the server has started
            try:
                num = satisfactory.query_server_state()['serverGameState']['isGameRunning']
            except Exception as e:
                num = None
        await interaction.follow.send("Server started successfully!")


# Command to check if the server is running
@bot.tree.command(name='server_status', description='Return the status of the server')
@app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)  # 1 use per 5 seconds per user, to prevent spam
async def server_status(interaction: discord.Interaction):
    try:
        num = satisfactory.query_server_state()['serverGameState']['isGameRunning']
        if(num == True):
            await interaction.response.send_message(f"Server is up!")
        else:
            await interaction.response.send_message(f"Server is down ;(")
    except Exception as e:
        await interaction.response.send_message(f"Failed to obtain server status: {e}")
@server_status.error #if the user is within the cooldown window it will send them an error that only they can see
async def server_status_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"You're on cooldown. Try again in {round(error.retry_after, 1)} seconds.", ephemeral=True)


# Command to restart the server through API calls
@bot.tree.command(name='restart_server', description='Restarts the server') #to ensure other users cannot access this make sure to configure it on the discord application end who all has access to it
async def restart_server(interaction: discord.Interaction):
    global server_process
    try:
        num = satisfactory.query_server_state()['serverGameState']['isGameRunning']
        if(num == True): #saves the game to a temp file for safety, then issues an API call to close the server
            await interaction.response.send_message(f"Server is up!")
            server_process = find_server_process()
            satisfactory.save_game("temp")
            satisfactory.shutdown()
            server_process.wait()
        else:
            await interaction.response.send_message(f"Server is down ;(")

    except Exception as e:
        await interaction.response.send_message(f"Failed to obtain server status: {e}")
    await interaction.followup.send("Restarting the Factory Server...")
    subprocess.Popen("C:\Program Files (x86)\Steam\steamapps\common\SatisfactoryDedicatedServer\start.bat", shell=True) #starts the server again through the bat file
    num = None
    while num is None:
        try:
            num = satisfactory.query_server_state()['serverGameState']['isGameRunning']
        except Exception as e:
            num = None
    await interaction.followup.send("Server restarted successfully!") #sends message to indicate it has started properly

# Command to close the server
@bot.tree.command(name='close_server', description='Shut down the server') #to ensure other users cannot access this make sure to configure it on the discord application end who all has access to it
async def close_server(interaction: discord.Interaction):
    global server_process
    try:
        num = satisfactory.query_server_state()['serverGameState']['isGameRunning'] #checks if the server is running through a API call
        if(num == True): #saves the game and issues an API call to close the server
            await interaction.response.send_message(f"Closing server!")
            server_process = find_server_process()
            satisfactory.save_game("temp")
            satisfactory.shutdown()
            server_process.wait()
        else:
            await interaction.response.send_message(f"Server is already down ;(")
    except Exception as e:
        await interaction.response.send_message(f"Error encountered in shutdown sequence: {e}")
    while num: #wait until the server has been successfully shut down to send the message
        try:
            num = satisfactory.query_server_state()['serverGameState']['isGameRunning']
        except Exception as e:
            num = None
    await interaction.followup.send(f"Closed Server")

# Command to obtain how many players are currently online
@bot.tree.command(name='player_count', description='Returns the amount of active players')
@app_commands.checks.cooldown(1, 30, key=lambda i: i.user.id)  # 1 use per 30 seconds per user to prevent spam
async def player_count(interaction: discord.Interaction): #issues an API call to obtain the amount of players currently online
    try:
        num = satisfactory.query_server_state()['serverGameState']['numConnectedPlayers']
        if(num == 0):
            await interaction.response.send_message(f"Active players: 0. Get back to the factory!")
        else:
            await interaction.response.send_message(f"Active players: {num}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to obtain player count: {e}")
@player_count.error #error triggered when a user violates the cooldown
async def player_count_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"You're on cooldown. Try again in {round(error.retry_after, 1)} seconds.", ephemeral=True)


# Command to obtain how long the current save file has been running for
@bot.tree.command(name='game_duration', description='Returns the total amount of time spent on the server')
@app_commands.checks.cooldown(1, 60, key=lambda i: i.guild.id)  # 1 use per 60 seconds per guild to prevent spam
async def game_duration(interaction: discord.Interaction): #returns the total time spent on the save in hours
    global server_process
    try:
        await interaction.response.send_message(f"Game duration: {round((satisfactory.query_server_state()['serverGameState']['totalGameDuration']/3600),2)} hours")
    except Exception as e:
        await interaction.response.send_message(f"Failed to obtain total game duration: {e}")

@game_duration.error #error triggered when a user violates the cooldown
async def game_duration_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"Command is on cooldown. Try again in {round(error.retry_after, 1)} seconds.")


# Command to retrieve the ping of the server
@bot.tree.command(name='ping', description='Returns the average ping of the server')
@app_commands.checks.cooldown(1, 30, key=lambda i: i.user.id)  # 1 use per 30 seconds per user, to prevent spam
async def ping(interaction: discord.Interaction): #issues an API call to obtain the average ping statistic from the server in ticks per second
    global server_process
    try:
        await interaction.response.send_message(f"Ping: {round((satisfactory.query_server_state()['serverGameState']['averageTickRate']),2)} TPS")
    except Exception as e:
        await interaction.response.send_message(f"Failed to obtain ping: {e}")
@ping.error #error triggered when a user violates the cooldown
async def ping_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"You're on cooldown. Try again in {round(error.retry_after, 1)} seconds.", ephemeral=True)

# Command to get the save of the server, useful for usage on the Satisfactory calculator website
@bot.tree.command(name='get_save', description='Sends the save file to the user')
@app_commands.checks.cooldown(1, 60, key=lambda i: i.guild.id)  # 1 use per 60 seconds per guild, to prevent spam
async def get_save(interaction: discord.Interaction):
    num = False
    try:
        num = satisfactory.query_server_state()['serverGameState']['isGameRunning']
        if num: #obtains the current save from the server if it is online and sends a link to the satisfactory calculator website
            await interaction.response.send_message("Getting save:")
            satisfactory.save_game("public")
            file_path = (r'C:\Users\Connor Kuziemko\AppData\Local\FactoryGame\Saved\SaveGames\server\public.sav')  # Replace with your file path
            await interaction.followup.send(file=discord.File(file_path))
            await interaction.followup.send('https://satisfactory-calculator.com/en/interactive-map')
            return
    except Exception as e:
        await interaction.response.send_message("Unable to retrieve save")

@get_save.error #error triggered when a user violates the cooldown
async def get_save_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"Command is on cooldown. Try again in {round(error.retry_after, 1)} seconds.")

#command to retrieve statistics on the collectibles obtained in the current game save, utilizes the web scraping of the Satisfactory calculator website
@bot.tree.command(name='get_collectibles', description='Returns statistics on in-game collectibles')
@app_commands.checks.cooldown(1, 60, key=lambda i: i.guild.id)  # 1 use per 60 seconds per guild, to prevent spam
async def get_collectibles(interaction: discord.Interaction):
    await interaction.response.defer()
    satisfactory.save_game("scrape")
    web_scrape()
    hard = get_hard()
    blueSlug = get_blue_slug()
    yellowSlug = get_yellow_slug()
    purpleSlug = get_purple_slug()
    mercer = get_mercer()
    somersloop = get_somersloop()
    message = (f"{hard}/118 Hard Drives collected ({round((hard/118)*100,2)}%)\n{blueSlug}/596 Blue Slugs collected ({round((blueSlug/596)*100,2)}%)\n{yellowSlug}/389 Yellow Slugs collected ({round((yellowSlug/389)*100,2)}%)\n"
               f"{purpleSlug}/257 Purple Slugs collected ({round((purpleSlug/257)*100,2)}%)\n{mercer}/298 Mercer Spheres collected ({round((mercer/298)*100,2)}%)\n{somersloop}/106 Somersloops collected ({round((somersloop/106)*100,2)}%)")
    await interaction.followup.send(message)

@get_collectibles.error #error triggered when a user violates the cooldown
async def get_collectibles_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"Command is on cooldown. Try again in {round(error.retry_after, 1)} seconds.")

# Event when bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.tree.sync()  # Sync commands with Discord, currently setup as slash commands

#Work in progress commands, remove permissions through the discord application if you do not want to use them:
#command to simulate interacting with a lizard doggo, where the user who entered the command will obtain a random item from its loot table once a day, saved to the database created earlier
#DOES NOT SYNC WITH IN GAME INVENTORY
@bot.tree.command(name="lizard_doggo", description='Check your lizard doggo\'s inventory')
@app_commands.checks.cooldown(1, 86400, key=lambda i: i.user.id)  # 1 use per day per user
async def lizard_doggo(interaction: discord.Interaction):
    user_id = interaction.user.id
    command_name = 'doggo'

    cursor.execute('SELECT last_claim, doggos, items FROM inventory WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    current_time = None
    if not result:
        # If the user doesn't have an inventory, create one
        inventory = {}
        doggo = 1.0
        last_claim = None
    else:
        last_claim, doggo, items = result
        last_claim = datetime.fromisoformat(last_claim) if last_claim else None
        inventory = json.loads(items) if items else {}
    if result:
        current_time = datetime.now()

        # Calculate the remaining cooldown time
        if current_time - last_claim < COOLDOWN_PERIOD/doggo:
            time_remaining = (COOLDOWN_PERIOD - (current_time - last_claim))
            hours, remainder = divmod(time_remaining.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            await interaction.response.send_message(f"You must wait {hours}h {minutes}m {seconds}s for your lizard doggo to obtain more items.", ephemeral=True)
            return



    # Calculate weighted random selection based on rarity
    items = list(daily_items.keys())
    weights = [daily_items[item]["rarity"] for item in items]

    # Select a random item based on the defined rarity weights
    selected_item = random.choices(items, weights=weights, k=1)[0]

    # Randomly select the amount of the item based on the item's amount range
    min_amount, max_amount = daily_items[selected_item]["amount_range"]
    amount = random.randint(min_amount, max_amount)

    # Fetch user's inventory from database
    cursor.execute('SELECT items FROM inventory WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()




    # Add the daily item to the user's inventory
    if selected_item in inventory:
        inventory[selected_item] += amount
    else:
        inventory[selected_item] = amount

    # Save the updated inventory back to the database
    cursor.execute('''INSERT OR REPLACE INTO inventory (user_id, items, last_claim, doggos) 
                      VALUES (?, ?, ?, ?)''', (user_id, json.dumps(inventory), current_time, doggo))
    conn.commit()
    cursor.execute('''UPDATE inventory SET last_claim = ? WHERE user_id = ?''',
                   (current_time, user_id))
    conn.commit()

#WIP command to obtain the inventory of the player, in relation to what has been collected by the lizard doggo command
@bot.tree.command(name='inventory', description='View the items in your inventory.')
@app_commands.checks.cooldown(1, 10, key=lambda i: i.user.id)
async def inventory(interaction: discord.Interaction):
    user_id = interaction.user.id
    cursor.execute('Select items FROM inventory where user_id = ?', (user_id,))
    result = cursor.fetchone()

    if not result or result[0] == '{}':
        await interaction.response.send_message(f"{interaction.user.mention}, your inventory is empty.")
        return

    inventory = json.loads(result[0])

    # Format the inventory items
    inventory_message = f"**{interaction.user.display_name}'s Inventory:**\n"

    for item, amount in inventory.items():
        inventory_message += f"- **{item}**: {amount}\n"

    await interaction.response.send_message(inventory_message)

@inventory.error
async def inventory_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"Command is on cooldown. Try again in {round(error.retry_after, 1)} seconds.")



# Run the bot with your bot token
bot.run('XXXXXXX')
