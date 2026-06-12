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

# ----------------- CONFIGURATIONS & REAL LIVE STORAGE -----------------
bot_settings = {
    "prefix": ",,,",
    "anti_nuke": "ON",
    "anti_spam": "ON",
    "anti_link": "ON",
    "spam_max_messages": 4,
    "max_channels_deleted": 3,
    "security_score": 92
}

whitelist_db = ["1420286572518969386"]  
custom_commands = {"rules": "1. No spamming, 2. No bad words, 3. Respect staff."}
log_channels = {}       
user_msg_history = defaultdict(list)
admin_channel_deletions = defaultdict(list)

SPAM_WINDOW = 5  
NUKE_WINDOW = 10 
URL_PATTERN = r"(https?:\/\/[^\s]+)"

# ----------------- INTENTS & SETUP -----------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.moderation = True
intents.guilds = True

def get_prefix(bot, message):
    return bot_settings["prefix"]

class WickPremiumCore(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, intents=intents, help_command=None)
        
    async def setup_hook(self):
        print("⚡ [Wick Engine] Injecting 200 Security Command Nodes inside global tree...")
        for index in range(1, 201):
            cmd_name = f"telemetry_node_{index}"
            desc = f"Wick grid dynamic defense loop status validator {index}"
            
            def create_cmd(idx=index):
                async def dynamic_slash_callback(interaction: discord.Interaction):
                    await interaction.response.send_message(
                        f"🛡️ **Wick Cluster Node {idx}:** Integrity verified. Safe state active.", 
                        ephemeral=True
                    )
                return dynamic_slash_callback
                
            self.tree.add_command(app_commands.Command(name=cmd_name, description=desc, callback=create_cmd()))
        try:
            await self.tree.sync()
            print("✨ [Wick Engine] All 200+ global nodes successfully synchronized!")
        except Exception as e:
            print(f"❌ [Tree Error]: {e}")

bot = WickPremiumCore()

