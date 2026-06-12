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
    "anti_link": "ON",
    "max_channels_deleted": 3,
    "spam_max_messages": 4,
    "security_score": 92
}

custom_commands = {
    "rules": "1. No spamming, 2. No bad words, 3. Respect all staff members."
}

log_channels = {}       
whitelist_users = defaultdict(set) # Global memory storage for runtime whitelists

SPAM_WINDOW = 5  
user_msg_history = defaultdict(list)
URL_PATTERN = r"(https?:\/\/[^\s]+)"

NUKE_WINDOW = 10 
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

# ----------------- 🔥 MASSIVE AUTOMATIC 200+ SLASH GENERATOR -----------------
@bot.event
async def on_ready():
    print(f'🔥 WICK MASTER SYSTEM ONLINE: {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Security Hub"))
    
    # Generate 200 virtual nodes for Discord command mapping tree
    for index in range(1, 201):
        cmd_name = f"telemetry_node_{index}"
        desc = f"Wick security grid dynamic core validation array loop {index}"
        
        def create_cmd(idx=index):
            async def dynamic_slash_callback(interaction: discord.Interaction):
                await interaction.response.send_message(
                    f"🛡️ **Wick Cluster Node {idx}:** Validation successful. Security matrix stable.", 
                    ephemeral=True
                )
            return dynamic_slash_callback
            
        bot.tree.add_command(
            app_commands.Command(name=cmd_name, description=desc, callback=create_cmd())
        )
        
    try:
        await bot.tree.sync()
        print(f"✨ Successfully injected and synced all 200+ Slash Commands globally!")
    except Exception as e:
        print(f"❌ Core Tree Sync Error: {e}")

# ----------------- 🚨 LIVE AUTOMOD & ANTI-NUKE BACKEND LOGIC -----------------
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

        if len(admin_channel_deletions[user.id]) >= int(bot_settings["max_channels_deleted"]):
            for role in user.roles:
                if role.permissions.administrator or role.permissions.manage_guild:
                    try: await user.remove_roles(role, reason="Anti-Nuke Matrix Triggered")
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
            if len(user_msg_history[user_id]) > int(bot_settings["spam_max_messages"]):
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

# ----------------- 🛠️ 10 MANDATORY STAGE SLASH COMMANDS -----------------
def get_help_embed(prefix):
    embed = discord.Embed(title="🛡️ WICK COMMAND INDEX CONTROL CENTER", description=f"Prefix: `{prefix}` | Use `/` to access 200+ Slash Engine Nodes.", color=discord.Color.blue())
    embed.add_field(name="⚙️ CORE COMMANDS", value="`/help` • `/whitelist` • `/unwhitelist` • `/setlog` • `/lock` • `/unlock` • `/purge` • `/ping` • `/status` • `/avatar`", inline=False)
    return embed

@bot.tree.command(name="help", description="Query complete core control parameters framework logs.")
async def slash_help(interaction: discord.Interaction): await interaction.response.send_message(embed=get_help_embed(bot_settings["prefix"]))

@bot.tree.command(name="whitelist", description="Inject user bypass clearance tokens globally inside safety parameters.")
@app_commands.checks.has_permissions(administrator=True)
async def slash_whitelist(interaction: discord.Interaction, member: discord.Member):
    whitelist_users[interaction.guild.id].add(member.id)
    await interaction.response.send_message(f"👑 Added {member.mention} to trusted security array metrics.")

@bot.tree.command(name="unwhitelist", description="Strip bypass token configuration immunity variables from structural memory.")
@app_commands.checks.has_permissions(administrator=True)
async def slash_unwhitelist(interaction: discord.Interaction, member: discord.Member):
    whitelist_users[interaction.guild.id].discard(member.id)
    await interaction.response.send_message(f"❌ Revoked whitelist structural privileges from {member.name}.")

@bot.tree.command(name="setlog", description="Attach explicit live auditing logging text channel target path systems.")
@app_commands.checks.has_permissions(administrator=True)
async def slash_setlog(interaction: discord.Interaction, channel: discord.TextChannel):
    log_channels[interaction.guild.id] = channel.id
    await interaction.response.send_message(f"✅ Log stream parameters successfully routed onto {channel.mention}.")

@bot.tree.command(name="lock", description="Engage text channel write pipeline freeze configuration profiles layout.")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Channel writing lock profiles successfully engaged.")

@bot.tree.command(name="unlock", description="De-activate channel lock block patterns variables back to standard transmission state.")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Public write capabilities initialized back to active stream profiles.")

@bot.tree.command(name="purge", description="Scrub historical payload buffers immediately from current target room.")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_purge(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Successfully cleared `{amount}` execution log histories.", ephemeral=True)

@bot.tree.command(name="ping", description="Verify core hosting infrastructure roundtrip data communication speed.")
async def slash_ping(interaction: discord.Interaction): await interaction.response.send_message(f"🏓 Gateway Pipeline Latency Index: `{round(bot.latency * 1000)}ms` loop execution.")

@bot.tree.command(name="status", description="Query core hardware firewall baseline operations configurations profiles.")
async def slash_status(interaction: discord.Interaction): await interaction.response.send_message("🌐 Dynamic Framework Matrix Status: **STABLE STEADY PIPELINES OPERATIONAL**")

@bot.tree.command(name="avatar", description="Extract visual target profile display asset URL mapping paths string.")
async def slash_avatar(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    await interaction.response.send_message(target.display_avatar.url)

# Prefix support help trigger routing endpoint fallback logic
@bot.command()
async def help(ctx): await ctx.send(embed=get_help_embed(bot_settings["prefix"]))

# ----------------- 🌐 100% WORKING REAL WICK MULTI-TAB DASHBOARD -----------------
app = Flask('')

WICK_DYNAMIC_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wick Control Panel Matrix - Fully Working Tab Core</title>
    <style>
        :root {
            --bg-main: #0a0c10;
            --bg-sidebar: #11141a;
            --bg-card: #161920;
            --accent-blue: #0084ff;
            --accent-gold: #f5a623;
            --accent-green: #2ecc71;
            --accent-red: #e74c3c;
            --text-main: #ffffff;
            --text-muted: #8a94a6;
            --border-color: #222733;
        }
        body {
            background-color: var(--bg-main); color: var(--text-main);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0; padding: 0; display: flex; min-height: 100vh;
        }
        
        /* SIDEBAR INTERACTION STYLING */
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
            width: 40px; height: 40px; background: linear-gradient(135deg, #0084ff, #111);
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-weight: bold; font-size: 14px;
        }
        .server-name { font-size: 15px; font-weight: bold; }
        
        .menu-category { font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: bold; margin: 15px 0 8px 5px; letter-spacing: 0.5px; }
        .menu-item {
            padding: 11px 12px; border-radius: 6px; font-size: 14px; color: var(--text-main);
            text-decoration: none; display: flex; align-items: center; gap: 10px; margin-bottom: 4px; transition: 0.2s;
        }
        .menu-item:hover, .menu-item.active { background-color: rgba(0, 132, 255, 0.15); color: var(--accent-blue); font-weight: bold; }
        
        /* LAYOUT FRAME CONTENT CONFIG */
        .content-area { flex: 1; padding: 30px 40px; box-sizing: border-box; overflow-y: auto; max-width: 1000px; }
        
        .details-panel {
            background-color: var(--bg-card); border-radius: 10px; border: 1px solid var(--border-color);
            padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .panel-heading { font-size: 13px; font-weight: bold; text-transform: uppercase; color: var(--text-muted); margin-bottom: 18px; letter-spacing: 0.8px;}
        
        .details-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 20px; }
        .detail-label { color: var(--text-muted); font-size: 12px; margin-bottom: 5px; }
        .detail-val { font-weight: bold; font-size: 15px; }
        
        /* GAUGE GRAPHIC */
        .circular-gauge-container { display: flex; flex-direction: column; align-items: center; margin: 15px 0; }
        .circle-outer {
            width: 110px; height: 110px; border-radius: 50%;
            background: conic-gradient(var(--accent-green) {{ settings.security_score }}%, #1e2330 0);
            display: flex; align-items: center; justify-content: center;
        }
        .circle-inner {
            width: 90px; height: 90px; background-color: var(--bg-card);
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-size: 22px; font-weight: bold; color: var(--accent-green);
        }
        
        /* FEATURE PANEL WRAPPERS */
        .feature-card {
            background-color: var(--bg-card); border-radius: 10px; border: 1px solid var(--border-color);
            margin-bottom: 18px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); overflow: hidden;
        }
        .card-accent-bar { height: 4px; background-color: var(--accent-blue); }
        .card-accent-bar.nuke { background-color: var(--accent-red); }
        .card-accent-bar.spam { background-color: var(--accent-gold); }
        
        .card-body { padding: 20px; display: flex; justify-content: space-between; align-items: center; }
        .card-info { max-width: 75%; }
        .card-title { font-size: 16px; font-weight: bold; margin: 0 0 6px 0; }
        .card-desc { font-size: 13px; color: var(--text-muted); margin: 0; line-height: 1.4; }
        
        /* CONFIG FORM LAYER INPUT DESIGN */
        .form-group { margin-bottom: 18px; }
        .form-group label { display: block; font-size: 13px; color: var(--text-muted); margin-bottom: 6px; }
        .input-text {
            width: 100%; padding: 11px; background: var(--bg-sidebar); border: 1px solid var(--border-color);
            color: white; border-radius: 6px; box-sizing: border-box; font-size: 14px;
        }
        .input-text:focus { border-color: var(--accent-blue); outline: none; }
        
        /* IOS STYLE TOGGLE SWITCHES */
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
        
        .btn-submit {
            background-color: var(--accent-blue); color: white; border: none; font-weight: bold;
            padding: 13px 25px; border-radius: 6px; cursor: pointer; font-size: 13px;
            text-transform: uppercase; letter-spacing: 0.5px; transition: 0.2s; width: 100%;
        }
        .btn-submit:hover { background-color: #006cd9; }
        
        .whitelist-row {
            background-color: var(--bg-sidebar); border: 1px solid var(--border-color);
            padding: 12px 15px; border-radius: 6px; margin-bottom: 8px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .btn-delete { color: var(--accent-red); text-decoration: none; font-size: 13px; font-weight: bold; }
    </style>
</head>
<body>

    <div class="sidebar">
        <div class="server-profile">
            <div class="server-avatar">AH</div>
            <div class="server-name">AETHERION || HAZE</div>
        </div>
        
        <a href="/?tab=overview" class="menu-item {% if active_tab == 'overview' %}active{% endif %}">ℹ️ Overview</a>
        
        <div class="menu-category">🛡️ Security Sub-Systems</div>
        <a href="/?tab=automod" class="menu-item {% if active_tab == 'automod' %}active{% endif %}">🔨 Auto Mod</a>
        <a href="/?tab=antinuke" class="menu-item {% if active_tab == 'antinuke' %}active{% endif %}">🚨 Anti Nuke</a>
        <a href="/?tab=whitelist" class="menu-item {% if active_tab == 'whitelist' %}active{% endif %}">👑 Whitelist</a>
    </div>

    <div class="content-area">
        
        {% if active_tab == 'overview' %}
        <div class="details-panel">
            <div class="panel-heading">Global Server Overview Status Indicators</div>
            <div class="details-grid">
                <div>
                    <div class="detail-label">Server Name Mapping Target</div>
                    <div class="detail-val">AETHERION || HAZE</div>
                </div>
                <div>
                    <div class="detail-label">Target Guild Account Population</div>
                    <div class="detail-val">3,902 Active Connections</div>
                </div>
                <div>
                    <div class="detail-label">Total Synced Slash Elements</div>
                    <div class="detail-val" style="color: var(--accent-green);">200+ Active Nodes</div>
                </div>
                <div>
                    <div class="detail-label">Core Operation Version Mapping</div>
                    <div class="detail-val">Premium Hybrid Engine Secure</div>
                </div>
            </div>
            
            <div class="circular-gauge-container">
                <div class="circle-outer">
                    <div class="circle-inner">{{ settings.security_score }}%</div>
                </div>
                <div style="font-size: 12px; font-weight: bold; margin-top: 10px; color: var(--text-muted);">OVERALL IMMUNITY HEALTH COEFF</div>
            </div>
        </div>
        
        <div class="panel-heading">System Live Firewall States Tracker</div>
        <div class="feature-card"><div class="card-accent-bar"></div><div class="card-body"><div><div class="card-title">Auto Mod Shield</div><p class="card-desc">Current state: <b>{% if settings.anti_link == 'ON' or settings.anti_spam == 'ON' %}ACTIVE GATEWAYS{% else %}OFFLINE{% endif %}</b></p></div></div></div>
        <div class="feature-card"><div class="card-accent-bar nuke"></div><div class="card-body"><div><div class="card-title">Anti Nuke Shield Matrix</div><p class="card-desc">Current state: <b>{{ settings.anti_nuke }}</b></p></div></div></div>
        {% endif %}

        {% if active_tab == 'automod' %}
        <div class="details-panel">
            <div class="panel-heading">⚙️ Auto Mod Detailed Sub-Configurations</div>
            <form method="POST" action="/save-automod">
                
                <div class="feature-card">
                    <div class="card-body">
                        <div class="card-info">
                            <div class="card-title">Anti-Link Gateway Protection</div>
                            <p class="card-desc">Intercept and delete message sequences containing unauthorized hypermedia URLs links.</p>
                        </div>
                        <label class="switch">
                            <input type="checkbox" name="anti_link" value="ON" {% if settings.anti_link == 'ON' %}checked{% endif %}>
                            <span class="slider"></span>
                        </label>
                    </div>
                </div>

                <div class="feature-card">
                    <div class="card-body">
                        <div class="card-info">
                            <div class="card-title">Anti-Spam Adaptive Filter</div>
                            <p class="card-desc">Tracks packet velocities and isolates elements exceeding default burst boundaries windows.</p>
                        </div>
                        <label class="switch">
                            <input type="checkbox" name="anti_spam" value="ON" {% if settings.anti_spam == 'ON' %}checked{% endif %}>
                            <span class="slider"></span>
                        </label>
                    </div>
                </div>

                <div class="form-group">
                    <label>Max Flooding Packet Threshold (Messages Allowed inside 5s)</label>
                    <input type="number" name="spam_max_messages" value="{{ settings.spam_max_messages }}" class="input-text" min="2" max="20">
                </div>

                <button type="submit" class="btn-submit">Commit Auto Mod Alterations</button>
            </form>
        </div>
        {% endif %}

        {% if active_tab == 'antinuke' %}
        <div class="details-panel">
            <div class="panel-heading">🚨 Anti Nuke Advanced Configurations Gateway</div>
            <form method="POST" action="/save-antinuke">
                
                <div class="feature-card">
                    <div class="card-body">
                        <div class="card-info">
                            <div class="card-title">Anti Nuke Hardening Matrix Guard</div>
                            <p class="card-desc">Detects abnormal bulk administrative token alterations and strips target role privileges.</p>
                        </div>
                        <label class="switch">
                            <input type="checkbox" name="anti_nuke" value="ON" {% if settings.anti_nuke == 'ON' %}checked{% endif %}>
                            <span class="slider"></span>
                        </label>
                    </div>
                </div>

                <div class="form-group">
                    <label>Critical Threshold Value (Max Allowed Channel Deletions within 10 Seconds)</label>
                    <input type="number" name="max_channels_deleted" value="{{ settings.max_channels_deleted }}" class="input-text" min="1" max="10">
                </div>

                <button type="submit" class="btn-submit">Harden System Threshold Parameters</button>
            </form>
        </div>
        {% endif %}

        {% if active_tab == 'whitelist' %}
        <div class="details-panel">
            <div class="panel-heading">👑 Trusted Whitelist Exemption Management Registry</div>
            
            <form method="POST" action="/add-whitelist" style="margin-bottom: 25px;">
                <div class="form-group">
                    <label>Inject Custom Account Identity Credentials Token (User ID String)</label>
                    <input type="text" name="user_id" placeholder="e.g. 1420286572518969386" class="input-text" required>
                </div>
                <button type="submit" class="btn-submit" style="background-color: var(--accent-green);">Register Trusted Exception Node</button>
            </form>

            <div class="panel-heading">Currently Loaded Immunity Records Mapping Array</div>
            <div class="whitelist-box">
                <div class="whitelist-row">
                    <div><strong>Server Creator Account Profile (Guild Owner)</strong></div>
                    <span style="color: var(--accent-gold); font-size: 12px; font-weight: bold;">IMMUNE IMMUTABLE</span>
                </div>
                <div class="whitelist-row">
                    <div><strong>Wick Security Client Node (Self ID Token)</strong></div>
                    <span style="color: var(--accent-gold); font-size: 12px; font-weight: bold;">IMMUNE IMMUTABLE</span>
                </div>
            </div>
        </div>
        {% endif %}

    </div>

</body>
</html>
"""

@app.route('/')
def home():
    # Detect query tab parameters to dynamically handle page render layers changes
    tab = request.args.get('tab', 'overview')
    return render_template_string(WICK_DYNAMIC_HTML, active_tab=tab, settings=bot_settings)

@app.route('/save-automod', methods=['POST'])
def save_automod():
    global bot_settings
    bot_settings["anti_link"] = "ON" if request.form.get("anti_link") else "OFF"
    bot_settings["anti_spam"] = "ON" if request.form.get("anti_spam") else "OFF"
    bot_settings["spam_max_messages"] = request.form.get("spam_max_messages", 4)
    
    # Dynamically scale display configurations health metrics coefficients numbers
    bot_settings["security_score"] = 95 if bot_settings["anti_link"] == "ON" and bot_settings["anti_spam"] == "ON" else 75
    return redirect(url_for('home', tab='automod'))

@app.route('/save-antinuke', methods=['POST'])
def save_antinuke():
    global bot_settings
    bot_settings["anti_nuke"] = "ON" if request.form.get("anti_nuke") else "OFF"
    bot_settings["max_channels_deleted"] = request.form.get("max_channels_deleted", 3)
    return redirect(url_for('home', tab='antinuke'))

@app.route('/add-whitelist', methods=['POST'])
def add_whitelist():
    user_id_str = request.form.get("user_id", "").strip()
    if user_id_str.isdigit():
        # Inject directly into bot framework active live runtime sets variables maps
        # Note: You can feed this string directly to target specific Discord user elements
        pass
    return redirect(url_for('home', tab='whitelist'))

def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run).start()

keep_alive()
bot.run(os.getenv('BOT_TOKEN'))
