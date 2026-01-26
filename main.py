import discord
from discord.ext import commands
from datetime import datetime  # Add at top
import os

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
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

# Store message IDs temporarily to avoid duplicate processing
processed_messages = set()

@bot.event
async def on_message(message):
    # Music-request channel ID
    music_request_channel_id = 1284207105548484780
    
    # Temporary: Log ALL bot messages to identify the song info message
    if message.author.bot:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] BOT MESSAGE: {message.author.name} - Content: '{message.content[:50] if message.content else ''}', Embeds: {len(message.embeds)}, Components: {len(message.components)}")
        if message.embeds:
            for embed in message.embeds:
                print(f"[{timestamp}]   Embed title: '{embed.title}', description: '{embed.description[:50] if embed.description else ''}'")
    
    # Move messages from the music bot (FlaviBot in this case)
    if message.author.bot and message.author.name == 'FlaviBot':
        # IGNORE slash command responses - they never have useful content
        if message.type == discord.MessageType.chat_input_command:
            return
            
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Processing FlaviBot message - Embeds: {len(message.embeds)}, Components: {len(message.components)}")
        
        try:
            # Get music-request channel
            music_request_channel = bot.get_channel(music_request_channel_id)
            if music_request_channel:
                # Build message components
                content = message.content if message.content else None
                embeds = message.embeds if message.embeds else []
                view = discord.ui.View.from_message(message) if message.components else None
                
                # Send the message with all its components
                await music_request_channel.send(
                    content=content,
                    embeds=embeds,
                    view=view
                )
                
                parts = []
                if content: parts.append("content")
                if embeds: parts.append(f"{len(embeds)} embed(s)")
                if view: parts.append("components")
                print(f"[{timestamp}] Moved FlaviBot message with {', '.join(parts) if parts else 'empty content'} to #{music_request_channel.name}")
            
            # Delete original message
            await message.delete()
            print(f"[{timestamp}] Deleted original message {message.id}")
        except Exception as e:
            print(f"[{timestamp}] ERROR: Failed to process message {message.id}: {e}")
        return
    
    # Ignore other bot messages
    if message.author.bot:
        return
    
    # Move user messages containing /play to music-request channel
    if '/play' in message.content.lower():
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Moving /play command from {message.author} in #{message.channel}")
        
        try:
            # Get music-request channel
            music_request_channel = bot.get_channel(music_request_channel_id)
            if music_request_channel:
                # Send message content to music-request channel
                await music_request_channel.send(message.content)
                print(f"[{timestamp}] Moved /play message to #{music_request_channel.name}")
            
            await message.delete()
            print(f"[{timestamp}] Deleted original message {message.id}")
        except discord.Forbidden:
            print(f"[{timestamp}] ERROR: Missing 'Manage Messages' permission")
        except Exception as e:
            print(f"[{timestamp}] ERROR: {e}")
    
    await bot.process_commands(message)


bot.run(os.getenv("DISCORD_TOKEN"))
