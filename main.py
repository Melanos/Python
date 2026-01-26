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
        embed = discord.Embed(
            title="🤖 Moderator Bot Online",
            description="Bot is now active and ready to moderate!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="📋 Available Commands",
            value=(
                "**`!delete <number>`** - Delete recent messages (1-100)\n"
                "**`!clear @user <number>`** - Delete messages from a specific user\n"
                "**`!slowmode <seconds>`** - Set channel slowmode (0-21600)\n"
                "**`!lock`** - Lock channel (mods only)\n"
                "**`!unlock`** - Unlock channel\n"
                "**`!commands`** or **`!help`** - Show help message"
            ),
            inline=False
        )
        embed.add_field(
            name="🔒 Permissions Required",
            value="Users need **Manage Messages** permission to use commands",
            inline=False
        )
        embed.set_footer(text="Use !help anytime to see this message again")
        await channel.send(embed=embed)
    else:
        print('ERROR: Could not find the specified channel')

# Remove Discord.py's default help command to use our custom one
bot.remove_command('help')

@bot.command(name='delete')
@commands.has_permissions(manage_messages=True)
async def delete_messages(ctx, amount: int = 10):
    """Delete a specified number of recent messages. Usage: !delete 10"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    notif_channel = bot.get_channel(1464696209309433876)
    
    if amount < 1 or amount > 100:
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - Please specify a number between 1 and 100.")
        return
    
    try:
        # Delete the command message itself
        await ctx.message.delete()
        
        # Delete the specified number of messages
        deleted = await ctx.channel.purge(limit=amount)
        
        # Send confirmation to notifications channel
        if notif_channel:
            await notif_channel.send(f"🗑️ {ctx.author.mention} deleted {len(deleted)} message(s) in {ctx.channel.mention}.")
        print(f"[{timestamp}] Deleted {len(deleted)} messages in #{ctx.channel.name} by {ctx.author}")
    except discord.Forbidden:
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - I don't have permission to delete messages!")
        print(f"[{timestamp}] ERROR: Missing permissions to delete messages")
    except Exception as e:
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - Error: {e}")
        print(f"[{timestamp}] ERROR: {e}")

@delete_messages.error
async def delete_error(ctx, error):
    notif_channel = bot.get_channel(1464696209309433876)
    if isinstance(error, commands.MissingPermissions):
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - You don't have permission to use this command!")
    elif isinstance(error, commands.BadArgument):
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - Please provide a valid number! Usage: `!delete 10`")

@bot.command(name='commands', aliases=['help', 'cmds'])
async def help_command(ctx):
    """Show help message with all available commands"""
    embed = discord.Embed(
        title="🤖 Moderator Bot - Commands",
        description="Here are all available moderation commands:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="�️ Message Management",
        value=(
            "**`!delete <number>`** - Delete recent messages (1-100)\n"
            "└ Example: `!delete 25`\n\n"
            "**`!clear @user <number>`** - Delete messages from a specific user\n"
            "└ Example: `!clear @John 10`"
        ),
        inline=False
    )
    embed.add_field(
        name="⚙️ Channel Management",
        value=(
            "**`!slowmode <seconds>`** - Set slowmode (0-21600 seconds)\n"
            "└ Example: `!slowmode 5` or `!slowmode 0` to disable\n\n"
            "**`!lock`** - Lock channel (only mods can talk)\n"
            "**`!unlock`** - Unlock channel"
        ),
        inline=False
    )
    embed.add_field(
        name="❓ Help",
        value="**`!commands`** or **`!help`** - Show this message",
        inline=False
    )
    embed.add_field(
        name="🔒 Required Permissions",
        value=(
            "**Manage Messages** - For !delete and !clear\n"
            "**Manage Channels** - For !slowmode, !lock, and !unlock"
        ),
        inline=False
    )
    embed.set_footer(text="Bot created for server moderation")
    notif_channel = bot.get_channel(1464696209309433876)
    if notif_channel:
        await notif_channel.send(embed=embed)
        await ctx.message.delete()

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear_user(ctx, member: discord.Member, amount: int = 10):
    """Delete messages from a specific user. Usage: !clear @user 20"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    notif_channel = bot.get_channel(1464696209309433876)
    
    if amount < 1 or amount > 100:
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - Please specify a number between 1 and 100.")
        return
    
    try:
        await ctx.message.delete()
        
        def check(msg):
            return msg.author.id == member.id
        
        # Delete messages from the specific user
        deleted = await ctx.channel.purge(limit=amount, check=check)
        
        if notif_channel:
            await notif_channel.send(f"🗑️ {ctx.author.mention} deleted {len(deleted)} message(s) from {member.mention} in {ctx.channel.mention}.")
        print(f"[{timestamp}] Deleted {len(deleted)} messages from {member} in #{ctx.channel.name} by {ctx.author}")
    except discord.Forbidden:
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - I don't have permission to delete messages!")
    except Exception as e:
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - Error: {e}")
        print(f"[{timestamp}] ERROR: {e}")

