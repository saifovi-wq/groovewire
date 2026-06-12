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
    "prefix": "{^}",
    "anti_nuke": "ON",
    "anti_spam": "ON",
    "anti_link": "ON"
}

# Realtime custom command trigger dictionary matrix storage
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

@bot.event
async def on_ready():
    print(f'🔥 WICK ULTIMATE CUSTOM ENGINE OPERATIONAL AS {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Dashboard Live Custom Cmds"))
    try:
        await bot.tree.sync()
    except Exception as e:
        print(f"Slash Sync Error: {e}")

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
                    try: await user.remove_roles(role, reason="Anti-Nuke System Core Action")
                    except: pass

# ----------------- 🛡️ UNIFIED SECURITY ENGINE & CUSTOM CMDS LAYER -----------------
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    guild_id = message.guild.id
    user_id = message.author.id
    current_time = time.time()
    
    is_whitelisted = user_id in whitelist_users[guild_id]
    is_staff = message.author.guild_permissions.manage_messages or is_whitelisted

    if not is_staff:
        # Anti-Link Filter Switch Check
        if bot_settings["anti_link"] == "ON" and re.search(URL_PATTERN, message.content):
            return await message.delete()

        # Anti-Spam Filter Switch Check
        if bot_settings["anti_spam"] == "ON":
            user_msg_history[user_id] = [t for t in user_msg_history[user_id] if current_time - t < SPAM_WINDOW]
            user_msg_history[user_id].append(current_time)
            if len(user_msg_history[user_id]) > MAX_MESSAGES:
                try:
                    await message.delete()
                    await message.author.timeout(datetime.timedelta(minutes=10))
                    return
                except: pass

    # --- WEBSITE GENERATED CUSTOM COMMAND TRACER ENGINE ---
    prefix = bot_settings["prefix"]
    if message.content.startswith(prefix):
        raw_cmd = message.content[len(prefix):].strip().lower()
        if raw_cmd in custom_commands:
            return await message.channel.send(custom_commands[raw_cmd])

    await bot.process_commands(message)

# ----------------- 📜 EMBED DASHBOARD CONTROL -----------------
@bot.command()
async def help(ctx):
    prefix = bot_settings["prefix"]
    embed = discord.Embed(title="🛡️ WICK ULTIMATE LIVE CORE", color=discord.Color.from_rgb(88, 101, 242))
    embed.add_field(name="Current Guard Settings", value=f"Prefix: `{prefix}`\nAnti-Nuke: `{bot_settings['anti_nuke']}`\nAnti-Spam: `{bot_settings['anti_spam']}`\nAnti-Link: `{bot_settings['anti_link']}`", inline=False)
    
    # Active custom commands trace string parser
    cmd_list = ", ".join([f"`{c}`" for c in custom_commands.keys()]) if custom_commands else "None Created"
    embed.add_field(name="✨ Dashboard Custom Commands", value=cmd_list, inline=False)
    await ctx.send(embed=embed)

# ----------------- 🌐 FLASK LIVE INTERACTIVE CONTROLLER PANEL -----------------
app = Flask('')

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Wick Premium Web Panel</title>
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
        <h1>🛡️ Wick Secure Customization Portal</h1>
        
        <form method="POST" action="/save-settings">
            <h2>⚙️ Core Engine Configuration</h2>
            <div class="form-group">
                <label>Command Prefix</label>
                <input type="text" name="prefix" value="{{ settings.prefix }}" maxlength="5">
            </div>
            <div class="form-group">
                <label>Anti-Nuke Matrix Shield</label>
                <select name="anti_nuke">
                    <option value="ON" {% if settings.anti_nuke == 'ON' %}selected{% endif %}>Enabled (ON)</option>
                    <option value="OFF" {% if settings.anti_nuke == 'OFF' %}selected{% endif %}>Disabled (OFF)</option>
                </select>
            </div>
            <div class="form-group">
                <label>Anti-Spam Filter Shield</label>
                <select name="anti_spam">
                    <option value="ON" {% if settings.anti_spam == 'ON' %}selected{% endif %}>Enabled (ON)</option>
                    <option value="OFF" {% if settings.anti_spam == 'OFF' %}selected{% endif %}>Disabled (OFF)</option>
                </select>
            </div>
            <div class="form-group">
                <label>Anti-Link Gateway Guard</label>
                <select name="anti_link">
                    <option value="ON" {% if settings.anti_link == 'ON' %}selected{% endif %}>Enabled (ON)</option>
                    <option value="OFF" {% if settings.anti_link == 'OFF' %}selected{% endif %}>Disabled (OFF)</option>
                </select>
            </div>
            <button type="submit" class="btn btn-green">UPDATE SYSTEM FILTERS</button>
        </form>

        <h2>✨ Custom Commands Manager</h2>
        <form method="POST" action="/add-command">
            <div class="form-group" style="border-left-color: #faa61a;">
                <label>Command Trigger (Do not include prefix symbol)</label>
                <input type="text" name="cmd_name" placeholder="e.g. facebook" required>
            </div>
            <div class="form-group" style="border-left-color: #faa61a;">
                <label>Automated Bot Text Response Output</label>
                <textarea name="cmd_reply" rows="3" placeholder="Type what the bot should reply..." required></textarea>
            </div>
            <button type="submit" class="btn">CREATE REALTIME COMMAND</button>
        </form>

        <h2>📋 Currently Active Custom Commands</h2>
        {% for name, reply in commands.items() %}
        <div class="cmd-item">
            <div><strong>{{ settings.prefix }}{{ name }}</strong> &rarr; <span style="color: #b9bbbe;">{{ reply }}</span></div>
            <a href="/delete-command/{{ name }}" class="delete-link">Remove</a>
        </div>
        {% else %}
        <p style="color: #72767d; text-align: center;">No custom commands created yet.</p>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(DASHBOARD_HTML, settings=bot_settings, commands=custom_commands)

@app.route('/save-settings', methods=['POST'])
def save_settings():
    global bot_settings
    bot_settings["prefix"] = request.form.get("prefix", "{^}")
    bot_settings["anti_nuke"] = request.form.get("anti_nuke", "ON")
    bot_settings["anti_spam"] = request.form.get("anti_spam", "ON")
    bot_settings["anti_link"] = request.form.get("anti_link", "ON")
    return redirect(url_for('home'))

@app.route('/add-command', methods=['POST'])
def add_command():
    global custom_commands
    name = request.form.get("cmd_name", "").strip().lower()
    reply = request.form.get("cmd_reply", "").strip()
    if name:
        custom_commands[name] = reply
    return redirect(url_for('home'))

@app.route('/delete-command/<name>')
def delete_command(name):
    global custom_commands
    if name in custom_commands:
        del custom_commands[name]
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
