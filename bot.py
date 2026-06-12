import discord
from discord.ext import commands
from discord import app_commands
import datetime
import os
import re
import time
from collections import defaultdict
from flask import Flask, render_template_string
from threading import Thread

# ----------------- CONFIGURATIONS & STORAGE -----------------
server_prefixes = {}
log_channels = {}       
whitelist_users = {}    

# Anti-Spam Limits
SPAM_WINDOW = 5  
MAX_MESSAGES = 4 
user_msg_history = defaultdict(list)

BAD_WORDS = ["scamlink", "free-nitro", "fake-bot", "badword1"]
URL_PATTERN = r"(https?:\/\/[^\s]+)"

# 🔥 ADVANCED ANTI-NUKE MONITORING STORAGE
# Tracks admin actions within a 10-second threshold matrix window
NUKE_WINDOW = 10 
MAX_CHANNELS_DELETED = 3
MAX_ROLES_DELETED = 3
MAX_MEMBERS_KICKED = 3

admin_channel_deletions = defaultdict(list)
admin_role_deletions = defaultdict(list)
admin_member_kicks = defaultdict(list)

# ----------------- INTENTS SETUP -----------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.moderation = True
intents.guilds = True

def get_prefix(bot, message):
    if not message.guild:
        return '$'
    return server_prefixes.get(message.guild.id, '$')

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

# ----------------- 📡 GLOBAL BACKEND DATA STREAM -----------------
system_metrics = {
    "bot_status": "Initializing Engine Layer...",
    "anti_nuke_status": "ACTIVE & ARMED",
    "total_servers": 0,
    "last_nuke_trigger": "None Detected"
}

