import discord,datetime,random,youtube_dl,os,asyncio
from discord.ext import commands
from discord.voice_client import VoiceClient
import numpy as np
import sqlite3

def get_prefix(bot,msg):
    db = sqlite3.connect("Config.db")
    cursor = db.cursor()
    x = cursor.execute(f"SELECT prefix FROM config WHERE guild_id = {msg.guild.id}")
    y = x.fetchone()
    if y == None:
        return commands.when_mentioned_or(".")(bot,msg)
    else:
        return commands.when_mentioned_or(y[0],".")(bot,msg)
    
client = commands.Bot(command_prefix=get_prefix)
client.remove_command("help")

@client.event
async def on_ready():
    print('Airi is ready !')
    bot_server = client.get_channel('PERSONAL_CHANNEL_ID <Int>')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=".help"))
    await bot_server.send(embed=discord.Embed(description=f"Airi is online\n> {datetime.datetime.now()}"))
@client.event
async def on_guild_join(guild):
    bot_server = client.get_channel('PERSONAL_CHANNEL_ID <Int>')
    embed = discord.Embed(color=discord.Color.blurple())
    embed.set_thumbnail(url=guild.icon_url)
    embed.add_field(name='Guild Name',value=guild.name,inline=True)
    embed.add_field(name='Guild Id', value=guild.id, inline=True)
    embed.add_field(name='Owner', value=f"<@{guild.owner_id}>", inline=True)
    embed.add_field(name='Member Count', value=guild.member_count, inline=True)
    embed.add_field(name='Region', value=guild.region, inline=True)
    embed.add_field(name='Created At', value=guild.created_at, inline=True)

    await bot_server.send(embed=embed)

# ERROR HANDELING
#comment this part, if you want to see all the errors in your terminal
@client.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.errors.CommandNotFound):
        embed = discord.Embed(description="Command not found !",color=discord.Color.red())
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("❓")

    if isinstance(error,commands.MissingPermissions):
        embed = discord.Embed(description="You don't have permissions to do that!",color=discord.Color.red())
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("⚠")

# DONE ERROR HANDELINGS

@client.group(invoke_without_command=True)
async def help(ctx):
    bot_roles = ctx.guild.get_member(client.user.id).roles
    embed = discord.Embed(title= "Getting Help",color=bot_roles[len(bot_roles)-1].color)
    embed.set_thumbnail(
        url="https://cdn.pixilart.com/photos/large/ffc272ece387503.gif")

    embed.add_field(
        name='Airi is a Multi-Purpose Bot',
        value='My Prefix is = `.`\n Use following commands for extended information on a command',inline=False)

    embed.add_field(name='🎵| Music Commands',value=".help music",inline=True)
    embed.add_field(name="😸| Fun Commands",value=".help fun",inline=True)
    embed.add_field(name="⚙| Manage Server",value=".help server",inline=False)
    embed.add_field(name="📐| Math Commands",value="Soon you'll be allowed",inline=True)
    embed.add_field(name="🧬| Covid-19",value=".help covid",inline=True)
    embed.add_field(name="\u200b", value=f"[Add me to your server !](https://discord.com/api/oauth2/authorize?client_id=BOT_ID&permissions=0&scope=bot)",inline=False)
    await ctx.send(embed=embed)

@help.command()
async def music(ctx):
    embed = discord.Embed(title= "🎵 | Music Help",description="Airi can play/stream music on your discord server.\nIt supports **Youtube** and **Spotify**",color=discord.Color.blurple())
    embed.set_thumbnail(
        url="https://cutewallpaper.org/21/tsumiki-miniwa-wallpaper/Tsumiki-miniwa-gif-13-GIF-Images-Download.gif"
    )
    embed.add_field(
        name ="Play music",value="`.p Song Name / Song Link / Playlist Link` ",inline=False)
    embed.add_field(name="Play/Pause",value="`.pause`to pause & `.play` to play a paused song\n You can use `.s` alternatively to toggle play/pause",inline=False)
    embed.add_field(name="Next/Previous",value="`.next` or `.n` to jump to next song in the queue\n `.previous`or `.ps` to go back to previously playing song",inline=False)
    embed.add_field(name="Jump",value='`.jump <number>` or `.j <number>` to jump in a perticular song in the queue.',inline=False)
    embed.add_field(name="Now Playing",value="`.np` displays currently playing song",inline=False)
    embed.add_field(name="Queue",value="`.q` or `.queue` displays songs in a queue",inline=False)
    embed.add_field(name="Leave",value="`.leave` leaves the voice channel and clears the queue !",inline=False)
    embed.add_field(name="Liked Songs",value="Create your Own playlist of favourite songs !\nFor more info use `.help liked`",inline=False)
    await ctx.send(embed=embed)

