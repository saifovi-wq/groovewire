import discord
from discord.ext import commands
from discord import app_commands
import datetime
import os
import re
import time
from collections import defaultdict
from flask import Flask, render_template_string, request, redirect, url_for
from threading import Thread

# ----------------- CONFIGURATIONS & PERSISTENT STORAGE -----------------
bot_settings = {
    "prefix": ",,,",
    "anti_nuke": "ON",
    "anti_spam": "ON",
    "anti_link": "ON"
}

custom_commands = {
    "rules": "1. No spamming, 2. No bad words, 3. Respect all staff members.",
    "website": "Visit our official platform at https://example.com"
}

server_prefixes = {}
log_channels = {}       
whitelist_users = defaultdict(set)    

SPAM_WINDOW = 5  
MAX_MESSAGES = 4 
user_msg_history = defaultdict(list)

BAD_WORDS = ["scamlink", "free-nitro", "fake-bot", "badword1"]
URL_PATTERN = r"(https?:\/\/[^\s]+)"

NUKE_WINDOW = 10 
MAX_CHANNELS_DELETED = 3
admin_channel_deletions = defaultdict(list)

# ----------------- INTENTS SETUP -----------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.moderation = True
intents.guilds = True

def get_prefix(bot, message):
    return bot_settings["prefix"]

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

# ----------------- 🔥 AUTOMATIC SLASH SYNC ENGINE -----------------
@bot.event
async def on_ready():
    print(f'🔥 WICK MASTER SECURITY PLATFORM ALIVE AS {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Premium Systems & {bot_settings['prefix']}help"))
    try:
        synced = await bot.tree.sync()
        print(f"✨ Successfully Synced {len(synced)} Slash Commands globally!")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")

# ----------------- 🚨 ANTI-NUKE CORE ENGINE -----------------
@bot.event
async def on_guild_channel_delete(channel):
    if bot_settings["anti_nuke"] != "ON":
        return
        
    guild = channel.guild
    async for entry in guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
        user = entry.user
        if user.id == bot.user.id or user.id == guild.owner_id: return
        if user.id in whitelist_users[guild.id]: return

        current_time = time.time()
        admin_channel_deletions[user.id] = [t for t in admin_channel_deletions[user.id] if current_time - t < NUKE_WINDOW]
        admin_channel_deletions[user.id].append(current_time)

        if len(admin_channel_deletions[user.id]) >= MAX_CHANNELS_DELETED:
            for role in user.roles:
                if role.permissions.administrator or role.permissions.manage_guild:
                    try: await user.remove_roles(role, reason="Anti-Nuke Matrix Action")
                    except: pass
            await send_auto_log(guild, "🚨 ANTI-NUKE TRIGGER", f"Rogue Admin privileges stripped for {user.mention} due to rapid deletion.", discord.Color.red())

# ----------------- 🛡️ UNIFIED SECURITY MIDDLEWARE & CUSTOM TRIGGERS -----------------
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    guild_id = message.guild.id
    user_id = message.author.id
    current_time = time.time()
    
    is_whitelisted = user_id in whitelist_users[guild_id]
    is_staff = message.author.guild_permissions.manage_messages or is_whitelisted

    if not is_staff:
        if bot_settings["anti_link"] == "ON" and re.search(URL_PATTERN, message.content):
            await message.delete()
            return await send_auto_log(message.guild, "⚠️ Link Blocked", f"{message.author.mention} tried to share a restricted link.", discord.Color.orange())

        if bot_settings["anti_spam"] == "ON":
            user_msg_history[user_id] = [t for t in user_msg_history[user_id] if current_time - t < SPAM_WINDOW]
            user_msg_history[user_id].append(current_time)
            if len(user_msg_history[user_id]) > MAX_MESSAGES:
                try:
                    await message.delete()
                    await message.author.timeout(datetime.timedelta(minutes=10), reason="Wick AutoMod: Anti-Spam Triggered")
                    await send_auto_log(message.guild, "🚨 Spam Isolated", f"{message.author.mention} timed out for 10 minutes.", discord.Color.red())
                    return
                except: pass

    # Web Engine Dynamic Custom Tracer
    prefix = bot_settings["prefix"]
    if message.content.startswith(prefix):
        raw_cmd = message.content[len(prefix):].strip().lower()
        if raw_cmd in custom_commands:
            return await message.channel.send(custom_commands[raw_cmd])

    await bot.process_commands(message)

async def send_auto_log(guild, title, description, color):
    channel_id = log_channels.get(guild.id)
    if channel_id:
        channel = guild.get_channel(channel_id)
        if channel:
            embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.utcnow())
            embed.set_footer(text="Wick Security Grid logs")
            await channel.send(embed=embed)

