import discord,sqlite3,asyncio,json,random,requests,praw
from discord import embeds
from discord.errors import DiscordServerError
from discord.ext import commands

queue1 = []

class Task(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.r_store = []

    @commands.command(aliases=['hi','hii','hello'])
    async def _hey(self,ctx):
        resp = str("Hello !")
        msg = await ctx.reply(resp)
        await ctx.message.add_reaction("🧡")

    @commands.command(aliases=['anime'])
    async def anime_(self,ctx,*,arg):
        search = arg
        search = search.split(" ")
        text = " "
        for i in range(len(search)):
            text = f'{text}{search[i]}/'
        text = (text[1:-1])
        x = requests.get(f'https://api.jikan.moe/v3/search/anime?q={text}&page=1')
        # print(x.text)
        anime_dict = json.loads(x.text)
        anime_dict=anime_dict['results'][0]
        if anime_dict['end_date'] == None:
            anime_dict['end_date'] = 'Currently Airing123456789012345'

        embed = discord.Embed(title=f"{anime_dict['title']}",color=discord.Color.orange())
        embed.set_thumbnail(url=f"{anime_dict['image_url']}")
        embed.add_field(name="🌟 | Rating",value=f"{anime_dict['score']}/10",inline=True)
        embed.add_field(name="🍿 | Episodes",value=f"  {anime_dict['episodes']}",inline=True)
        embed.add_field(name="🎬 | Rated",value=f"{anime_dict['rated']}",inline=False)
        embed.add_field(name="Release Date",value=f"{anime_dict['start_date'][:-15]}",inline=True)
        embed.add_field(name="Finished Airing",value=f"{anime_dict['end_date'][:-15]}",inline=True)

        embed.add_field(name="Storyline",value=f"{anime_dict['synopsis']}\n **[click to see more]({anime_dict['url']})**",inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=['manga'])
    async def manga_(self, ctx, *, arg):
        search = arg
        search = search.split(" ")
        text = " "
        for i in range(len(search)):
            text = f'{text}{search[i]}/'
        text = (text[1:-1])
        x = requests.get(f'https://api.jikan.moe/v3/search/manga?q={text}&page=1')
        # print(x.text)
        anime_dict = json.loads(x.text)
        anime_dict = anime_dict['results'][0]
        if anime_dict['end_date'] == None:
            anime_dict['end_date'] = 'Currently Airing123456789012345'

        embed = discord.Embed(title=f"{anime_dict['title']}", color=discord.Color.orange())
        embed.set_thumbnail(url=f"{anime_dict['image_url']}")
        embed.add_field(name="🌟 | Rating", value=f"{anime_dict['score']}/10", inline=True)
        embed.add_field(name="🍿 | Chapters", value=f"  {anime_dict['chapters']}", inline=True)
        embed.add_field(name="📘 | Volumes", value=f"{anime_dict['volumes']}", inline=False)
        embed.add_field(name="Release Date", value=f"{anime_dict['start_date'][:-15]}", inline=True)
        embed.add_field(name="Finished Airing", value=f"{anime_dict['end_date'][:-15]}", inline=True)

        embed.add_field(name="Storyline",
                        value=f"{anime_dict['synopsis']}\n **[click to see more]({anime_dict['url']})**", inline=False)

        await ctx.send(embed=embed)
    @commands.command(aliases=['pic'])
    async def get_img(self,ctx,person:discord.Member):
        pic_url_jpg = person.avatar_url_as(format='jpg',size=1024)
        pic_url_jpeg = person.avatar_url_as(format='jpeg',size=1024)
        pic_url_png = person.avatar_url_as(format='png',size=1024)

        if person.is_avatar_animated() == True:
            pic_url_gif = person.avatar_url_as(format='gif',size=1024)
            embed = discord.Embed(title="Profile Picture",description=f"**{person.mention} Download : [JPG]({pic_url_jpg}) | [ JPEG ]({pic_url_jpeg}) | [ PNG ]({pic_url_png}) | [ GIF ]({pic_url_gif})**",color=discord.Color.from_rgb(121, 192, 212))
            embed.set_image(url=pic_url_jpg)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Profle Picture",description=f"**{person.mention} Download : [ JPG ]({pic_url_jpg}) | [ JPEG ]({pic_url_jpeg}) | [ PNG ]({pic_url_png})**",color=discord.Color.from_rgb(121, 192, 212))
            embed.set_image(url=pic_url_jpg)
            await ctx.send(embed=embed)

    # @commands.group(invoke_without_command=True)
    @commands.command(aliases=['react','em'])
    async def _replied(self,ctx,*,text:str):
        emoji_list = {' ':'〰','a': '🇦', 'b': '🇧', 'c': '🇨', 'd': '🇩', 'e': '🇪', 'f': '🇫', 'g': '🇬', 'h': '🇭','i': '🇮', 'j': '🇯', 'k': '🇰', 'l': '🇱', 'm': '🇲', 'n': '🇳', 'o': '🇴', 'p': '🇵','q': '🇶', 'r': '🇷', 's': '🇸', 't': '🇹', 'u': '🇺', 'v': '🇻', 'w': '🇼', 'x': '🇽','y': '🇾', 'z': '🇿','0':'0️⃣','1':'1️⃣','2':'2️⃣','3':'3️⃣','4':'4️⃣','5':'5️⃣','6':'6️⃣','7':'7️⃣','8':'8️⃣','9':'9️⃣'}
        msg_id = 0
        if ctx.message.reference != None:
            msg_id =  ctx.message.reference.message_id
        else:
            await ctx.send(embed=discord.Embed(description="Please reply to a message in order to react !",color=discord.Color.red()))
        msg = await ctx.fetch_message(msg_id)
        text = str(text)
        try:
            await ctx.message.delete()
        except:
            print("permisson denied")
        for i in range(len(text)):
            y = text[i]
            emoji = emoji_list[y]
            await msg.add_reaction(emoji)
        # except:
            # await ctx.send(embed = discord.Embed(description="Referenced message not found !!",color=discord.Color.red()))

    @commands.command(aliases=['wall','wallpaper'])
    async def wallp_(self,ctx,*,query:str=None):
        page = random.randint(1,10)
        try:
            url = " "
            if query == None:
                url = f'https://api.unsplash.com/topics/wallpapers/photos?client_id=CLIENT_ID&page={page}'
                r = requests.get(url)
                r = json.loads(r.text)
                rand_int = random.randint(1,10)
                embed = discord.Embed(description=f"**[Original/Raw]({r[rand_int]['urls']['raw']})**",color=discord.Color.blue())
                embed.set_image(url=r[rand_int]['urls']['raw'])
                embed.set_footer(text=f"Picture's from {r[rand_int]['user']['username']}", icon_url=r[rand_int]['user']['profile_image']['small'])
                msg = await ctx.send(embed=embed)
                await msg.add_reaction("♥")
            else:
                url = f'https://api.unsplash.com/search/photos/?query={query}&client_id=CLIENT_ID&page={page}'
                r = requests.get(url)
                r = json.loads(r.text)
                rand_int = random.randint(1,10)
                embed = discord.Embed(description=f"**[Original/Raw]({r['results'][rand_int]['urls']['raw']})**",color=discord.Color.blue())
                embed.set_image(url=r['results'][rand_int]['urls']['raw'])
                embed.set_footer(
                    text=f"Picture's from {r['results'][rand_int]['user']['username']}", icon_url=r['results'][rand_int]['user']['profile_image']['small'])
                msg = await ctx.send(embed=embed)
                await msg.add_reaction("♥")
        except:
            await ctx.send(embed=discord.Embed(description="Failed to get images ! Try again",color=discord.Color.red()))



def setup(client):
    client.add_cog(Task(client))
