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
async def on_message_edit(before, after):
    # Music-request channel ID
    music_request_channel_id = 1284207105548484780
    
    # Handle FlaviBot message edits (when embeds are added)
    if after.author.bot and after.author.name == 'FlaviBot':
        # Skip if already processed
        if after.id in processed_messages:
            return
        
        # Only process if embed was added in this edit
        if len(after.embeds) > len(before.embeds):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] FlaviBot message edited - EMBED ADDED! Moving to music-request...")
            print(f"[{timestamp}] Embeds: {len(after.embeds)}, Components: {len(after.components)}")
            
            try:
                processed_messages.add(after.id)
                
                # Get music-request channel
                music_request_channel = bot.get_channel(music_request_channel_id)
                if music_request_channel:
                    content = after.content if after.content else None
                    embeds = after.embeds if after.embeds else []
                    view = discord.ui.View.from_message(after) if after.components else None
                    
                    # Send the complete message
                    await music_request_channel.send(
                        content=content,
                        embeds=embeds,
                        view=view
                    )
                    print(f"[{timestamp}] Sent complete message with {len(embeds)} embed(s) and components")
                
                # Delete the original
                await after.delete()
                print(f"[{timestamp}] Deleted original message {after.id}")
            except Exception as e:
                print(f"[{timestamp}] ERROR: {e}")
                import traceback
                traceback.print_exc()

@bot.event
async def on_message(message):
    # Music-request channel ID
    music_request_channel_id = 1284207105548484780
    
    # Debug: Log ALL messages to see if we're receiving them
    if message.author.bot:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Bot message from {message.author.name} detected")
    
    # Move messages from the music bot (FlaviBot in this case)
    if message.author.bot and message.author.name == 'FlaviBot':
        # IGNORE slash command responses - they never have useful content
        if message.type == discord.MessageType.chat_input_command:
            return
            
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Processing FlaviBot message - Embeds: {len(message.embeds)}, Components: {len(message.components)}")
        
        # Debug: Show what embeds we have
        if message.embeds:
            for i, embed in enumerate(message.embeds):
                print(f"[{timestamp}] Embed {i}: title='{embed.title}', description='{embed.description[:50] if embed.description else 'None'}'")
        else:
            print(f"[{timestamp}] WARNING: No embeds found in message!")
        
        try:
            # Get music-request channel
            music_request_channel = bot.get_channel(music_request_channel_id)
            if music_request_channel:
                # Build message components
                content = message.content if message.content else None
                embeds = message.embeds if message.embeds else []
                view = discord.ui.View.from_message(message) if message.components else None
                
                print(f"[{timestamp}] About to send - Content: {bool(content)}, Embeds: {len(embeds)}, View: {bool(view)}")
                
                # Send the message with all its components
                sent_msg = await music_request_channel.send(
                    content=content,
                    embeds=embeds,
                    view=view
                )
                
                parts = []
                if content: parts.append("content")
                if embeds: parts.append(f"{len(embeds)} embed(s)")
                if view: parts.append("components")
                print(f"[{timestamp}] Sent message {sent_msg.id} with {', '.join(parts) if parts else 'empty content'}")
            
            # Delete original message
            await message.delete()
            print(f"[{timestamp}] Deleted original message {message.id}")
        except Exception as e:
            print(f"[{timestamp}] ERROR: Failed to process message {message.id}: {e}")
            import traceback
            traceback.print_exc()
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