@help.command()
async def covid(ctx):
    bot_roles = ctx.guild.get_member(client.user.id).roles
    embed = discord.Embed(title= "🧬 | Covid-19 Help",description="Use `.<command name>` to activate !",color=bot_roles[len(bot_roles)-1].color)
    embed.set_thumbnail(
        url="https://media0.giphy.com/media/hubAFdn7wrjM3SVkq5/source.gif")

    embed.add_field(name='😷 | About Covid',value="`.cinfo` Gives the Covid-19 information.",inline=False)
    embed.add_field(name="📈 | Covid Cases",value="`.cc <country>` Use this command to get Covid-19 stats in a country (default:India)\nFor eg: cc usa to get Covid stats of United States",inline=False)
    embed.add_field(name="🩹 | General Medicines",value="`.cmed` Gives general purpose Medicines name and their Dosage",inline=False)
    embed.add_field(name="💉 | Vaccine Information",value="`.cvac` Gives information and important url related to Vaccination in India",inline=False)


    await ctx.send(embed=embed)

@help.command()
async def server(ctx):
    bot_roles = ctx.guild.get_member(client.user.id).roles
    embed = discord.Embed(title="⚙ | Server Help",description="Use `.<command name` to activate !\n You need to give **certain permissions** to run a command !\n List of permissions can be found inside description of each command !",color=bot_roles[len(bot_roles)-1].color)
    embed.set_thumbnail(
        url = "https://media4.giphy.com/media/Fo5y4K3GD3RYijvsCS/giphy.gif")
    embed.add_field(name="Server Info",value = "`.si` gives information about Server",inline=False)
    embed.add_field(name="Mute/Unmute",value="> `.mute <username> <duration>` default duration : forever `.unmute <@username>`",inline=True)
    embed.add_field(name="Ban/Unban", value="> `.ban <username>` &  `.unban <@username>`", inline=True)

    embed.add_field(name='Kick',value="> `.kick <@username>` Required Permissions : Kick Members",inline=False)
    embed.add_field(name='Invite',value= "> `.invite` Gives the Invite link of Server.",inline=True)

    embed.add_field(name='Delete Messsages',value="> `.del <number>` or `.clear <number>`",inline=True)
    embed.add_field(name="Ping",value="> `.ping` gives ping of the server",inline=False)

    await ctx.send(embed=embed)

@help.command()
async def fun(ctx):
    bot_roles = ctx.guild.get_member(client.user.id).roles
    embed = discord.Embed(title="🎮 | Fun Commands",description="Use `.<command name>` to activate !\n",color=bot_roles[len(bot_roles)-1].color)
    embed.set_thumbnail(url='https://i.gifer.com/Vx3x.gif')
    embed.add_field(name='Anime/Manga',value="> `.anime <name>` or `.manga <name>`",inline=False)
    embed.add_field(name='Wallpapers',value="> `.wall` get any random wallpaper\n> `.wall <name>` get wallpapers in the mentioned category")
    embed.add_field(name='Profile picture',value=' `.pic <@member>`')

    await ctx.send(embed=embed)

@help.command()
async def liked(ctx):
    bot_roles = ctx.guild.get_member(client.user.id).roles
    embed = discord.Embed(title="♥ | Liked Commands",description="Airi allows you to save your favourite songs in cloud.\nYou can play your favourite songs anytime from any server.", color=bot_roles[len(bot_roles)-1].color)
    embed.set_thumbnail(url="https://media1.giphy.com/media/UXFWIX08KNkBVdg5Iy/giphy.gif?cid=6c09b952p6uen16tvz1yyvky2xlndq2uvy0r15y9fk69ntcl&rid=giphy.gif&ct=s")
    embed.add_field(name='Like a song',value="> `.like` Adds the song to your Liked songs playlist.",inline=True)
    embed.add_field(name='Dislike',value='> `.dl <number>` or `.dislike <no.>`',inline=True)
    embed.add_field(name="Show Liked",value="> `.get` Shows all of your liked songs",inline=False)
    embed.add_field(name="Play Selected",value="> `.pliked <no.>` Plays the specific song from Liked Songs",inline=False)
    embed.add_field(name='Play All',value="> `.pliked` Plays all Liked songs that You've added.",inline=False)
    await ctx.send(embed=embed)
# COGS

@client.command()
async def load(ctx,extension):
    client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx,extension):
    client.unload_extension(f'cogs.{extension}')

@client.command()
async def reload(ctx,extension):
    client.reload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

# run command
client.run('DISCORD_TOKEN')
