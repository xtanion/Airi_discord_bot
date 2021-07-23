from sqlite3.dbapi2 import connect
import discord
from discord.ext import commands
import sqlite3

from discord.ext.commands.core import command

class Config(commands.command):
    def __init__(self,bot):
        self.bot = bot
        self.db = sqlite3.connect("config.db")
        self.cursor = self.db.cursor()
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS config(
            guild_id INT,
            prefix TEXT
        )
        """)
    @commands.command(name="prefix")
    async def _prefix(self,ctx,prefix:str=None):
        if prefix == None:
            x = self.cursor.execute(f"SELECT prefix FROM config WHERE guild_id = {ctx.guild.id}")
            y = x.fetchone()
            if y is None:
                em = discord.Embed(title="My Prefixes Here",description=f"`1.` **.**",color=discord.Color.blurple())
            else:
                em = discord.Embed(title="My Prefixes Here",description=f"`1.` **.**\n`2.` **{y[0]}**",color=discord.Color.blurple())
            await ctx.send(embed=em)
        else:
            x = self.cursor.execute(f"SELECT prefix FROM config WHERE guild_id = {ctx.guild.id}")
            y = x.fetchone()
            if y is None:
                self.cursor.execute("INSERT INTO config VALUES (?,?)", (ctx.guild.id,prefix))
                em = discord.Embed(title="Prefix Updated",description=f"Your Server Prefix Updated to : `{prefix}`",color=discord.Color.green())
                await ctx.send(embed=em)
                self.db.commit()
            else:
                self.cursor.execute(f"UPDATE config SET prefix = ? WHERE guild_id = ?",(prefix,ctx.guild.id))
                em = discord.Embed(title="Prefix Updated",description=f"Your Server Prefix Updated to : `{prefix}`",color=discord.Color.green())
                await ctx.send(embed=em)
                self.db.commit()
def setup(bot):
    bot.add_cog(Config(bot))