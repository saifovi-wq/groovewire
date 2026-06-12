import discord
from discord.ext import commands
import datetime
import os
import re
import time
from collections import defaultdict

# ----------------- CONFIGURATIONS & STORAGE -----------------
server_prefixes = {}
log_channels = {}       # Guild ID -> Channel ID
whitelist_users = {}    # Guild ID -> Set of User IDs

# Anti-Spam configurations
SPAM_WINDOW = 5  
MAX_MESSAGES = 4 
user_msg_history = defaultdict(list)

# Bad Words for AutoMod Filter
BAD_WORDS = ["scamlink", "free-nitro", "fake-bot", "badword1"]
URL_PATTERN = r"(https?:\/\/[^\s]+)"

# ----------------- INTENTS SETUP -----------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.moderation = True

def get_prefix(bot, message):
    if not message.guild:
        return '??'
    return server_prefixes.get(message.guild.id, '??')

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'🔥 WICK-ULTIMATE SECURE ALIVE AS {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="🛡️ Absolute Security"))

# ----------------- 🛡️ UNIFIED AUTOMOD & SECURITY ENGINE -----------------
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    guild_id = message.guild.id
    user_id = message.author.id
    current_time = time.time()
    
    # Whitelist & Staff Check
    is_whitelisted = user_id in whitelist_users.get(guild_id, set())
    is_staff = message.author.guild_permissions.manage_messages or is_whitelisted

    if not is_staff:
        # 1. AUTOMOD: BAD WORD FILTER
        if any(word in message.content.lower() for word in BAD_WORDS):
            await message.delete()
            return await send_auto_log(message.guild, "🛡️ AutoMod: Bad Word Detected", f"{message.author.mention} banned word use korar chesta koreche.", discord.Color.orange())

        # 2. AUTOMOD: ANTI-LINK PROTECTION
        if re.search(URL_PATTERN, message.content):
            await message.delete()
            return await send_auto_log(message.guild, "⚠️ AutoMod: Link Blocked", f"{message.author.mention} text channel-e link share korer chesta koreche.", discord.Color.orange())

        # 3. AUTOMOD: ANTI-SPAM & ANTI-BOT SYSTEM
        user_msg_history[user_id] = [t for t in user_msg_history[user_id] if current_time - t < SPAM_WINDOW]
        user_msg_history[user_id].append(current_time)
        
        if len(user_msg_history[user_id]) > MAX_MESSAGES:
            try:
                await message.delete()
                # 10 Minutes Auto-Timeout for Spammers/Rogue Bots
                duration = datetime.timedelta(minutes=10)
                await message.author.timeout(duration, reason="Wick AutoMod: Anti-Spam Triggered")
                
                await send_auto_log(message.guild, "🚨 Rogue Spam Isolated", f"{message.author.mention}-ke mass spamming-er jonno **10 Minutes Timeout** kora hoyeche.", discord.Color.red())
                return
            except Exception as e:
                print(f"Anti-spam action error: {e}")

    # Standard command processing configuration
    await bot.process_commands(message)

# Helper Function: Auto Log Sender
async def send_auto_log(guild, title, description, color):
    channel_id = log_channels.get(guild.id)
    if channel_id:
        channel = guild.get_channel(channel_id)
        if channel:
            embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.utcnow())
            embed.set_footer(text="Wick Engine Security Logs")
            await channel.send(embed=embed)

# ----------------- ⚙️ SYSTEM CONFIG COMMANDS -----------------