# ----------------- 🔥 AUTOMATIC SLASH SYNC ENGINE -----------------
@bot.event
async def on_ready():
    print(f'🔥 WICK-ULTIMATE HYBRID ALIVE AS {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Premium Anti-Nuke System Loaded"))
    
    system_metrics["bot_status"] = "ONLINE & SECURED"
    system_metrics["total_servers"] = len(bot.guilds)
    
    try:
        synced = await bot.tree.sync()
        print(f"✨ Successfully Synced {len(synced)} Slash Commands globally!")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")

# ----------------- 🚨 PREMIUM ANTI-NUKE CORE ENGINE -----------------

async def strip_admin_privileges(guild, member, reason_msg):
    """Emergency System Lockdown: Strips all roles containing high permissions from a rogue user"""
    global system_metrics
    system_metrics["last_nuke_trigger"] = f"Rogue Admin Detected: {member.name} on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    for role in member.roles:
        if role.permissions.administrator or role.permissions.manage_guild or role.permissions.ban_members:
            try:
                await member.remove_roles(role, reason="Anti-Nuke Emergency Strip Action")
            except Exception:
                pass # Safe check in case bot lacks capability for specific upper tree layer nodes

    await send_auto_log(guild, "🚨 ANTI-NUKE EMERGENCY LOCKDOWN", 
                        f"**Rogue Admin Isolated!**\nUser: {member.mention} ({member.id})\nReason: {reason_msg}\n*Action Executed: Removed administrative privileges.*", 
                        discord.Color.red())

@bot.event
async def on_guild_channel_delete(channel):
    """Monitors unauthorized rapid mass channel deletions"""
    guild = channel.guild
    async for entry in guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
        user = entry.user
        if user.id == bot.user.id or user.id == guild.owner_id:
            return
            
        if user.id in whitelist_users.get(guild.id, set()):
            return

        current_time = time.time()
        admin_channel_deletions[user.id] = [t for t in admin_channel_deletions[user.id] if current_time - t < NUKE_WINDOW]
        admin_channel_deletions[user.id].append(current_time)

        if len(admin_channel_deletions[user.id]) >= MAX_CHANNELS_DELETED:
            await strip_admin_privileges(guild, user, "Mass Channel Deletion Threshold Reached")

@bot.event
async def on_guild_role_delete(role):
    """Monitors unauthorized rapid mass role deletions"""
    guild = role.guild
    async for entry in guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
        user = entry.user
        if user.id == bot.user.id or user.id == guild.owner_id:
            return
            
        if user.id in whitelist_users.get(guild.id, set()):
            return

        current_time = time.time()
        admin_role_deletions[user.id] = [t for t in admin_role_deletions[user.id] if current_time - t < NUKE_WINDOW]
        admin_role_deletions[user.id].append(current_time)

        if len(admin_role_deletions[user.id]) >= MAX_ROLES_DELETED:
            await strip_admin_privileges(guild, user, "Mass Role Deletion Threshold Reached")

@bot.event
async def on_member_remove(member):
    """Monitors unauthorized rapid mass member kicks/bans"""
    guild = member.guild
    async for entry in guild.audit_logs(limit=1):
        if entry.action == discord.AuditLogAction.kick or entry.action == discord.AuditLogAction.ban:
            user = entry.user
            if user.id == bot.user.id or user.id == guild.owner_id:
                return
                
            if user.id in whitelist_users.get(guild.id, set()):
                return

            current_time = time.time()
            admin_member_kicks[user.id] = [t for t in admin_member_kicks[user.id] if current_time - t < NUKE_WINDOW]
            admin_member_kicks[user.id].append(current_time)

            if len(admin_member_kicks[user.id]) >= MAX_MEMBERS_KICKED:
                await strip_admin_privileges(guild, user, "Mass Member Extraction / Rogue Pruning Detected")

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
        if any(word in message.content.lower() for word in BAD_WORDS):
            await message.delete()
            return await send_auto_log(message.guild, "🛡️ AutoMod: Blocked Content", f"{message.author.mention} tried to use a prohibited word.", discord.Color.orange())

        if re.search(URL_PATTERN, message.content):
            await message.delete()
            return await send_auto_log(message.guild, "⚠️ AutoMod: Link Blocked", f"{message.author.mention} tried to share a link in a text channel.", discord.Color.orange())

        user_msg_history[user_id] = [t for t in user_msg_history[user_id] if current_time - t < SPAM_WINDOW]
        user_msg_history[user_id].append(current_time)
        
        if len(user_msg_history[user_id]) > MAX_MESSAGES:
            try:
                await message.delete()
                duration = datetime.timedelta(minutes=10)
                await message.author.timeout(duration, reason="Wick AutoMod: Anti-Spam Triggered")
                await send_auto_log(message.guild, "🚨 Rogue Spam Isolated", f"{message.author.mention} has been timed out for **10 Minutes** due to mass spamming.", discord.Color.red())
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
            embed.set_footer(text="Wick Engine Premium Security Logs")
            await channel.send(embed=embed)

# ----------------- 📜 HYBRID DASHBOARD (HELP) -----------------
def get_help_embed(prefix):
    embed = discord.Embed(
        title="🛡️ WICK-SECURE PRO ULTIMATE ENGINE",
        description=f"Advanced system commands. Prefix: `{prefix}` or Slash: `/`",
        color=discord.Color.from_rgb(47, 49, 54),
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="👑 SECURITY & TRUST (Whitelisting)", value="`whitelist @user` • `unwhitelist @user`", inline=False)
    embed.add_field(name="⚙️ BOT CONFIGURATION", value="`setlog #channel` • `setprefix [prefix]`", inline=False)
    embed.add_field(name="🔨 PUNISHMENT CONTROLS", value="`punish @user [timeout/kick/ban] [reason]`", inline=False)
    embed.add_field(name="🛡️ ANTI-NUKE SYSTEMS", value="`Automated Security Guard active across channels/roles.`", inline=False)
    embed.set_footer(text="Premium Security Node Operational Backend")
    return embed

@bot.command()
async def help(ctx):
    await ctx.send(embed=get_help_embed(ctx.prefix))

@bot.tree.command(name="help", description="Show the secure command dashboard.")
async def slash_help(interaction: discord.Interaction):
    prefix = server_prefixes.get(interaction.guild.id, '$')
    await interaction.response.send_message(embed=get_help_embed(prefix))

# ----------------- ⚙️ SYSTEM CONFIG (HYBRID) -----------------

@bot.command()
@commands.has_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel):
    log_channels[ctx.guild.id] = channel.id
    await ctx.send(f"📝 Security logs channel successfully set to {channel.mention}")

@bot.tree.command(name="setlog", description="Set the security logs channel.")
@app_commands.checks.has_permissions(administrator=True)
async def slash_setlog(interaction: discord.Interaction, channel: discord.TextChannel):
    log_channels[interaction.guild.id] = channel.id
    await interaction.response.send_message(f"📝 Security logs channel successfully set to {channel.mention}")

