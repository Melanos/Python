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
        print(f"[{timestamp}] Detected FlaviBot message...")
        print(f"[{timestamp}] Message details - Content: {bool(message.content)}, Embeds: {len(message.embeds)}, Components: {len(message.components)}, Attachments: {len(message.attachments)}")
        try:
            # Get music-request channel
            music_request_channel = bot.get_channel(music_request_channel_id)
            if music_request_channel:
                print(f"[{timestamp}] Found channel: #{music_request_channel.name}")
                
                # Build message components
                content = message.content if message.content else None
                embeds = message.embeds if message.embeds else None
                view = discord.ui.View.from_message(message) if message.components else None
                files = [await att.to_file() for att in message.attachments] if message.attachments else None
                
                # Send the message with all its components
                if embeds or content or view or files:
                    await music_request_channel.send(
                        content=content,
                        embeds=embeds,
                        view=view,
                        files=files
                    )
                    parts = []
                    if content: parts.append("content")
                    if embeds: parts.append(f"{len(embeds)} embed(s)")
                    if view: parts.append("components")
                    if files: parts.append(f"{len(files)} file(s)")
                    print(f"[{timestamp}] Sent message with {', '.join(parts)} to #{music_request_channel.name}")
                else:
                    print(f"[{timestamp}] WARNING: Message has no content, embeds, components, or attachments")
            else:
                print(f"[{timestamp}] ERROR: Could not find music-request channel with ID {music_request_channel_id}")
            
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
        print(f"[{timestamp}] Detected /play command from {message.author} in #{message.channel}: {message.content[:100]}...")
        
        try:
            # Get music-request channel
            music_request_channel = bot.get_channel(music_request_channel_id)
            if music_request_channel:
                # Send message content to music-request channel
                await music_request_channel.send(message.content)
                print(f"[{timestamp}] Sent /play message to #{music_request_channel.name}")
            else:
                print(f"[{timestamp}] ERROR: Could not find music-request channel with ID {music_request_channel_id}")
            
            await message.delete()
            print(f"[{timestamp}] Deleted original message {message.id}")
        except discord.Forbidden:
            print(f"[{timestamp}] ERROR: Missing 'Manage Messages' permission to delete message {message.id}")
        except Exception as e:
            print(f"[{timestamp}] ERROR: Failed to process message {message.id}: {e}")
    
    await bot.process_commands(message)


bot.run(os.getenv("DISCORD_TOKEN"))