@clear_user.error
async def clear_error(ctx, error):
    notif_channel = bot.get_channel(1464696209309433876)
    if isinstance(error, commands.MissingPermissions):
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - You don't have permission to use this command!")
    elif isinstance(error, commands.MemberNotFound):
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - User not found! Usage: `!clear @user 10`")
    elif isinstance(error, commands.BadArgument):
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - Invalid arguments! Usage: `!clear @user 10`")

@bot.command(name='slowmode')
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int = 0):
    """Set channel slowmode. Usage: !slowmode 5"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    notif_channel = bot.get_channel(1464696209309433876)
    
    if seconds < 0 or seconds > 21600:
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - Slowmode must be between 0 and 21600 seconds (6 hours).")
        return
    
    try:
        await ctx.message.delete()
        await ctx.channel.edit(slowmode_delay=seconds)
        
        if seconds == 0:
            if notif_channel:
                await notif_channel.send(f"⏱️ {ctx.author.mention} disabled slowmode in {ctx.channel.mention}.")
            print(f"[{timestamp}] Slowmode disabled in #{ctx.channel.name} by {ctx.author}")
        else:
            if notif_channel:
                await notif_channel.send(f"⏱️ {ctx.author.mention} set slowmode to {seconds} second(s) in {ctx.channel.mention}.")
            print(f"[{timestamp}] Slowmode set to {seconds}s in #{ctx.channel.name} by {ctx.author}")
    except discord.Forbidden:
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - I don't have permission to manage channels!")
    except Exception as e:
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - Error: {e}")
        print(f"[{timestamp}] ERROR: {e}")

@slowmode.error
async def slowmode_error(ctx, error):
    notif_channel = bot.get_channel(1464696209309433876)
    if isinstance(error, commands.MissingPermissions):
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - You don't have permission to use this command!")
    elif isinstance(error, commands.BadArgument):
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - Please provide a valid number! Usage: `!slowmode 5`")

@bot.command(name='lock')
@commands.has_permissions(manage_channels=True)
async def lock_channel(ctx):
    """Lock the channel so only mods can send messages"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    notif_channel = bot.get_channel(1464696209309433876)
    
    try:
        await ctx.message.delete()
        # Deny @everyone from sending messages
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        
        if notif_channel:
            await notif_channel.send(f"🔒 {ctx.author.mention} locked {ctx.channel.mention}. Only moderators can send messages.")
        print(f"[{timestamp}] Channel #{ctx.channel.name} locked by {ctx.author}")
    except discord.Forbidden:
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - I don't have permission to manage channel permissions!")
    except Exception as e:
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - Error: {e}")
        print(f"[{timestamp}] ERROR: {e}")

@lock_channel.error
async def lock_error(ctx, error):
    notif_channel = bot.get_channel(1464696209309433876)
    if isinstance(error, commands.MissingPermissions):
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - You don't have permission to use this command!")

@bot.command(name='unlock')
@commands.has_permissions(manage_channels=True)
async def unlock_channel(ctx):
    """Unlock the channel"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    notif_channel = bot.get_channel(1464696209309433876)
    
    try:
        await ctx.message.delete()
        # Allow @everyone to send messages again
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
        
        if notif_channel:
            await notif_channel.send(f"🔓 {ctx.author.mention} unlocked {ctx.channel.mention}. Everyone can send messages again.")
        print(f"[{timestamp}] Channel #{ctx.channel.name} unlocked by {ctx.author}")
    except discord.Forbidden:
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - I don't have permission to manage channel permissions!")
    except Exception as e:
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - Error: {e}")
        print(f"[{timestamp}] ERROR: {e}")

@unlock_channel.error
async def unlock_error(ctx, error):
    notif_channel = bot.get_channel(1464696209309433876)
    if isinstance(error, commands.MissingPermissions):
        if notif_channel:
            await notif_channel.send(f"❌ {ctx.author.mention} - You don't have permission to use this command!")

@bot.event
async def on_message(message):
    # Don't respond to bot messages
    if message.author.bot:
        return
    
    # Process commands
    await bot.process_commands(message)


bot.run(os.getenv("DISCORD_TOKEN"))