# ----------------- 👑 WHITELIST SYSTEM (HYBRID) -----------------

@bot.command()
@commands.has_permissions(administrator=True)
async def whitelist(ctx, member: discord.Member):
    guild_id = ctx.guild.id
    if guild_id not in whitelist_users: whitelist_users[guild_id] = set()
    whitelist_users[guild_id].add(member.id)
    await ctx.send(f"👑 {member.mention} has been added to the whitelist.")
    await send_auto_log(ctx.guild, "🛡️ Whitelist Update", f"{member.mention} was whitelisted by {ctx.author.mention}.", discord.Color.blue())

@bot.tree.command(name="whitelist", description="Add a user to the security whitelist.")
@app_commands.checks.has_permissions(administrator=True)
async def slash_whitelist(interaction: discord.Interaction, member: discord.Member):
    guild_id = interaction.guild.id
    if guild_id not in whitelist_users: whitelist_users[guild_id] = set()
    whitelist_users[guild_id].add(member.id)
    await interaction.response.send_message(f"👑 {member.mention} has been added to the whitelist.")
    await send_auto_log(interaction.guild, "🛡️ Whitelist Update", f"{member.mention} was whitelisted by {interaction.user.mention}.", discord.Color.blue())

# ----------------- 🔨 PUNISH SYSTEM (HYBRID) -----------------

@bot.command()
@commands.has_permissions(administrator=True)
async def punish(ctx, member: discord.Member, actionType: str, *, reason: str = "No reason provided"):
    actionType = actionType.lower()
    if member.top_role >= ctx.author.top_role:
        return await ctx.send("❌ Hierarchy error: Target user has a higher or equal role.")
    
    if actionType == "timeout":
        duration = datetime.timedelta(minutes=15)
        await member.timeout(duration, reason=reason)
        await ctx.send(f"⏳ {member.mention} has been manually muted (15m).")
    elif actionType == "kick":
        await member.kick(reason=reason)
        await ctx.send(f"👢 {member.mention} has been manually kicked.")
    elif actionType == "ban":
        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member.mention} has been manually banned.")

# ----------------- 🌐 FLASK PREMIUM LIVE DASHBOARD ENGINE -----------------
app = Flask('')

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Wick Ultimate Web Controller</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #2f3136; color: #fff; margin: 0; padding: 40px; }
        .card { background: #36393f; border-radius: 12px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); max-width: 700px; margin: auto; }
        h1 { color: #5865F2; border-bottom: 2px solid #40444b; padding-bottom: 10px; font-size: 28px; }
        .metric-group { margin: 20px 0; display: flex; justify-content: space-between; background: #2f3136; padding: 15px; border-radius: 8px; border-left: 5px solid #3ba55d; }
        .alert-box { background: #f04747; color: white; padding: 15px; border-radius: 8px; margin-top: 20px; font-weight: bold; }
        .footer { text-align: center; margin-top: 30px; color: #72767d; font-size: 12px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🛡️ Wick Ultimate Security Control Node</h1>
        <div class="metric-group"><strong>System Operation Core:</strong> <span>{{ metrics.bot_status }}</span></div>
        <div class="metric-group" style="border-left-color: #faa61a;"><strong>Anti-Nuke Defense Engine:</strong> <span>{{ metrics.anti_nuke_status }}</span></div>
        <div class="metric-group" style="border-left-color: #5865F2;"><strong>Total Connected Servers:</strong> <span>{{ metrics.total_servers }} servers</span></div>
        
        {% if "None" not in metrics.last_nuke_trigger %}
        <div class="alert-box">🚨 EMERGENCY WARNING:<br>{{ metrics.last_nuke_trigger }}</div>
        {% else %}
        <div class="metric-group" style="border-left-color: #72767d;"><strong>Last Anti-Nuke Event:</strong> <span>No threats detected</span></div>
        {% endif %}
    </div>
    <div class="footer">Wick Anti-Nuke Hybrid Automation System • Operational Platform Layer</div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(DASHBOARD_HTML, metrics=system_metrics)

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# Run the Discord Bot
bot.run(os.getenv('BOT_TOKEN'))