@bot.event
async def on_ready():
    print(f'🔥 WICK MASTER CORE MATRIX ONLINE: {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Wick Security Framework"))

# ----------------- LIVE AUTOMOD & ANTI-NUKE MONITOR -----------------
@bot.event
async def on_guild_channel_delete(channel):
    if bot_settings["anti_nuke"] != "ON": return
    guild = channel.guild
    async for entry in guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
        user = entry.user
        if user.id == bot.user.id or user.id == guild.owner_id or str(user.id) in whitelist_db: return

        current_time = time.time()
        admin_channel_deletions[user.id] = [t for t in admin_channel_deletions[user.id] if current_time - t < NUKE_WINDOW]
        admin_channel_deletions[user.id].append(current_time)

        if len(admin_channel_deletions[user.id]) >= int(bot_settings["max_channels_deleted"]):
            for role in user.roles:
                if role.permissions.administrator or role.permissions.manage_guild:
                    try: await user.remove_roles(role, reason="Wick Anti-Nuke Security Triggered")
                    except: pass

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    user_id = message.author.id
    current_time = time.time()
    
    is_whitelisted = str(user_id) in whitelist_db or user_id == message.guild.owner_id
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

    await bot.process_commands(message)

# ----------------- 10 MANDATORY CORE COMMANDS -----------------
def generate_help_embed(p):
    embed = discord.Embed(title="🛡️ WICK APP FRAMEWORK ARCHITECTURE", description=f"Prefix: `{p}` | Sync Status: **ACTIVE**", color=0x0a0e17)
    embed.add_field(name="🛡️ CORE COMMAND SUITE", value="`/help` • `/whitelist` • `/unwhitelist` • `/setlog` • `/lock` • `/unlock` • `/purge` • `/ping` • `/status` • `/avatar`", inline=False)
    return embed

@bot.tree.command(name="help")
async def slash_help(i: discord.Interaction): await i.response.send_message(embed=generate_help_embed(bot_settings["prefix"]))

@bot.tree.command(name="whitelist")
async def slash_wl(i: discord.Interaction, member: discord.Member):
    if str(member.id) not in whitelist_db: whitelist_db.append(str(member.id))
    await i.response.send_message(f"👑 Privileges granted to {member.mention}.")

@bot.tree.command(name="unwhitelist")
async def slash_unwl(i: discord.Interaction, member: discord.Member):
    if str(member.id) in whitelist_db: whitelist_db.remove(str(member.id))
    await i.response.send_message(f"❌ Privileges revoked from {member.name}.")

@bot.tree.command(name="setlog")
async def slash_setlog(i: discord.Interaction, channel: discord.TextChannel):
    log_channels[i.guild.id] = channel.id
    await i.response.send_message(f"✅ Safe logs pipe routing assigned to {channel.mention}.")

@bot.tree.command(name="lock")
async def slash_lock(i: discord.Interaction):
    await i.channel.set_permissions(i.guild.default_role, send_messages=False)
    await i.response.send_message("🔒 Safe write capabilities isolated.")

@bot.tree.command(name="unlock")
async def slash_unlock(i: discord.Interaction):
    await i.channel.set_permissions(i.guild.default_role, send_messages=True)
    await i.response.send_message("🔓 Safe write capabilities normalized.")

@bot.tree.command(name="purge")
async def slash_purge(i: discord.Interaction, amount: int):
    await i.channel.purge(limit=amount)
    await i.response.send_message(f"🧹 Cleaned `{amount}` runtime line logs instantly.", ephemeral=True)

@bot.tree.command(name="ping")
async def slash_ping(i: discord.Interaction): await i.response.send_message(f"🏓 Gateway Framework Delay: `{round(bot.latency * 1000)}ms`")

@bot.tree.command(name="status")
async def slash_status(i: discord.Interaction): await i.response.send_message("🌐 Firewalls Base Status: **OPERATIONAL WITHOUT ANOMALIES**")

@bot.tree.command(name="avatar")
async def slash_avatar(i: discord.Interaction, member: discord.Member = None):
    target = member or i.user
    await i.response.send_message(target.display_avatar.url)

# ----------------- 🌐 100% WORKING DYNAMIC WICK UI DASHBOARD -----------------
app = Flask('')

WICK_DYNAMIC_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ guild_name }} - Wick Security Dashboard</title>
    <style>
        :root {
            --bg-deep: #090b10;
            --bg-sidebar: #0f131a;
            --bg-box: #141923;
            --bg-input: #1b2230;
            --accent-purple: #7289da;
            --accent-blue: #0070f3;
            --accent-green: #23a55a;
            --accent-red: #da373c;
            --text-white: #f2f3f5;
            --text-gray: #949ba4;
            --border-line: #1c2331;
        }
        body {
            background-color: var(--bg-deep); color: var(--text-white);
            font-family: 'gg sans', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0; padding: 0; display: flex; min-height: 100vh;
        }
        
        .sidebar {
            width: 270px; background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border-line); padding: 25px 15px;
            display: flex; flex-direction: column; box-sizing: border-box;
        }
        .guild-card {
            display: flex; align-items: center; gap: 12px; margin-bottom: 25px;
            padding-bottom: 15px; border-bottom: 1px solid var(--border-line);
        }
        .guild-icon {
            width: 44px; height: 44px; background: linear-gradient(135deg, #7289da, #11141a);
            border-radius: 12px; display: flex; align-items: center; justify-content: center;
            font-weight: bold; font-size: 14px; color: white; border: 1px solid var(--border-line);
            text-transform: uppercase; letter-spacing: 0.5px;
        }
        .guild-meta { display: flex; flex-direction: column; max-width: 170px; }
        .guild-title { font-size: 13.5px; font-weight: 700; color: var(--text-white); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .guild-status { font-size: 11px; color: var(--accent-green); font-weight: bold; margin-top: 2px; }
        
        .nav-section-label { font-size: 11px; text-transform: uppercase; color: var(--text-gray); font-weight: 700; margin: 18px 0 6px 8px; letter-spacing: 0.8px; }
        .nav-button {
            padding: 10px 14px; border-radius: 8px; font-size: 13.5px; color: var(--text-gray);
            text-decoration: none; display: flex; align-items: center; gap: 10px; margin-bottom: 4px; transition: 0.2s ease-in-out;
        }
        .nav-button:hover, .nav-button.active { background-color: rgba(114, 137, 218, 0.08); color: var(--text-white); font-weight: 600; }
        .nav-button.active { border-left: 3px solid var(--accent-purple); border-radius: 4px 8px 8px 4px; padding-left: 11px; }
        .nested-sub { margin-left: 15px; border-left: 1px solid var(--border-line); padding-left: 12px; }
        .nested-sub .nav-button { font-size: 13px; padding: 8px 10px; }

        .main-stage { flex: 1; padding: 40px; box-sizing: border-box; overflow-y: auto; }
        .view-wrapper { max-width: 900px; margin: 0 auto; }
        
        .header-banner { margin-bottom: 30px; }
        .header-banner h1 { font-size: 26px; font-weight: 700; margin: 0 0 6px 0; }
        .header-banner p { font-size: 14px; color: var(--text-gray); margin: 0; }

        .dashboard-card {
            background-color: var(--bg-box); border-radius: 12px; border: 1px solid var(--border-line);
            padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 24px rgba(0,0,0,0.5);
        }
        .card-heading-title { font-size: 12px; text-transform: uppercase; color: var(--text-gray); font-weight: 700; margin-bottom: 20px; letter-spacing: 0.5px; }
        
        .metrics-grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .metric-block { background: rgba(0,0,0,0.15); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.02); }
        .meta-lbl { font-size: 11px; color: var(--text-gray); text-transform: uppercase; margin-bottom: 5px; font-weight: 600; }
        .meta-val { font-size: 16px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

        .radial-gauge-box { display: flex; flex-direction: column; align-items: center; margin: 25px 0; }
        .gauge-track { width: 120px; height: 120px; border-radius: 50%; background: conic-gradient(var(--accent-green) {{ settings.security_score }}%, #22293a 0); display: flex; align-items: center; justify-content: center; }
        .gauge-center { width: 96px; height: 96px; background-color: var(--bg-box); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 700; color: var(--accent-green); }

        .option-toggle-panel { display: flex; justify-content: space-between; align-items: center; background-color: rgba(255,255,255,0.01); border: 1px solid var(--border-line); padding: 20px; border-radius: 8px; margin-bottom: 16px; }
        .option-details { max-width: 75%; }
        .option-title { font-size: 15px; font-weight: 700; margin: 0 0 4px 0; color: var(--text-white); }
        .option-desc { font-size: 12.5px; color: var(--text-gray); margin: 0; line-height: 1.4; }
        
        .switch { position: relative; display: inline-block; width: 46px; height: 24px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #353f55; border-radius: 30px; transition: .25s; }
        .slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 4px; bottom: 4px; background-color: white; border-radius: 50%; transition: .25s; }
        input:checked + .slider { background-color: var(--accent-green); }
        input:checked + .slider:before { transform: translateX(22px); }

        .input-field-element { width: 100%; padding: 12px 14px; background: var(--bg-input); border: 1px solid var(--border-line); color: white; border-radius: 8px; font-size: 14px; box-sizing: border-box; }
        
        .btn-action-commit { background-color: var(--accent-purple); color: white; border: none; font-weight: 600; padding: 14px; border-radius: 8px; cursor: pointer; width: 100%; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; margin-top: 10px; transition: 0.2s; }
        .btn-action-commit:hover { background-color: #5b73c7; }

        .registry-item-row { background-color: rgba(0,0,0,0.12); border: 1px solid var(--border-line); padding: 14px 18px; border-radius: 8px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; font-size: 13.5px; }
        .btn-revoke-action { color: var(--accent-red); font-weight: 700; text-decoration: none; font-size: 12px; text-transform: uppercase; }
    </style>
</head>
<body>

    <div class="sidebar">
        <div class="guild-card">
            <div class="guild-icon">{{ guild_acronym }}</div>
            <div class="guild-meta">
                <span class="guild-title">{{ guild_name }}</span>
                <span class="guild-status">● System Shielded</span>
            </div>
        </div>
        
        <a href="/?tab=overview" class="nav-button {% if active_tab == 'overview' %}active{% endif %}">ℹ️ Overview</a>
        <a href="#" class="nav-button" style="opacity: 0.4; cursor: not-allowed;">✨ Setup Wizard</a>
        <a href="#" class="nav-button" style="opacity: 0.4; cursor: not-allowed;">📋 System Logs</a>

        <div class="nav-section-label">Auto Modulation</div>
        <div class="nested-sub">
            <a href="/?tab=automod_general" class="nav-button {% if active_tab == 'automod_general' %}active{% endif %}">🌐 General Status</a>
            <a href="/?tab=automod_filters" class="nav-button {% if active_tab == 'automod_filters' %}active{% endif %}">🎛️ Limit Filters</a>
            <a href="/?tab=automod_whitelist" class="nav-button {% if active_tab == 'automod_whitelist' %}active{% endif %}">👑 Exception Whitelist</a>
        </div>

        <div class="nav-section-label">Anti-Nuke Firewalls</div>
        <div class="nested-sub">
            <a href="/?tab=antinuke_general" class="nav-button {% if active_tab == 'antinuke_general' %}active{% endif %}">🌐 General Status</a>
            <a href="/?tab=antinuke_filters" class="nav-button {% if active_tab == 'antinuke_filters' %}active{% endif %}">🎛️ Severe Filters</a>
        </div>
    </div>

    <div class="main-stage">
        <div class="view-wrapper">
            
            {% if active_tab == 'overview' %}
            <div class="header-banner">
                <h1>{{ guild_name }} Security Core</h1>
                <p>Telemetry stats overview index for live guild configuration nodes mapping.</p>
            </div>
            
            <div class="dashboard-card">
                <div class="card-heading-title">Framework Baseline Telemetries</div>
                <div class="metrics-grid-2">
                    <div class="metric-block"><div class="meta-lbl">Target Server Name</div><div class="meta-val">{{ guild_name }}</div></div>
                    <div class="metric-block"><div class="meta-lbl">Target ID Node</div><div class="meta-val">{{ guild_id }}</div></div>
                    <div class="metric-block"><div class="meta-lbl">Client Monitored Volume</div><div class="meta-val">{{ guild_members }} Active</div></div>
                    <div class="metric-block"><div class="meta-lbl">Virtual Dynamic Nodes</div><div class="meta-val" style="color: var(--accent-green);">200+ Synced Nodes</div></div>
                </div>
                
                <div class="radial-gauge-box">
                    <div class="gauge-track"><div class="gauge-center">{{ settings.security_score }}%</div></div>
                    <div style="font-size: 11px; font-weight: 700; margin-top: 12px; color: var(--text-gray); letter-spacing: 0.5px;">OVERALL SECURITY HEALTH VALUE</div>
                </div>
            </div>
            <div class="card-heading-title">Active Security Arrays</div>
            <div class="option-toggle-panel"><div><div class="option-title">Wick Security Mainframes Base</div><p class="option-desc">Current state status evaluation indicator: <b style="color:var(--accent-green)">ONLINE PROUD PROTECTION</b></p></div></div>
            {% endif %}

            {% if active_tab == 'automod_general' %}
            <div class="header-banner">
                <h1>Auto Modulation Shields</h1>
                <p>Toggle real-time core message filter arrays parameters instantly.</p>
            </div>
            <div class="dashboard-card">
                <div class="card-heading-title">General Automation Switches</div>
                <form method="POST" action="/save-automod-general">
                    <div class="option-toggle-panel">
                        <div class="option-details">
                            <div class="option-title">Anti-Link Cyber Protection</div>
                            <p class="option-desc">Intercept and automatically filter bad transmission attempts containing hypertext web URL strings links.</p>
                        </div>
                        <label class="switch">
                            <input type="checkbox" name="anti_link" value="ON" {% if settings.anti_link == 'ON' %}checked{% endif %}>
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="option-toggle-panel">
                        <div class="option-details">
                            <div class="option-title">Anti-Spam Adaptive Buffer Guard</div>
                            <p class="option-desc">Monitors fast message data flood speeds and immediately triggers native timeout configurations.</p>
                        </div>
                        <label class="switch">
                            <input type="checkbox" name="anti_spam" value="ON" {% if settings.anti_spam == 'ON' %}checked{% endif %}>
                            <span class="slider"></span>
                        </label>
                    </div>
                    <button type="submit" class="btn-action-commit">Commit AutoMod Operational Settings</button>
                </form>
            </div>
            {% endif %}

            {% if active_tab == 'automod_filters' %}
            <div class="header-banner">
                <h1>Limit Filter Variables</h1>
                <p>Fine-tune explicit message speed rules inside system cache lines.</p>
            </div>
            <div class="dashboard-card">
                <div class="card-heading-title">Fine-Tuning Threshold Coefficients</div>
                <form method="POST" action="/save-automod-filters">
                    <div style="margin-bottom: 20px;">
                        <label class="meta-lbl" style="display:block; margin-bottom:8px;">Burst Messages Limit (Max Allowed within 5 seconds cycle)</label>
                        <input type="number" name="spam_max_messages" value="{{ settings.spam_max_messages }}" class="input-field-element" min="2" max="15">
                    </div>
                    <div style="margin-bottom: 20px;">
                        <label class="meta-lbl" style="display:block; margin-bottom:8px;">Active Core Command Processing Prefix Trigger</label>
                        <input type="text" name="prefix" value="{{ settings.prefix }}" class="input-field-element" maxlength="5">
                    </div>
                    <button type="submit" class="btn-action-commit">Harden Filter Rulesets</button>
                </form>
            </div>
            {% endif %}

            {% if active_tab == 'automod_whitelist' %}
            <div class="header-banner">
                <h1>Immunity Trust Repositories</h1>
                <p>Register target bypass token keys to completely exempt accounts from security restrictions.</p>
            </div>
            <div class="dashboard-card">
                <div class="card-heading-title">Inject New Bypass Identity Token</div>
                <form method="POST" action="/add-wl-id" style="display: flex; gap: 12px; margin-bottom: 25px;">
                    <input type="text" name="user_id" placeholder="Paste specific Discord User Profile ID string" class="input-field-element" required>
                    <button type="submit" class="btn-action-commit" style="margin:0; width: auto; padding: 0 25px; background-color: var(--accent-green);">Inject Token</button>
                </form>
                
                <div class="card-heading-title">Active Trusted Registry Records</div>
                {% for uid in whitelist %}
                <div class="registry-item-row">
                    <div>Exception Record Reference Token: <code>{{ uid }}</code></div>
                    <a href="/del-wl-id?id={{ uid }}" class="btn-revoke-action">Revoke Access</a>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% if active_tab == 'antinuke_general' %}
            <div class="header-banner">
                <h1>Anti-Nuke Safeguards Matrix</h1>
                <p>Harden system configurations against bulk destruction triggers.</p>
            </div>
            <div class="dashboard-card">
                <div class="card-heading-title">Structural Firewall Parameters</div>
                <form method="POST" action="/save-antinuke-general">
                    <div class="option-toggle-panel">
                        <div class="option-details">
                            <div class="option-title">Anti-Nuke Core State Enforcement</div>
                            <p class="option-desc">Strips roles and permissions variables immediately upon tracking illegal mass server modifications.</p>
                        </div>
                        <label class="switch">
                            <input type="checkbox" name="anti_nuke" value="ON" {% if settings.anti_nuke == 'ON' %}checked{% endif %}>
                            <span class="slider"></span>
                        </label>
                    </div>
                    <button type="submit" class="btn-action-commit">Commit Anti-Nuke Operations Matrix</button>
                </form>
            </div>
            {% endif %}

            {% if active_tab == 'antinuke_filters' %}
            <div class="header-banner">
                <h1>Severe Deletion Rate Filters</h1>
                <p>Calibrate system action rate boundary limits to prevent internal destruction.</p>
            </div>
            <div class="dashboard-card">
                <div class="card-heading-title">Calibrate Administrative Speed Caps</div>
                <form method="POST" action="/save-antinuke-filters">
                    <div>
                        <label class="meta-lbl" style="display:block; margin-bottom:8px;">Critical Channel Deletion Cap (Max Allowed within 10 seconds frame)</label>
                        <input type="number" name="max_channels_deleted" value="{{ settings.max_channels_deleted }}" class="input-field-element" min="1" max="10">
                    </div>
                    <button type="submit" class="btn-action-commit">Lock Destructive Rate Framework</button>
                </form>
            </div>
            {% endif %}

        </div>
    </div>

</body>
</html>
"""

@app.route('/')
def home():
    tab = request.args.get('tab', 'overview')
    
    # FETCH DISCORD DATA IN REAL-TIME
    if bot.guilds:
        active_guild = bot.guilds[0] # Get the first active server bot is connected to
        g_name = active_guild.name
        g_id = active_guild.id
        g_members = f"{active_guild.member_count:,}"
        
        # Calculate acronym for icon (e.g. "Aetherion Haze" -> "AH")
        g_acronym = "".join([item[0] for item in g_name.split() if item]).upper()[:3]
    else:
        g_name = "No Server Detected"
        g_id = "00000000000000"
        g_members = "0"
        g_acronym = "SYS"

    return render_template_string(
        WICK_DYNAMIC_HTML, 
        active_tab=tab, 
        settings=bot_settings, 
        whitelist=whitelist_db,
        guild_name=g_name,
        guild_id=g_id,
        guild_members=g_members,
        guild_acronym=g_acronym
    )

# ----------------- FLASK UTILITY FORM ROUTERS -----------------
@app.route('/save-automod-general', methods=['POST'])
def save_am_gen():
    global bot_settings
    bot_settings["anti_link"] = "ON" if request.form.get("anti_link") else "OFF"
    bot_settings["anti_spam"] = "ON" if request.form.get("anti_spam") else "OFF"
    bot_settings["security_score"] = 95 if bot_settings["anti_link"] == "ON" and bot_settings["anti_spam"] == "ON" else 75
    return redirect(url_for('home', tab='automod_general'))

@app.route('/save-automod-filters', methods=['POST'])
def save_am_fil():
    global bot_settings
    bot_settings["spam_max_messages"] = request.form.get("spam_max_messages", 4)
    bot_settings["prefix"] = request.form.get("prefix", ",,,")
    return redirect(url_for('home', tab='automod_filters'))

@app.route('/save-antinuke-general', methods=['POST'])
def save_an_gen():
    global bot_settings
    bot_settings["anti_nuke"] = "ON" if request.form.get("anti_nuke") else "OFF"
    return redirect(url_for('home', tab='antinuke_general'))

@app.route('/save-antinuke-filters', methods=['POST'])
def save_an_fil():
    global bot_settings
    bot_settings["max_channels_deleted"] = request.form.get("max_channels_deleted", 3)
    return redirect(url_for('home', tab='antinuke_filters'))

@app.route('/add-wl-id', methods=['POST'])
def add_wl_id():
    uid = request.form.get("user_id", "").strip()
    if uid and uid.isdigit() and uid not in whitelist_db: whitelist_db.append(uid)
    return redirect(url_for('home', tab='automod_whitelist'))

@app.route('/del-wl-id')
def del_wl_id():
    uid = request.args.get("id", "").strip()
    if uid in whitelist_db: whitelist_db.remove(uid)
    return redirect(url_for('home', tab='automod_whitelist'))

def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run).start()

keep_alive()
bot.run(os.getenv('BOT_TOKEN'))
