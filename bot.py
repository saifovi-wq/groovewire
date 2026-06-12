import discord
from discord.ext import commands
from discord import app_commands
import datetime
import os
import re
import time
from collections import defaultdict
from flask import Flask
from threading import Thread

# ----------------- CONFIGURATIONS & STORAGE -----------------
server_prefixes = {}
log_channels = {}       
whitelist_users = {}    

SPAM_WINDOW = 5  
MAX_MESSAGES = 4 
user_msg_history = defaultdict(list)

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

# ----------------- 🔥 AUTOMATIC SLASH SYNC ENGINE -----------------
@bot.event
async def on_ready():
    print(f'🔥 WICK-ULTIMATE HYBRID ALIVE AS {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="🛡️ Prefix ?? & / Commands"))
    
    # Global Slash Commands Sync Kora (Discord Server-e code registration)
    try:
        synced = await bot.tree.sync()
        print(f"✨ Successfully Synced {len(synced)} Slash Commands globally!")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")

# ----------------- 🛡️ UNIFIED AUTOMOD & SECURITY ENGINE -----------------
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    guild_id = message.guild.id
    user_id = message.author.id
    current_time = time.time()
    
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
                duration = datetime.timedelta(minutes=10)
                await message.author.timeout(duration, reason="Wick AutoMod: Anti-Spam Triggered")
                await send_auto_log(message.guild, "🚨 Rogue Spam Isolated", f"{message.author.mention}-ke mass spamming-er jonno **10 Minutes Timeout** kora hoyeche.", discord.Color.red())
                return
            except Exception as e:
                print(f"Anti-spam action error: {e}")

    await bot.process_commands(message)

async def send_auto_log(guild, title, description, color):
    channel_id = log_channels.get(guild.id)
    if channel_id:
        channel = guild.get_channel(channel_id)
        if channel:
            embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.utcnow())
            embed.set_footer(text="Wick Engine Security Logs")
            await channel.send(embed=embed)

# ----------------- 📜 HYBRID DASHBOARD (HELP) -----------------
def get_help_embed(prefix):
    embed = discord.Embed(
        title="🛡️ WICK-SECURE PRO SYSTEM",
        description=f"Aponi Prefix `{prefix}` ebong Slash `/` duto diyei command run korte parben.",
        color=discord.Color.from_rgb(47, 49, 54),
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="👑 SECURITY & TRUST (Whitelisting)", value="`whitelist @user` • `unwhitelist @user`", inline=False)
    embed.add_field(name="⚙️ BOT LOGS & CONFIG", value="`setlog #channel` • `setprefix [prefix]`", inline=False)
    embed.add_field(name="🛡️ ADMINISTRATIVE MODERATION", value="`ban @user [reason]` • `timeout @user [mins]` • `setnick @user [name]`", inline=False)
    embed.set_footer(text="Anti-Spam & AutoMod Active BACKGROUND WORKTIME")
    return embed

# Prefix Help Command
@bot.command()
async def help(ctx):
    await ctx.send(embed=get_help_embed(ctx.prefix))

# Slash Help Command
@bot.tree.command(name="help", description="Show the secure command dashboard.")
async def slash_help(interaction: discord.Interaction):
    prefix = server_prefixes.get(interaction.guild.id, '??')
    await interaction.response.send_message(embed=get_help_embed(prefix))

# ----------------- ⚙️ SYSTEM CONFIG (HYBRID) -----------------

# Prefix SetLog
@bot.command()
@commands.has_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel):
    log_channels[ctx.guild.id] = channel.id
    await ctx.send(f"📝 Security logs channel successfully set to {channel.mention}")

# Slash SetLog
@bot.tree.command(name="setlog", description="Set the security logs channel.")
@app_commands.checks.has_permissions(administrator=True)
async def slash_setlog(interaction: discord.Interaction, channel: discord.TextChannel):
    log_channels[interaction.guild.id] = channel.id
    await interaction.response.send_message(f"📝 Security logs channel successfully set to {channel.mention}")

# Prefix SetPrefix
@bot.command()
@commands.has_permissions(administrator=True)
async def setprefix(ctx, new_prefix: str):
    if len(new_prefix) > 5: return await ctx.send("❌ Prefix high-limit rules error (Max 5 chars).")
    server_prefixes[ctx.guild.id] = new_prefix
    await ctx.send(f"✅ Prefix successfully modified to `{new_prefix}`")

# ----------------- 👑 WHITELIST SYSTEM (HYBRID) -----------------

# Prefix Whitelist
@bot.command()
@commands.has_permissions(administrator=True)
async def whitelist(ctx, member: discord.Member):
    guild_id = ctx.guild.id
    if guild_id not in whitelist_users: whitelist_users[guild_id] = set()
    whitelist_users[guild_id].add(member.id)
    await ctx.send(f"👑 {member.mention} has been added to the whitelist.")
    await send_auto_log(ctx.guild, "🛡️ Whitelist Update", f"{member.mention} whitelisted by {ctx.author.mention}.", discord.Color.blue())

# Slash Whitelist
@bot.tree.command(name="whitelist", description="Add a user to the security whitelist.")
@app_commands.checks.has_permissions(administrator=True)
async def slash_whitelist(interaction: discord.Interaction, member: discord.Member):
    guild_id = interaction.guild.id
    if guild_id not in whitelist_users: whitelist_users[guild_id] = set()
    whitelist_users[guild_id].add(member.id)
    await interaction.response.send_message(f"👑 {member.mention} has been added to the whitelist.")
    await send_auto_log(interaction.guild, "🛡️ Whitelist Update", f"{member.mention} whitelisted by {interaction.user.mention}.", discord.Color.blue())

# ----------------- 🔨 ADVANCED MODERATION (HYBRID) -----------------

# Prefix Timeout
@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int, *, reason: str = None):
    if member.top_role >= ctx.author.top_role: return await ctx.send("❌ Role hierarchy control access block.")
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await ctx.send(f"⏳ {member.mention} successfully timed out for {minutes} minutes.")
    await send_auto_log(ctx.guild, "⏳ Timeout Log", f"{member.name} timed out by {ctx.author.name}.", discord.Color.orange())

# Slash Timeout
@bot.tree.command(name="timeout", description="Timeout/Mute a mischievous member.")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = None):
    if member.top_role >= interaction.user.top_role: 
        return await interaction.response.send_message("❌ Role hierarchy control access block.", ephemeral=True)
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await interaction.response.send_message(f"⏳ {member.mention} successfully timed out for {minutes} minutes.")
    await send_auto_log(interaction.guild, "⏳ Timeout Log", f"{member.name} timed out by {interaction.user.name}.", discord.Color.orange())

# Prefix Ban
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = None):
    if member.top_role >= ctx.author.top_role: return await ctx.send("❌ Hierarchy error.")
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Banned {member.mention}")
    await send_auto_log(ctx.guild, "🔨 Member Banned", f"{member.name} banned by {ctx.author.name}.", discord.Color.red())

# Slash Ban
@bot.tree.command(name="ban", description="Permanently ban a user from the server.")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if member.top_role >= interaction.user.top_role: 
        return await interaction.response.send_message("❌ Hierarchy error.", ephemeral=True)
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 Banned {member.mention}")
    await send_auto_log(interaction.guild, "🔨 Member Banned", f"{member.name} banned by {interaction.user.name}.", discord.Color.red())

# ----------------- DUMMY WEB SERVER FOR RENDER PORT BINDING -----------------
app = Flask('')

@app.route('/')
def home():
    return "Wick Ultimate Hybrid Security Engine Alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# Run the Discord Bot
bot.run(os.getenv('BOT_TOKEN'))