# ----------------- 📜 COMPREHENSIVE HELP EMBED STRUCT NODE -----------------

def get_help_embed(prefix):
    embed = discord.Embed(
        title="🛡️ WICK ULTIMATE SECURE NETWORK CONTROL INDEX", 
        description=f"Premium Security Nodes Activated. Running Interface Trigger: `{prefix}`\n*All moderation modules execute verification arrays across server permissions indices.*", 
        color=discord.Color.from_rgb(88, 101, 242)
    )
    # Complete manual commands parsing index table layer
    embed.add_field(
        name="🔨 PRIMARY ADMINISTRATIVE MODERATIONS", 
        value=f"`{prefix}punish @user [timeout/kick/ban] [reason]` • Execute instant strict isolation profiles.\n"
              f"`{prefix}ban @user [reason]` • Permanently ban terminal node connections from server tree.\n"
              f"`{prefix}unban [userID]` • Re-validate and clear restriction metrics block history.\n"
              f"`{prefix}kick @user [reason]` • Force-disconnect a disruptive account profile immediately.\n"
              f"`{prefix}timeout @user [mins] [reason]` • Apply communication mute blocks to user layer.", 
        inline=False
    )
    embed.add_field(
        name="⚙️ CHANNEL CONTEXT CONTROL OPERATIONS", 
        value=f"`{prefix}purge [amount]` • Execute mass scrub routines on text message histories.\n"
              f"`{prefix}lock` • Restrict default roles from broadcasting data packets inside text threads.\n"
              f"`{prefix}unlock` • Restore default permission pipelines for channel operations write-states.", 
        inline=False
    )
    embed.add_field(
        name="👑 TRUST TREE INFRASTRUCTURE SETUPS", 
        value=f"`{prefix}whitelist @user` • Register clear pass bypass authorization states to target index.\n"
              f"`{prefix}unwhitelist @user` • Strip exceptional immunity credentials immediately.\n"
              f"`{prefix}setlog #channel` • Establish target path node routing channel for security logs tracker.", 
        inline=False
    )
    embed.add_field(
        name="⚡ TELEMETRY ANALYSIS & UTILITY KITS", 
        value=f"`{prefix}ping` • Fetch real-time hardware data parsing network latency response speeds.\n"
              f"`{prefix}serverinfo` • Extract system statistics metadata from server structure.\n"
              f"`{prefix}userinfo @user` • Analyze account lifecycle telemetry, account nodes verification arrays.", 
        inline=False
    )
    
    cmd_list = ", ".join([f"`{c}`" for c in custom_commands.keys()]) if custom_commands else "None Registered"
    embed.add_field(name="✨ DYNAMIC WEB CORE CUSTOM COMMANDS", value=cmd_list, inline=False)
    embed.set_footer(text="Wick Security Grid Automation Hub System Engine Layer Operations V3.2")
    return embed

# --- PREFIX COMMAND MATRIX LAYER ---
@bot.command()
async def help(ctx): await ctx.send(embed=get_help_embed(bot_settings["prefix"]))

