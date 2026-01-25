import discord
from discord.ext import commands
from datetime import datetime  # Add at top
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    
    # Send message to specific channel
    channel = bot.get_channel(1464696209309433876)
    if channel:
        await channel.send('Bot is now online and monitoring messages for "/play" commands to delete.')
    else:
        print('ERROR: Could not find the specified channel')

@bot.event
async def on_message(message):
    # Music-request channel ID
    music_request_channel_id = 1284207105548484780
    
    # Move messages from the music bot (FlaviBot in this case)
    if message.author.bot and message.author.name == 'FlaviBot':
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Moving FlaviBot message: {message.content[:100]}...")
        try:
            # Get music-request channel
            music_request_channel = bot.get_channel(music_request_channel_id)
            if music_request_channel:
                # Send message content to music-request channel
                content = message.content if message.content else "*Empty message*"
                await music_request_channel.send(content)
                print(f"[{timestamp}] Moved FlaviBot message to #{music_request_channel.name}")
            
            await message.delete()
            print(f"[{timestamp}] Successfully moved message {message.id}")
        except Exception as e:
            print(f"[{timestamp}] ERROR: Failed to move message {message.id}: {e}")
        return
    
    # Ignore other bot messages
    if message.author.bot:
        return
    
    # Move user messages containing /play to music-request channel
    if '/play' in message.content.lower():
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Attempting to move '/play' from {message.author} in #{message.channel}: {message.content[:100]}...")
        
        try:
            # Get music-request channel
            music_request_channel = bot.get_channel(music_request_channel_id)
            if music_request_channel:
                # Send message content to music-request channel
                await music_request_channel.send(message.content)
                print(f"[{timestamp}] Moved /play message to #{music_request_channel.name}")
            
            await message.delete()
            print(f"[{timestamp}] Successfully moved message {message.id}")
        except discord.Forbidden:
            print(f"[{timestamp}] ERROR: Missing 'Manage Messages' permission to delete message {message.id}")
        except Exception as e:
            print(f"[{timestamp}] ERROR: Failed to move message {message.id}: {e}")
    
    await bot.process_commands(message)


bot.run(os.getenv("DISCORD_TOKEN"))
