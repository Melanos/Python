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
    # Archive channel ID
    archive_channel_id = 1284207105548484780
    
    # Move messages from the music bot (FlaviBot in this case)
    if message.author.bot and message.author.name == 'FlaviBot':
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Moving FlaviBot message: {message.content[:100]}...")
        try:
            # Get archive channel
            archive_channel = bot.get_channel(archive_channel_id)
            if archive_channel:
                # Create embed with message info
                embed = discord.Embed(
                    description=message.content if message.content else "*No text content*",
                    color=discord.Color.blue(),
                    timestamp=message.created_at
                )
                embed.set_author(name=f"{message.author.name}", icon_url=message.author.display_avatar.url)
                embed.add_field(name="Original Channel", value=f"#{message.channel.name}", inline=True)
                embed.add_field(name="Message ID", value=message.id, inline=True)
                
                # Include attachments if any
                if message.attachments:
                    attachment_urls = "\n".join([att.url for att in message.attachments])
                    embed.add_field(name="Attachments", value=attachment_urls, inline=False)
                
                await archive_channel.send(embed=embed)
                print(f"[{timestamp}] Archived FlaviBot message to #{archive_channel.name}")
            
            await message.delete()
            print(f"[{timestamp}] Successfully moved message {message.id}")
        except Exception as e:
            print(f"[{timestamp}] ERROR: Failed to move message {message.id}: {e}")
        return
    
    # Ignore other bot messages
    if message.author.bot:
        return
    
    # Move user messages containing /play
    if '/play' in message.content.lower():
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Attempting to move '/play' from {message.author} in #{message.channel}: {message.content[:100]}...")
        
        try:
            # Get archive channel
            archive_channel = bot.get_channel(archive_channel_id)
            if archive_channel:
                # Create embed with message info
                embed = discord.Embed(
                    description=message.content,
                    color=discord.Color.orange(),
                    timestamp=message.created_at
                )
                embed.set_author(name=f"{message.author.name}", icon_url=message.author.display_avatar.url)
                embed.add_field(name="Original Channel", value=f"#{message.channel.name}", inline=True)
                embed.add_field(name="Message ID", value=message.id, inline=True)
                
                # Include attachments if any
                if message.attachments:
                    attachment_urls = "\n".join([att.url for att in message.attachments])
                    embed.add_field(name="Attachments", value=attachment_urls, inline=False)
                
                await archive_channel.send(embed=embed)
                print(f"[{timestamp}] Archived /play message to #{archive_channel.name}")
            
            await message.delete()
            print(f"[{timestamp}] Successfully moved message {message.id}")
        except discord.Forbidden:
            print(f"[{timestamp}] ERROR: Missing 'Manage Messages' permission to delete message {message.id}")
        except Exception as e:
            print(f"[{timestamp}] ERROR: Failed to move message {message.id}: {e}")
    
    await bot.process_commands(message)


bot.run(os.getenv("DISCORD_TOKEN"))