@bot.command()
@commands.has_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel):
    log_channels[ctx.guild.id] = channel.id
    embed = discord.Embed(title="📝 Log Channel Configuration", description=f"Safolbhabe security logs channel {channel.mention}-e set kora hoyeche.", color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def setprefix(ctx, new_prefix: str):
    if len(new_prefix) > 5: return await ctx.send("❌ Prefix high-limit rules error (Max 5 chars).")
    server_prefixes[ctx.guild.id] = new_prefix
    await ctx.send(f"✅ Prefix successfully modified to `{new_prefix}`")

# ----------------- 👑 WHITELIST SYSTEM -----------------

@bot.command()
@commands.has_permissions(administrator=True)
async def whitelist(ctx, member: discord.Member):
    guild_id = ctx.guild.id
    if guild_id not in whitelist_users:
        whitelist_users[guild_id] = set()
    
    whitelist_users[guild_id].add(member.id)
    embed = discord.Embed(title="👑 Whitelist Protection Added", description=f"{member.mention}-ke security trust-list e add kora hoyeche. Ey user ekhon bypass permission pabe.", color=discord.Color.gold())
    await ctx.send(embed=embed)
    await send_auto_log(ctx.guild, "🛡️ Whitelist Update", f"{member.mention} has been added to the whitelist by {ctx.author.mention}.", discord.Color.blue())

@bot.command()
@commands.has_permissions(administrator=True)
async def unwhitelist(ctx, member: discord.Member):
    guild_id = ctx.guild.id
    if guild_id in whitelist_users and member.id in whitelist_users[guild_id]:
        whitelist_users[guild_id].remove(member.id)
        await ctx.send(f"✅ Removed {member.name} from whitelist.")
        await send_auto_log(ctx.guild, "🛡️ Whitelist Update", f"{member.mention} has been removed from the whitelist by {ctx.author.mention}.", discord.Color.red())
    else:
        await ctx.send("❌ User whitelist-e nei.")

# ----------------- 🔨 ADVANCED MODERATION -----------------

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if member.top_role >= ctx.author.top_role:
        return await ctx.send("❌ Hierarchy error: Target user high rank hierarchy access hold kore.")
    await member.ban(reason=reason)
    
    embed = discord.Embed(title="🔨 Member Permanent Ban", color=discord.Color.red())
    embed.add_field(name="Target Member", value=member.mention)
    embed.add_field(name="Executioner", value=ctx.author.mention)
    embed.add_field(name="Reason", value=reason or "None")
    await ctx.send(embed=embed)
    await send_auto_log(ctx.guild, "🔨 Member Banned", f"{member.name} ban content complete by {ctx.author.name}.", discord.Color.red())

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int, *, reason=None):
    if member.top_role >= ctx.author.top_role: return await ctx.send("❌ Role hierarchy control access block.")
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await ctx.send(f"⏳ {member.mention} successfully timed out for {minutes} minutes.")
    await send_auto_log(ctx.guild, "⏳ Timeout Log", f"{member.name} timed out for {minutes}m by {ctx.author.name}.", discord.Color.orange())

@bot.command()
@commands.has_permissions(manage_nicknames=True)
async def setnick(ctx, member: discord.Member, *, nickname: str = None):
    if member.top_role >= ctx.author.top_role: return await ctx.send("❌ Permission denied hierarchy context.")
    await member.edit(nick=nickname)
    await ctx.send("✏️ Nickname processing sequence completed.")

# ----------------- 📜 PREMIUM HELP DASHBOARD -----------------
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🛡️ WICK-SECURE PRO SYSTEM",
        description=f"Current Guild Runtime Prefix: `{ctx.prefix}`",
        color=discord.Color.from_rgb(47, 49, 54),
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="👑 SECURITY & TRUST (Whitelisting)", value="`whitelist @user` • `unwhitelist @user`", inline=False)
    embed.add_field(name="⚙️ BOT LOGS & CONFIG", value="`setlog #channel` • `setprefix [prefix]`", inline=False)
    embed.add_field(name="🛡️ ADMINISTRATIVE MODERATION", value="`ban @user [reason]` • `timeout @user [mins]` • `setnick @user [name]`", inline=False)
    embed.set_footer(text="Anti-Spam & AutoMod Active BACKGROUND WORKTIME")
    await ctx.send(embed=embed)

bot.run(os.getenv('BOT_TOKEN'))
