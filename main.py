import discord
from discord.ext import commands
import os # default module
from dotenv import load_dotenv
import database
import json


load_dotenv()
bot = discord.Bot()

PROFANITY_LIST = []


db = database.Database()
# load config


def load_comma_separated_file(file_name):
    # load a file that contains a list of comma separated values
    with open(file_name, "r") as file:
        return file.read().split(", ")

def profanity_filter(server_id, message):
    # check if the message contains a banned word
    for word in message.split(" "):
        if word in PROFANITY_LIST:
            return True

    return False

def check_role_permissions(server_id, role : discord.Role):
    # check if the user has the required role to use the bot
    role_permissions = db.get_server_settings(server_id)["RolesThatCanSendPortalMessages"]
    if role_permissions == []:
        return True

    if role.name in role_permissions:
        return True

    return False

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

'''
set the channel for the bot to send messages
It can be used only by admins
'''
@bot.slash_command(name="setchannel", description="Set the channel for the bot to send messages to")
async def setchannel(ctx, channel: discord.TextChannel):
    # if error on @commands.has_role("admin") then it will return this
    if not ctx.author.guild_permissions.administrator:
        return await ctx.respond("You do not have permission to use this command!",ephemeral=True)
        
    await ctx.respond(f"Set the channel to {channel.mention}", ephemeral=True)
    # set the channel in the database
    db.set_channel(ctx.guild.id, ctx.guild.name, channel.id, channel.name)


'''
Help - show all commands
'''
@bot.slash_command(name="help", description="Show all commands")
async def help(ctx):
    await ctx.respond('''
- `/help` - show all commands
- `/hello` - say hello to yourself
- `/portal` - send a message to the portal channel
- `/settings` - set the settings for the bot (only admins)
- `/setchannel` - set the channel for the bot to send messages to (only admins)
    ''')

'''
Hello - this pings the user saying hi in the channel that was set
'''
@bot.slash_command(name = "hello", description = "Say hello to the bot")
async def hello(ctx):
    # send message to the channel
    channel_id = db.get_channel(ctx.guild.id)
    if channel_id:
        await ctx.respond(f"done", ephemeral=True)
        channel = bot.get_channel(channel_id[2])
        return await channel.send(f"Hello {ctx.author.mention}!")
    await ctx.respond(f"Please set a channel first!", ephemeral=True)


'''
Portal - this command allows you to send a message across all the servers that the bot is in
'''
@bot.slash_command(name = "portal", description = "Send a message across all the servers")
async def portal(ctx, message : str):
    # check for profanity
    channel_id = db.get_channel(ctx.guild.id)
    if channel_id is None:
        return await ctx.respond("Please set a channel first!", ephemeral=True)
    if profanity_filter(ctx.guild.id ,message):
        profanity = True
    if db.get_server_settings(ctx.guild.id)["AllowFilteringProfanity"] == True and profanity:
        return await ctx.respond("Profanity is not allowed!", ephemeral=True)

    # get all the channels from the database
    if not check_role_permissions(ctx.guild.id, ctx.author.roles[0]):
        return await ctx.respond("You do not have permission to use this command!", ephemeral=True)
    channels_query = db.get_channels()
    counter = 0
    for channel_query in channels_query:
        channel = bot.get_channel(channel_query[2])
        if channel_query[0] != ctx.guild.id:
            await channel.send(f"Message from **{ctx.author.name}** from server :arrow_forward: *{ctx.guild.name}* :arrow_backward: : ```{message}```")
            counter += 1
    
    await ctx.respond(f"done. I sent message \"{message}\" to {counter} servers.")


'''
Portal Invite - this command allows you to send an invite across all the servers that the bot is in
'''
@bot.slash_command(name = "portalinvite", description = "Send an invite across all servers that the bot is in")
async def portalinvite(ctx, max_age : int, max_uses : int):
    # generate invite link
    channel_id = db.get_channel(ctx.guild.id)
    if channel_id is None:
        return await ctx.respond("Please set a channel first!", ephemeral=True)

    channel = bot.get_channel(channel_id[2])
    print(channel)
    invite = await channel.create_invite(max_age=max_age, max_uses=max_uses)
    channels_query = db.get_channels()
    counter = 0
    for channel_query in channels_query:
        channel = bot.get_channel(channel_query[2])
        if channel_query[0] != ctx.guild.id and db.get_server_settings(channel_query[0])["AllowPortalInvites"] == True:
            await channel.send(f"Invite from **{ctx.author.name}** from  *{ctx.guild.name}* \n {invite}")
            counter += 1
    
    await ctx.respond(f"done. I sent invite to {counter} servers.")


'''
Settings - this command allows you to change the settings of the bot
'''
@bot.slash_command(name = "settings", description = "Change the settings of the bot")
async def settings(ctx, setting : str, value : str):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.respond("You do not have permission to use this command!",ephemeral=True)
    # get the settings from the database
    settings = db.get_server_settings(ctx.guild.id)
    # check if the setting exists
    if setting not in settings:
        return await ctx.respond(f"Setting {setting} does not exist!", ephemeral=True)
    # check if the value is valid
    if setting == "AllowFilteringProfanity":
        if value not in ["True", "False"]:
            return await ctx.respond(f"Value {value} is not valid!", ephemeral=True)
        if value == "True":
            settings["AllowFilteringProfanity"] = True 
        else:
            settings["AllowFilteringProfanity"] = False

    elif setting == "RolesThatCanSendPortalMessages":
        if value == "":
            settings["RolesThatCanSendPortalMessages"] = []
        else:
            settings["RolesThatCanSendPortalMessages"] = value.split(", ")

    # set the value in the database
    db.set_server_settings(ctx.guild.id, settings)
    await ctx.respond(f"done", ephemeral=True)
"""
Show settings - this command allows you to show the settings of the bot
"""
@bot.slash_command(name = "showsettings", description = "Show the settings of the bot")
async def showsettings(ctx):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.respond("You do not have permission to use this command!",ephemeral=True)
    # get the settings from the database
    settings = db.get_server_settings(ctx.guild.id)
    await ctx.respond(f"```\n{settings}```", ephemeral=True)

if __name__ == "__main__":
    PROFANITY_LIST = load_comma_separated_file("data/profanity.txt")

    try:
        bot.run(os.getenv('TOKEN')) # run the bot with the token from the env file
    except Exception as e:
        print(e)
    # load database