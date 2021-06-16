import discord
from discord import embeds
from discord.ext import commands
import numpy as np
import asyncio
import sqlite3

class Mod(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.mute = []
        self.afk = []
        self.poll_ids = []

    @commands.has_permissions(manage_messages=True)
    @commands.command(aliases=['mute'])
    async def _mute(self,ctx,member: commands.MemberConverter,time:int=None):
        await ctx.message.add_reaction("👌")
        guild = ctx.guild
        id = ctx.author.id
        self.mute.append(id)
        role = discord.utils.get(guild.roles,name='Mute')
        print(role)
        if role == None :
            print('creating mute role')
            await guild.create_role(name='Mute',permissions=discord.Permissions(permissions=1024))
            muted_role = discord.utils.get(ctx.guild.roles, name="Mute")
            await ctx.channel.set_permissions(muted_role, read_messages=True,send_messages=False)
            await member.add_roles(muted_role)
        else:
            await ctx.channel.set_permissions(role, read_messages=True,send_messages=False)
            print(f'muting {member}')
            await member.add_roles(role)

        embed = discord.Embed(description=f'{member.name} has been muted for {time} minutes.',color=discord.Color.red())
        await ctx.send(embed=embed)

        if time!=None:
            await asyncio.sleep(time*60)
            await member.remove_roles(role)
            pos = self.mute.index(id)
            self.mute.pop(pos)
            embed = discord.Embed(description=f'{member.name} is free to speak now.',color=discord.Color.green())
            await ctx.send(embed=embed)

    @commands.has_permissions(manage_messages=True)
    @commands.command(aliases=['unmute'])
    async def _unmute(self,ctx,member: discord.Member,time=5):
        await ctx.message.add_reaction("👌")
        guild = ctx.guild
        id = ctx.author.id
        # list = guild.roles
        role = discord.utils.get(guild.roles,name='Mute')
        if id in self.mute :
            await member.remove_roles(role)
            embed = discord.Embed(description=f'{member.name} is free to speak now.',color=discord.Color.green())
            await ctx.send(embed=embed)
            pos = self.mute.index(id)
            self.mute.pop(id)
        else:
            embed = discord.Embed(description=f'{member.name} was never Muted.',color=discord.Color.green())
            await ctx.send(embed=embed)

    @commands.command(aliases=['ping'])
    async def ping_(self,ctx):
        embed = discord.Embed(description=f'pong ! {str(round(self.client.latency*1000))}ms',color=discord.Color.blurple())
        await ctx.reply(embed=embed)

    @commands.has_permissions(manage_messages=True)
    @commands.command(aliases=['purge','del','delete'])
    async def delete_(self,ctx,num=1):
        await ctx.channel.purge(limit = num+1)

    @commands.command(aliases=['afk'])
    async def afk_(self,ctx,reason='Not Given'):
        id = ctx.author
        if id in self.afk:
            pos = self.afk.index(id)
            self.afk.pop(pos)
            embed = discord.Embed(description="You are set to online now !",color=discord.Color.green())
            await ctx.reply(embed=embed)
        else:
            self.afk.append(id)
            embed = discord.Embed(description=f"{id.name},You are set to AFK now !",color=discord.Color.red())
            await ctx.send(embed=embed)
        print(self.afk)

    @commands.Cog.listener()
    async def on_message(self,message):
        for id in self.afk:
            if id.mentioned_in(message)==True:
                embed = discord.Embed(description=f"{id.name} is afk now !",color=discord.Color.red())
                await message.channel.send(embed=embed)
        try:
            if message.mentions[0] == self.client.user:
                embed = discord.Embed(description="My prefix is `.`",color=discord.Color.blurple())
                await message.channel.send(embed=embed)
        except:
            pass

    @commands.command(aliases=['join'])
    async def join_(self,ctx,member:discord.Member=None):
        try:
            channel = ctx.author.voice.channel.id
            if member!=None:
                msg = await ctx.send(f'{member.mention}')
            else:
                msg = await ctx.send(f'{ctx.message.guild.default_role}')
            await ctx.send(embed=discord.Embed(description=f"📢 Join <#{channel}>",color=discord.Color.orange()))
        except:
            await ctx.send(embed=discord.Embed(description="You are not connected to any VoiceChannel",color=discord.Color.red()))
        # embed = discord.Embed(description="use `join vc <@person>` or `join tc <@person>`")

    @commands.command(aliases=['invite'])
    async def create_invite(self, ctx,age=5):
        link = await ctx.channel.create_invite(max_age=age*60)
        await ctx.send(f"**Timeout: {age} Minutes** {link}")

    @commands.command(aliases=['bug','report'])
    async def bug_report(self,ctx,*,arg):
        bug_channel = self.client.get_channel('BUG_REPORT_CHANNEL <Int>')
        try:
            url = ctx.message.attachments[0].url
        except IndexError:
            url = None
        await bug_channel.send(embed=discord.Embed(title="Bug Report",description=f"{arg} : {ctx.author.mention} in {ctx.guild.name}",color=discord.Color.red()))
        if url != None:
            await bug_channel.send(url)
        msg = await ctx.send(embed=discord.Embed(description="Bug Report sent !!",color=discord.Color.orange()))
        await asyncio.sleep(10)
        await msg.delete()
    # @commands.command()
    # async def poll(self,ctx,*,msg):
    #     conn = sqlite3.connect('fav_disc.db')
    #     c = conn.cursor()
    #     try:
    #         c.execute("""CREATE TABLE poll(
    #                 id integer,
    #                 poll text
    #                 )""")
    #     except:
    #         print("db already there")
    #     msg = msg.split(':')
    #     title = msg[0]
    #     desc = msg[1]
    #     values = msg[2]
    #     values = values.split(',')
    #     embed = discord.Embed(title=title,description=desc,color=discord.Color.orange())
    #     for i in range(len(values)):
    #         embed.add_field(name='')
    # >>>> MAYBE I'LL IMPLEMENT IT LATER

def setup(client):
    client.add_cog(Mod(client))