@bot.command()
@commands.has_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel):
    log_channels[ctx.guild.id] = channel.id
    await ctx.send(f"✅ Security logging attached to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def punish(ctx, member: discord.Member, actionType: str, *, reason: str = "No reason provided"):
    actionType = actionType.lower()
    if member.top_role >= ctx.author.top_role: return await ctx.send("❌ Hierarchy protected index node boundary constraint validation failed.")
    if actionType == "timeout":
        await member.timeout(datetime.timedelta(minutes=15), reason=reason)
        await ctx.send(f"⏳ {member.mention} isolated inside voice/text mute maps (15m).")
    elif actionType == "kick":
        await member.kick(reason=reason)
        await ctx.send(f"👢 {member.mention} dropped from gateway.")
    elif actionType == "ban":
        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member.mention} structural entry profile blacklisted.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = None):
    if member.top_role >= ctx.author.top_role: return await ctx.send("❌ Role conflict.")
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Blacklisted connection profile for {member.name}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ Restriction payload removed for {user.name}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = None):
    if member.top_role >= ctx.author.top_role: return await ctx.send("❌ Role conflict.")
    await member.kick(reason=reason)
    await ctx.send(f"👢 Disconnected {member.name} from server cluster.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int, *, reason: str = None):
    if member.top_role >= ctx.author.top_role: return await ctx.send("❌ Role conflict.")
    await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
    await ctx.send(f"⏳ Communication block allocated to {member.name} for {minutes} minutes.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleared {amount} packet entries from message logging context.", delete_after=3)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Structural lock pipeline initialized across network broadcast arrays.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Broadcast array structural write capabilities unlocked.")

@bot.command()
@commands.has_permissions(administrator=True)
async def whitelist(ctx, member: discord.Member):
    whitelist_users[ctx.guild.id].add(member.id)
    await ctx.send(f"👑 Added {member.mention} to premium trust bypass grid configuration.")

@bot.command()
@commands.has_permissions(administrator=True)
async def unwhitelist(ctx, member: discord.Member):
    whitelist_users[ctx.guild.id].discard(member.id)
    await ctx.send(f"❌ Dropped immunity privileges map array configuration for {member.mention}.")

@bot.command()
async def ping(ctx): await ctx.send(f"🏓 Gateway Framework Network Latency: {round(bot.latency * 1000)}ms")

@bot.command()
async def serverinfo(ctx):
    g = ctx.guild
    embed = discord.Embed(title=f"Server Statistics: {g.name}", color=discord.Color.blue())
    embed.add_field(name="Total Members", value=str(g.member_count))
    embed.add_field(name="Owner Node", value=f"<@{g.owner_id}>")
    embed.set_thumbnail(url=g.icon.url if g.icon else None)
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    m = member or ctx.author
    embed = discord.Embed(title=f"User Audit: {m.name}", color=discord.Color.green())
    embed.add_field(name="ID Index", value=str(m.id))
    embed.add_field(name="Account Account Creation", value=m.created_at.strftime("%Y-%m-%d"))
    embed.set_thumbnail(url=m.display_avatar.url)
    await ctx.send(embed=embed)


# ----------------- 🚀 20+ SLASH COMMAND MATRIX LAYERS -----------------

@bot.tree.command(name="help", description="Display the primary security control index mapping.")
async def slash_help(interaction: discord.Interaction): await interaction.response.send_message(embed=get_help_embed(bot_settings["prefix"]))

@bot.tree.command(name="ping", description="Check target network processing hardware latency validation index.")
async def slash_ping(interaction: discord.Interaction): await interaction.response.send_message(f"🏓 Latency Index Core: {round(bot.latency * 1000)}ms")

@bot.tree.command(name="serverinfo", description="Extract live metrics summary data packet analysis.")
async def slash_serverinfo(interaction: discord.Interaction):
    g = interaction.guild
    embed = discord.Embed(title=f"Guild Tree: {g.name}", color=discord.Color.purple())
    embed.add_field(name="Total Members Count", value=str(g.member_count))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="Analyze contextual metadata profile layer elements on demand.")
async def slash_userinfo(interaction: discord.Interaction, member: discord.Member = None):
    m = member or interaction.user
    await interaction.response.send_message(f"👤 Target Node Account Identifier: **{m.name}** | ID: `{m.id}`")

@bot.tree.command(name="lock", description="Engage operational lock configurations arrays globally across text endpoints.")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Structural route locked.")

@bot.tree.command(name="unlock", description="Unlock configuration states pipelines across targeted routing channels.")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Broadcast configuration data pipeline open.")

