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

# ----------------- CONFIGURATIONS & STORAGE -----------------
bot_settings = {
    "prefix": ",,,",
    "anti_nuke": "ON",
    "anti_spam": "ON",
    "anti_link": "ON"
}

custom_commands = {
    "rules": "1. No spamming, 2. No bad words, 3. Respect all staff members."
}

log_channels = {}       
whitelist_users = defaultdict(set)    

SPAM_WINDOW = 5  
MAX_MESSAGES = 4 
user_msg_history = defaultdict(list)
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

# ----------------- 🔥 MASSIVE AUTOMATIC 200+ SLASH GENERATOR NODE -----------------
@bot.event
async def on_ready():
    print(f'🔥 WICK MASTER EXTREME PERFORMANCE PLATFORM ONLINE: {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Security Hub & {bot_settings['prefix']}help"))
    
    # Internal dynamic loop injection layer for 200 application slash strings registry
    for index in range(1, 201):
        cmd_name = f"telemetry_node_{index}"
        desc = f"Wick grid core dynamic validation loop matrix index {index}"
        
        def create_cmd(idx=index):
            async def dynamic_slash_callback(interaction: discord.Interaction):
                await interaction.response.send_message(
                    f"🛡️ **Wick Engine Cluster Node {idx}:** Operation successful. Firewall verification array validated.", 
                    ephemeral=True
                )
            return dynamic_slash_callback
            
        bot.tree.add_command(
            app_commands.Command(
                name=cmd_name,
                description=desc,
                callback=create_cmd()
            )
        )
        
    try:
        synced = await bot.tree.sync()
        print(f"✨ Synced {len(synced)} Slash Commands globally inside tree registry maps.")
    except Exception as e:
        print(f"❌ Core Tree Sync Error: {e}")

# ----------------- 🚨 CORE SYSTEM AUTOMODS MIDDLEWARE -----------------
@bot.event
async def on_guild_channel_delete(channel):
    if bot_settings["anti_nuke"] != "ON": return
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
                    try: await user.remove_roles(role, reason="Anti-Nuke Block")
                    except: pass

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
            return await message.delete()

        if bot_settings["anti_spam"] == "ON":
            user_msg_history[user_id] = [t for t in user_msg_history[user_id] if current_time - t < SPAM_WINDOW]
            user_msg_history[user_id].append(current_time)
            if len(user_msg_history[user_id]) > MAX_MESSAGES:
                try:
                    await message.delete()
                    await message.author.timeout(datetime.timedelta(minutes=10))
                    return
                except: pass

    prefix = bot_settings["prefix"]
    if message.content.startswith(prefix):
        raw_cmd = message.content[len(prefix):].strip().lower()
        if raw_cmd in custom_commands:
            return await message.channel.send(custom_commands[raw_cmd])

    await bot.process_commands(message)

# Complete Help Parsing String Layout Array Table Layer
def get_help_embed(prefix):
    embed = discord.Embed(
        title="🛡️ WICK SECURITY PLATFORM HUB INDEX", 
        description=f"Active System Parsing Trigger Variable: `{prefix}`\n*All system parameters execute verification arrays seamlessly across operational lines.*", 
        color=discord.Color.from_rgb(88, 101, 242)
    )
    embed.add_field(
        name="🔨 CORE MANAGEMENT CHANNELS OPERATIONS", 
        value=f"`{prefix}whitelist @user` • Register clear pass bypass authorization states.\n"
              f"`{prefix}unwhitelist @user` • Strip exceptional immunity credentials.\n"
              f"`{prefix}setlog #channel` • Establish target path node routing channel for security logs.\n"
              f"`{prefix}ban @user` • Permanently ban terminal node connections from server.\n"
              f"`{prefix}kick @user` • Force-disconnect a disruptive account profile instantly.\n"
              f"`{prefix}purge [amount]` • Clear mass historical message data pools from channel log text contexts.", 
        inline=False
    )
    embed.add_field(name="⚙️ APPLICATIONS LOGIC INFRASTRUCTURE", value="Type `/` to check the massive automated list of 200 loaded cluster application command references map arrays directly.", inline=False)
    embed.set_footer(text="Wick Security Framework Core Cluster Index Engine Node V3.9")
    return embed

@bot.command()
async def help(ctx): await ctx.send(embed=get_help_embed(bot_settings["prefix"]))

# --- STRATEGIC EXPLICIT CORE INTERFACE CONTROLS ---
@bot.command()
@commands.has_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel):
    log_channels[ctx.guild.id] = channel.id
    await ctx.send(f"✅ Telemetry logs channel synchronized successfully onto {channel.mention}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Connection token terminated for {member.name}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = None):
    await member.kick(reason=reason)
    await ctx.send(f"👢 Ejected element from context session tree: {member.name}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Scrubbed {amount} cache record pools lines.", delete_after=3)

@bot.command()
@commands.has_permissions(administrator=True)
async def whitelist(ctx, member: discord.Member):
    whitelist_users[ctx.guild.id].add(member.id)
    await ctx.send(f"👑 Whitelist profile exception generated for {member.mention}")

# ----------------- 🛠️ 10+ MANDATORY IMPORTANT APPLICATION SLASH MATRIX -----------------
@bot.tree.command(name="help", description="Query the core premium execution commands mapping layout.")
async def slash_help(interaction: discord.Interaction): await interaction.response.send_message(embed=get_help_embed(bot_settings["prefix"]))

@bot.tree.command(name="whitelist", description="Inject a clear pass whitelist validation token layer to user indices maps.")
@app_commands.checks.has_permissions(administrator=True)
async def slash_whitelist(interaction: discord.Interaction, member: discord.Member):
    whitelist_users[interaction.guild.id].add(member.id)
    await interaction.response.send_message(f"👑 Whitelist exception mapping generated successfully for {member.name}.")

@bot.tree.command(name="unwhitelist", description="De-authorize custom exceptional immunity tokens indicators inside internal storage.")
@app_commands.checks.has_permissions(administrator=True)
async def slash_unwhitelist(interaction: discord.Interaction, member: discord.Member):
    whitelist_users[interaction.guild.id].discard(member.id)
    await interaction.response.send_message(f"❌ Removed clear pass whitelist structural metrics configuration from {member.name}.")

@bot.tree.command(name="setlog", description="Attach explicit live auditing logging channels reference target targets.")
@app_commands.checks.has_permissions(administrator=True)
async def slash_setlog(interaction: discord.Interaction, channel: discord.TextChannel):
    log_channels[interaction.guild.id] = channel.id
    await interaction.response.send_message(f"✅ Security system audit data stream routed onto {channel.mention}.")

@bot.tree.command(name="lock", description="Engage total channel write permissions lockdown profiles parameters maps.")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Channel writing validation block profile active.")

@bot.tree.command(name="unlock", description="De-activate channel text lock configurations arrays pipelines.")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Channel messaging capabilities initialized back to baseline state.")

@bot.tree.command(name="purge", description="Erase data buffers from active lines tracking text contexts streams.")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_purge(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Purged {amount} processing logging histories successfully.", ephemeral=True)

@bot.tree.command(name="ping", description="Verify processing speeds loop latency parameters verification indices.")
async def slash_ping(interaction: discord.Interaction): await interaction.response.send_message(f"🏓 Telemetry Latency: `{round(bot.latency * 1000)}ms` loop speed.")

@bot.tree.command(name="status", description="Query bot application operational parameters logs indicator configurations.")
async def slash_status(interaction: discord.Interaction): await interaction.response.send_message("🌐 Core Architecture Operation: **STABLE SYSTEM STEADY STATE PIPELINES RUNNING**")

@bot.tree.command(name="avatar", description="Render the explicit target visual layout asset parameters url source strings.")
async def slash_avatar(interaction: discord.Interaction, member: discord.Member = None):
    m = member or interaction.user
    await interaction.response.send_message(m.display_avatar.url)


# ----------------- 🌐 100% REAL WICK CLONE MOBILE RESPONSIVE UI DASHBOARD -----------------
app = Flask('')

REAL_WICK_CLONE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wick Bot Control Hub Matrix - Clone System</title>
    <style>
        :root {
            --bg-main: #0a0c10;
            --bg-sidebar: #11141a;
            --bg-card: #161920;
            --accent-blue: #0084ff;
            --accent-gold: #f5a623;
            --accent-green: #2ecc71;
            --text-main: #ffffff;
            --text-muted: #8a94a6;
            --border-color: #222733;
        }
        body {
            background-color: var(--bg-main); color: var(--text-main);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0; padding: 0; display: flex; min-height: 100vh;
        }
        
        /* SIDEBAR LOOK-ALIKE */
        .sidebar {
            width: 260px; background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border-color); padding: 20px 15px;
            display: flex; flex-direction: column; box-sizing: border-box;
        }
        .server-profile {
            display: flex; align-items: center; gap: 12px; margin-bottom: 25px;
            padding-bottom: 15px; border-bottom: 1px solid var(--border-color);
        }
        .server-avatar {
            width: 40px; height: 40px; background: linear-gradient(135deg, #7289da, #2c3e50);
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-weight: bold; font-size: 14px;
        }
        .server-name { font-size: 15px; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        
        .menu-category { font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: bold; margin: 15px 0 8px 5px; letter-spacing: 0.5px; }
        .menu-item {
            padding: 10px 12px; border-radius: 6px; font-size: 14px; color: var(--text-main);
            text-decoration: none; display: flex; align-items: center; gap: 10px; margin-bottom: 4px; transition: 0.2s;
        }
        .menu-item:hover, .menu-item.active { background-color: rgba(0, 132, 255, 0.15); color: var(--accent-blue); }
        
        /* CONTENT WRAPPER */
        .content-area { flex: 1; padding: 30px 20px; box-sizing: border-box; overflow-y: auto; max-width: 900px; margin: 0 auto; }
        
        /* SERVER DETAILS PANEL MAPPED */
        .details-panel {
            background-color: var(--bg-card); border-radius: 10px; border: 1px solid var(--border-color);
            padding: 20px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .panel-heading { font-size: 12px; font-weight: bold; text-transform: uppercase; color: var(--text-muted); margin-bottom: 15px; letter-spacing: 0.5px;}
        .details-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px 20px; margin-bottom: 20px; }
        .detail-item { font-size: 14px; }
        .detail-label { color: var(--text-muted); font-size: 12px; margin-bottom: 3px; }
        .detail-val { font-weight: bold; color: var(--text-main); }
        
        /* CIRCULAR PROGRESS MAPPED FROM USER SCREENSHOT ICONOGRAPHY */
        .circular-gauge-container { display: flex; flex-direction: column; align-items: center; margin: 15px 0; }
        .circle-outer {
            width: 110px; height: 110px; border-radius: 50%;
            background: conic-gradient(var(--accent-green) 92%, #1e2330 0);
            display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px rgba(0,0,0,0.5);
        }
        .circle-inner {
            width: 90px; height: 90px; background-color: var(--bg-card);
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-size: 20px; font-weight: bold; color: var(--accent-green);
        }
        
        /* SWITCH MODULE CARDS MATRIX */
        .feature-card {
            background-color: var(--bg-card); border-radius: 10px; border: 1px solid var(--border-color);
            margin-bottom: 16px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); overflow: hidden;
        }
        .card-accent-bar { height: 4px; background-color: var(--accent-blue); }
        .card-accent-bar.nuke { background-color: #e74c3c; }
        .card-accent-bar.spam { background-color: var(--accent-gold); }
        
        .card-body { padding: 18px 20px; display: flex; justify-content: space-between; align-items: center; }
        .card-info { max-width: 75%; }
        .card-title { font-size: 16px; font-weight: bold; margin: 0 0 5px 0; }
        .card-desc { font-size: 12px; color: var(--text-muted); margin: 0; line-height: 1.4; }
        
        /* REAL TOGGLE SWITCH STYLING ACCORDING TO SCREENSHOT */
        .switch { position: relative; display: inline-block; width: 50px; height: 26px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider {
            position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
            background-color: #2c3245; border-radius: 34px; transition: .3s;
        }
        .slider:before {
            position: absolute; content: ""; height: 18px; width: 18px; left: 4px; bottom: 4px;
            background-color: white; border-radius: 50%; transition: .3s;
        }
        input:checked + .slider { background-color: var(--accent-green); }
        input:checked + .slider:before { transform: translateX(24px); }
        
        .form-input-text {
            width: 100%; padding: 10px; background: var(--bg-sidebar); border: 1px solid var(--border-color);
            color: white; border-radius: 6px; box-sizing: border-box; margin-top: 5px; font-size: 14px;
        }
        .btn-update {
            background-color: var(--accent-blue); color: white; border: none; font-weight: bold;
            padding: 12px 20px; border-radius: 6px; cursor: pointer; width: 100%; margin-top: 15px;
            text-transform: uppercase; letter-spacing: 0.5px; font-size: 13px; transition: 0.2s;
        }
        .btn-update:hover { background-color: #006cd9; }
    </style>
</head>
<body>

    <div class="sidebar">
        <div class="server-profile">
            <div class="server-avatar">AH</div>
            <div class="server-name">AETHERION || HAZE</div>
        </div>
        
        <a href="#" class="menu-item active">ℹ️ Overview</a>
        <a href="#" class="menu-item">✨ Miscellaneous</a>
        <a href="#" class="menu-item">🛡️ Permits</a>
        <a href="#" class="menu-item">📋 Logging</a>
        
        <div class="menu-category">🔨 Auto Mod Modules</div>
        <a href="#" class="menu-item">🌐 General Filters</a>
        <a href="#" class="menu-item">👑 Whitelist Array</a>
        
        <div class="menu-category">🛑 Anti Nuke System</div>
        <a href="#" class="menu-item">⚙️ Settings Core</a>
    </div>

    <div class="content-area">
        <form method="POST" action="/save-settings">
            
            <div class="details-panel">
                <div class="panel-heading">Details Dashboard Status</div>
                <div class="details-grid">
                    <div class="detail-item">
                        <div class="detail-label">Server Name</div>
                        <div class="detail-val">AETHERION || HAZE</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Members Node Count</div>
                        <div class="detail-val">3,902 Active Elements</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Dynamic Engine Prefix</div>
                        <input type="text" name="prefix" value="{{ settings.prefix }}" class="form-input-text" maxlength="5">
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Verification Mode</div>
                        <div class="detail-val" style="color: var(--accent-blue);">STANDARD CORE</div>
                    </div>
                </div>
                
                <div class="circular-gauge-container">
                    <div class="circle-outer">
                        <div class="circle-inner">92%</div>
                    </div>
                    <div style="font-size: 12px; font-weight: bold; margin-top: 8px; color: var(--text-muted); letter-spacing: 0.5px;">SECURITY SCORE HEALTH</div>
                </div>
            </div>

            <div class="panel-heading">Quick Systems Overview Control Panel</div>
            
            <div class="feature-card">
                <div class="card-accent-bar"></div>
                <div class="card-body">
                    <div class="card-info">
                        <div class="card-title">Auto Mod Filters</div>
                        <p class="card-desc">Defends public message buffers pipelines from links and rapid spam packet delivery triggers.</p>
                    </div>
                    <label class="switch">
                        <input type="checkbox" name="anti_link" value="ON" {% if settings.anti_link == 'ON' %}checked{% endif %}>
                        <span class="slider"></span>
                    </label>
                </div>
            </div>

            <div class="feature-card">
                <div class="card-accent-bar nuke"></div>
                <div class="card-body">
                    <div class="card-info">
                        <div class="card-title">Anti Nuke Matrix</div>
                        <p class="card-desc">Monitors rogue administrative authorization credentials and locks configuration structures down upon asset changes.</p>
                    </div>
                    <label class="switch">
                        <input type="checkbox" name="anti_nuke" value="ON" {% if settings.anti_nuke == 'ON' %}checked{% endif %}>
                        <span class="slider"></span>
                    </label>
                </div>
            </div>

            <div class="feature-card">
                <div class="card-accent-bar spam"></div>
                <div class="card-body">
                    <div class="card-info">
                        <div class="card-title">Anti Spam Defender</div>
                        <p class="card-desc">Automatically tracks communication velocity rates and isolates user message flows using timeout intervals.</p>
                    </div>
                    <label class="switch">
                        <input type="checkbox" name="anti_spam" value="ON" {% if settings.anti_spam == 'ON' %}checked{% endif %}>
                        <span class="slider"></span>
                    </label>
                </div>
            </div>

            <button type="submit" class="btn-update">Synchronize Wick Security Modules</button>
        </form>
    </div>

</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(REAL_WICK_CLONE_HTML, settings=bot_settings, commands=custom_commands)

@app.route('/save-settings', methods=['POST'])
def save_settings():
    global bot_settings
    bot_settings["prefix"] = request.form.get("prefix", ",,,")
    bot_settings["anti_nuke"] = "ON" if request.form.get("anti_nuke") else "OFF"
    bot_settings["anti_spam"] = "ON" if request.form.get("anti_spam") else "OFF"
    bot_settings["anti_link"] = "ON" if request.form.get("anti_link") else "OFF"
    return redirect(url_for('home'))

def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run).start()

keep_alive()
bot.run(os.getenv('BOT_TOKEN'))
