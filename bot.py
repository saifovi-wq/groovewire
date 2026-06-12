import discord
from discord.ext import commands
import datetime
import os
import re

# Intents configuration
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.moderation = True

# Custom prefix storage configuration
server_prefixes = {}

def get_prefix(bot, message):
    if not message.guild:
        return '??'
    return server_prefixes.get(message.guild.id, '??')

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

# Regular expression pattern to detect links
URL_PATTERN = r"(https?:\/\/[^\s]+)"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} | Premium Active')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Server Security"))

# 🚫 AUTOMATED BACKGROUND ANTI-LINK SYSTEM
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if re.search(URL_PATTERN, message.content):
        if not message.author.guild_permissions.manage_messages:
            await message.delete()
            embed = discord.Embed(
                title="⚠️ Security Alert", 
                description=f"{message.author.mention}, aponi ekhane kono link share korte parben na!", 
                color=discord.Color.red()
            )
            return await message.channel.send(embed=embed, delete_after=5)

    await bot.process_commands(message)

# ⚙️ PREFIX MANAGEMENT
@bot.command()
@commands.has_permissions(administrator=True)
async def setprefix(ctx, new_prefix: str):
    if len(new_prefix) > 5:
        return await ctx.send("❌ Prefix khub boro! Maximum 5 ti character allow.")
    server_prefixes[ctx.guild.id] = new_prefix
    
    embed = discord.Embed(title="⚙️ Prefix Updated", description="Notun prefix successfully set kora hoyeche.", color=discord.Color.green())
    embed.add_field(name="Current Prefix", value=f"`{new_prefix}`")
    await ctx.send(embed=embed)

# ⏳ TIMEOUT (MUTE) COMMAND
@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int, *, reason=None):
    if member.top_role >= ctx.author.top_role:
        return await ctx.send("❌ Higher/Equal rank text operations block kora.")
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await ctx.send(f"⏳ Successfully muted {member.mention} for {minutes} minutes.")

# 🔨 BAN COMMAND
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if member.top_role >= ctx.author.top_role:
        return await ctx.send("❌ Error handling hierarchy validation failed.")
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Banned {member.mention}")

# ✏️ SET NICKNAME
@bot.command()
@commands.has_permissions(manage_nicknames=True)
async def setnick(ctx, member: discord.Member, *, nickname: str = None):
    await member.edit(nick=nickname)
    await ctx.send(f"✏️ Nickname process successfully completed.")

# ✨ PREMIUM HELP DASHBOARD
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="✨ WICK-SECURE PRO",
        description=f"Current prefix: `{ctx.prefix}`",
        color=discord.Color.from_rgb(47, 49, 54)
    )
    embed.add_field(name="🛡️ MODERATION", value="`ban`, `kick`, `timeout`, `setnick`", inline=False)
    embed.add_field(name="⚙️ CONFIG", value="`setprefix`", inline=False)
    await ctx.send(embed=embed)

# Grab secret environmental runtime variables safely
bot.run(os.getenv('BOT_TOKEN'))