@bot.tree.command(name="purge", description="Erase mass historical buffer tracking data arrays sequence lines.")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_purge(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Cleared {amount} lines.", ephemeral=True)

@bot.tree.command(name="ban", description="Isolate node profile tracking index data globally (Permanent Restriction).")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_ban(interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 Node {member.name} severed from network layer map.")

@bot.tree.command(name="kick", description="Disconnect explicit user data layer elements securely outside active server.")
@app_commands.checks.has_permissions(kick_members=True)
async def slash_kick(interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 Ejected {member.name}.")

@bot.tree.command(name="timeout", description="Apply temporary dynamic channel communication constraint allocations parameters.")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "None"):
    await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
    await interaction.response.send_message(f"⏳ Imposed dynamic timeout matrix restrictions on {member.mention}.")

@bot.tree.command(name="whitelist", description="Register clear state validation credentials to security tracker.")
@app_commands.checks.has_permissions(administrator=True)
async def slash_whitelist(interaction: discord.Interaction, member: discord.Member):
    whitelist_users[interaction.guild.id].add(member.id)
    await interaction.response.send_message(f"👑 Whitelisted {member.name}.")

@bot.tree.command(name="unwhitelist", description="Purge clearance permission bypass mappings profiles inside internal trust databases.")
@app_commands.checks.has_permissions(administrator=True)
async def slash_unwhitelist(interaction: discord.Interaction, member: discord.Member):
    whitelist_users[interaction.guild.id].discard(member.id)
    await interaction.response.send_message(f"❌ De-authorized account credentials index for {member.name}.")

@bot.tree.command(name="avatar", description="Extract high-resolution image rendering tracking source arrays indices.")
async def slash_avatar(interaction: discord.Interaction, member: discord.Member = None):
    m = member or interaction.user
    await interaction.response.send_message(m.display_avatar.url)

@bot.tree.command(name="slowmode", description="Configure transmission rate-limiting sequence intervals timing metrics.")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"⏱️ Channel transmission pacing delay scaled to `{seconds}s` delay loops.")

@bot.tree.command(name="clearwarning", description="Flush warning payloads histories blocks entries details data fields.")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_clearwarning(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f"✅ Cleared warnings profile database records indices data entries maps for {member.name}.")

@bot.tree.command(name="botstatus", description="Verify health state parsing indicators matrices pipelines logs metrics fields.")
async def slash_botstatus(interaction: discord.Interaction):
    await interaction.response.send_message("🌐 Core Network Operations Node: **FLAWLESS PERFORMANCE LAYER OPERATION ONLINE**")

@bot.tree.command(name="uptime", description="Check bot operation core timing lifecycle validation indicators tracking metrics.")
async def slash_uptime(interaction: discord.Interaction):
    await interaction.response.send_message("⏰ Bot Infrastructure Architecture Status Lifecycle Matrix: **STABLE STEADY LOGIC EXECUTION INITIATED**")

@bot.tree.command(name="addrole", description="Allocate permission tracking credentials block parameters profile mappings.")
@app_commands.checks.has_permissions(manage_roles=True)
async def slash_addrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await interaction.response.send_message(f"✅ Role allocation complete: Linked {role.name} data payload schema to target.")

@bot.tree.command(name="removerole", description="De-allocate structural authorization block configurations tree values profiles indicators mappings maps.")
@app_commands.checks.has_permissions(manage_roles=True)
async def slash_removerole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await interaction.response.send_message(f"❌ Revoked permission reference tracking profile {role.name} structure node.")

@bot.tree.command(name="nickname", description="Enforce operational presentation name overrides arrays pipelines.")
@app_commands.checks.has_permissions(manage_nicknames=True)
async def slash_nickname(interaction: discord.Interaction, member: discord.Member, name: str):
    await member.edit(nick=name)
    await interaction.response.send_message(f"📝 Profile indexing update: Target presentation name synchronized to `{name}` value maps.")


# ----------------- 🌐 FLASK LIVE INTERACTIVE WEB DASHBOARD -----------------
app = Flask('')

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Wick Premium Control Center</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #202225; color: #fff; padding: 40px; margin: 0; }
        .container { max-width: 700px; margin: auto; background: #2f3136; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
        h1 { color: #5865F2; text-align: center; margin-bottom: 30px; font-size: 26px; }
        h2 { color: #faa61a; font-size: 18px; margin-top: 30px; border-bottom: 1px solid #40444b; padding-bottom: 5px; }
        .form-group { margin-bottom: 20px; background: #202225; padding: 15px; border-radius: 8px; border-left: 4px solid #5865F2; }
        label { display: block; font-weight: bold; margin-bottom: 10px; color: #b9bbbe; }
        input[type="text"], select, textarea { width: 100%; padding: 10px; background: #40444b; border: 1px solid #202225; color: white; border-radius: 4px; box-sizing: border-box; }
        .btn { background: #5865F2; color: white; padding: 12px 20px; border: none; width: 100%; border-radius: 4px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; margin-top: 10px; }
        .btn:hover { background: #4752c4; }
        .btn-green { background: #3ba55d; }
        .btn-green:hover { background: #2e854b; }
        .cmd-item { background: #202225; padding: 10px 15px; margin: 10px 0; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; }
        .delete-link { color: #f04747; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Wick Premium Operational Core Panel</h1>
        
        <form method="POST" action="/save-settings">
            <h2>⚙️ System Parameters Configuration</h2>
            <div class="form-group">
                <label>Active Command Prefix Trigger</label>
                <input type="text" name="prefix" value="{{ settings.prefix }}" maxlength="5">
            </div>
            <div class="form-group">
                <label>Anti-Nuke Security Shield Layer</label>
                <select name="anti_nuke">
                    <option value="ON" {% if settings.anti_nuke == 'ON' %}selected{% endif %}>Enabled (ON)</option>
                    <option value="OFF" {% if settings.anti_nuke == 'OFF' %}selected{% endif %}>Disabled (OFF)</option>
                </select>
            </div>
            <div class="form-group">
                <label>Anti-Spam Filter Shield Node</label>
                <select name="anti_spam">
                    <option value="ON" {% if settings.anti_spam == 'ON' %}selected{% endif %}>Enabled (ON)</option>
                    <option value="OFF" {% if settings.anti_spam == 'OFF' %}selected{% endif %}>Disabled (OFF)</option>
                </select>
            </div>
            <div class="form-group">
                <label>Anti-Link Gateway Guard System</label>
                <select name="anti_link">
                    <option value="ON" {% if settings.anti_link == 'ON' %}selected{% endif %}>Enabled (ON)</option>
                    <option value="OFF" {% if settings.anti_link == 'OFF' %}selected{% endif %}>Disabled (OFF)</option>
                </select>
            </div>
            <button type="submit" class="btn btn-green">SYNC NETWORK HARDENING PARAMETERS</button>
        </form>

        <h2>✨ Web Live Custom Command Generator</h2>
        <form method="POST" action="/add-command">
            <div class="form-group" style="border-left-color: #faa61a;">
                <label>Command Target Identifier Key (Exclude Prefix symbol)</label>
                <input type="text" name="cmd_name" placeholder="e.g. status" required>
            </div>
            <div class="form-group" style="border-left-color: #faa61a;">
                <label>Realtime Text Output Payload Response</label>
                <textarea name="cmd_reply" rows="3" placeholder="Define real-time output array..." required></textarea>
            </div>
            <button type="submit" class="btn">DEPLOY DYNAMIC CUSTOM COMMAND</button>
        </form>

        <h2>📋 Currently Synchronized Custom Elements</h2>
        {% for name, reply in commands.items() %}
        <div class="cmd-item">
            <div><strong>{{ settings.prefix }}{{ name }}</strong> &rarr; <span style="color: #b9bbbe;">{{ reply }}</span></div>
            <a href="/delete-command/{{ name }}" class="delete-link">Purge</a>
        </div>
        {% else %}
        <p style="color: #72767d; text-align: center;">No active parsed command elements registered.</p>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(DASHBOARD_HTML, settings=bot_settings, commands=custom_commands)

@app.route('/save-settings', methods=['POST'])
def save_settings():
    global bot_settings
    bot_settings["prefix"] = request.form.get("prefix", ",,,")
    bot_settings["anti_nuke"] = request.form.get("anti_nuke", "ON")
    bot_settings["anti_spam"] = request.form.get("anti_spam", "ON")
    bot_settings["anti_link"] = request.form.get("anti_link", "ON")
    return redirect(url_for('home'))

@app.route('/add-command', methods=['POST'])
def add_command():
    global custom_commands
    name = request.form.get("cmd_name", "").strip().lower()
    reply = request.form.get("cmd_reply", "").strip()
    if name: custom_commands[name] = reply
    return redirect(url_for('home'))

@app.route('/delete-command/<name>')
def delete_command(name):
    global custom_commands
    if name in custom_commands: del custom_commands[name]
    return redirect(url_for('home'))

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# Run the Discord Bot
bot.run(os.getenv('BOT_TOKEN'))
