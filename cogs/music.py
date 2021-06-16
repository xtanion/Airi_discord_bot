import discord,spotipy,sqlite3,asyncio,time,youtube_dl,random
from discord.ext import commands
from discord.ext.commands.core import command
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
from datetime import datetime

youtube_dl.utils.bug_reports_message = lambda: ''
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'no_warnings': True,
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ydl_opts)


class Test(commands.Cog):
    def __init__(self, client):
        self.client = client
        # CONTAINS {'COUNT':int,'IS_PLAYING':bool,'QUEUE':[]}
        self.order = []  # KEEPS GUILD ID's THAT BOT CONNECTS TO [id1,id2,...]
        self.container = []
        # KEEPS {'NAME':'SONG NAME','URL':'SOMEHING.COM','DURATION':time}
        self.nowplaying = []
        # KEEPS {LOOP:TRUE/FALSE,SUFFLE:TRUE/FALSE,S_LIST=[s_names],D_LIST=['durations]}
        self.songlist = []
        self.sent_id = []  # KEEPS {SENT_QUEUE_ID:ID,TIME:TIME.TIME()}

    def search_yt(self, item):
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{item}", download=False)[
                    'entries'][0]
            except Exception:
                return False
            return {'url': info['url'], 'title': info['title'], 'duration': info['duration'], 'web_url': info['webpage_url']}

    def spotify_ply(self, url, n):
        print(n)
        spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id='SPOTIFY_ID', client_secret='SPOTIFY_SECRET'))
        dict = url.split('/')
        if 'playlist' in dict:
            ply_url = url
            results = spotify.playlist_tracks(ply_url, market='IN')
            # print(results['items'][0]['track']['name'])
            albums = results['items']
            while results['next']:
                results = spotify.next(results)
                albums.extend(results['items'])

            for album in albums:
                sname = (album['track']['name'])  # gives track name
                artist = (album['track']['artists'][0]
                          ['name'])  # gives artist name
                duration = time.strftime('%M:%S', time.gmtime(
                    (int(album['track']['duration_ms'])/1000)))  # gives duration
                self.container[n]['queue'].append(f'{artist} {sname}')
                self.songlist[n]['s_list'].append(f'{artist} - {sname}')
                self.songlist[n]['d_list'].append(duration)
        elif 'track' in dict:
            results = spotify.track(url, market="IN")
            sname = results['name']
            artist = results['artists'][0]['name']
            self.container[n]['queue'].append(f'{artist} {sname}')
            title = f'{artist} - {sname}'
            if (len(title) > 50):
                title = (title[:50])
            self.songlist[n]['s_list'].append(f'{title}...')
        print('spotify queued')

    def ytube_ply(self, url, n):
        #eg: https://youtube.com/playlist?list=PL9HckX-l3UzvBrAYYA9or8ewEI_D_rJy1
        dict = url.split('/')
        for words in dict:
            if words.startswith('playlist'):
                plyID = words[14:]
        youtube = build('youtube', 'v3',
                        developerKey="yOUTUBE_DATA_API_KEY")
        nextPageToken = None
        pl_request = youtube.playlistItems().list(part='contentDetails', playlistId=plyID,maxResults=50, pageToken=nextPageToken)
        pl_response = pl_request.execute()
        print("searching youtube playlist")
        vid_ids = []
        for item in pl_response['items']:
            vid_ids.append(item['contentDetails']['videoId'])
        vid_request = youtube.videos().list(
            part="contentDetails",
            id=','.join(vid_ids))
        vid_response = vid_request.execute()
        vid_ids = []
        for item in vid_response['items']:
            vid_id = item['id']
            vid_ids.append(vid_id)
            duration = (f'{item["contentDetails"]["duration"]}')
            duration = ":".join(duration[2:-1].split('M'))
            self.songlist[n]['d_list'].append(duration)
        for i in range(len(vid_ids)):
            request = youtube.videos().list(
                part="snippet", id=vid_ids[i], maxResults=5)
            response = request.execute()
            url = 'https://www.youtube.com/watch?v='+response['items'][0]['id']
            title = response['items'][0]['snippet']['title']
            self.container[n]['queue'].append(url)
            if (len(title) > 50):
                title = (title[:50])
            self.songlist[n]['s_list'].append(f'{title}..')

    def get_n(self, ctx):
        guild_id = ctx.message.guild.id
        if guild_id in self.order:
            return (int(self.order.index(guild_id)))
        else:
            return None

    @commands.command(aliases=['p', 'play'])
    async def play_function(self, ctx, *, arg=None):
        await self.test_play(ctx, arg)

    async def test_play(self, ctx, arg=None):
        n = self.get_n(ctx)
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        # voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        print(f">> n value: {n}")
        try:
            channel = ctx.author.voice.channel
        except:
            channel = None
        if arg == None:
            try:
                voice.resume()
                await ctx.message.add_reaction("▶")
            except:
                if voice == None:
                    await ctx.send(embed=discord.Embed(description="No songs in the queue !", color=discord.Color.red()))
                else:
                    await ctx.send(embed=discord.Embed(description="Song is already playing !", color=discord.Color.red()))
        else:
            if channel != None:
                if voice == None:
                    self.order.append(ctx.message.guild.id)
                    self.nowplaying.append(
                        {'name': ' ', 'url': ' ', 'duration': ' '})
                    self.container.append(
                        {'count': 0, 'is_playing': False, 'queue': []})
                    self.songlist.append(
                        {'loop': False, 'shuffle': False, 's_list': [], 'd_list': [], 'u_list': []})
                    self.sent_id.append({'queue_id': None, 'start_time': None})
                    n = self.get_n(ctx)
                    print(f'{self.container} && {n}')
                    await channel.connect()
                    print('connected')

                dict = arg.split('/')
                if 'open.spotify.com' in dict:
                    self.spotify_ply(arg, n)
                    await ctx.send(embed=discord.Embed(description=f"**Queued** {len(self.songlist[n]['s_list'])} tracks", color=discord.Color.green()))
                elif 'youtube.com' in dict:
                    msg = await ctx.send(embed=discord.Embed(description="Searching on YouTube, It may take a while.", color=discord.Color.red()))
                    self.ytube_ply(arg, n)
                    await msg.edit(embed=discord.Embed(description=f"**Queued** {len(self.songlist[n]['s_list'])} tracks", color=discord.Color.red()))
                else:
                    arg = self.search_yt(arg)
                    self.container[n]['queue'].append(arg)
                    self.songlist[n]['s_list'].append(arg['title'])
                    self.songlist[n]['d_list'].append(
                        time.strftime('%M:%S', time.gmtime(arg['duration'])))
                    self.songlist[n]['u_list'].append(arg['web_url'])
                    await ctx.send(embed=discord.Embed(description=f"**Queued** [{arg['title']}]({arg['web_url']})", color=discord.Color.blurple()))

                if self.container[n]['is_playing'] == False:
                    await self.test_music(ctx)
                else:
                    print('Added to queue')
            else:
                await ctx.message.add_reaction("⚠")
                await ctx.send(embed=discord.Embed(description="Please join a voice channel to use this command !", color=discord.Color.red()))
            # except:
                # await ctx.send(embed=discord.Embed(description="Failed to get the song ! Try Again.",color=discord.Color.red()))

    async def test_music(self, ctx):
        n = self.get_n(ctx)
        self.container[n]['is_playing'] = True
        count = self.container[n]['count']
        if self.songlist[n]['loop'] != 'one':
            self.container[n]['count'] += 1

        server = ctx.message.guild
        vc = server.voice_client
        if type(self.container[n]['queue'][count]) != dict:
            s_dict = self.search_yt(self.container[n]['queue'][count])
        else:
            s_dict = self.container[n]['queue'][count]
        url = s_dict['url']
        self.nowplaying[n]['name'] = s_dict['title']
        self.nowplaying[n]['url'] = s_dict['web_url']
        self.nowplaying[n]['duration'] = time.strftime(
            '%M:%S', time.gmtime(s_dict['duration']))
        self.sent_id[n]['start_time'] = time.time()

        vc.play(discord.FFmpegPCMAudio(url, **ffmpeg_options),
                after=lambda e: self.test_next(ctx))
        vc.source = discord.PCMVolumeTransformer(vc.source)

        embed = discord.Embed(
            description=f'**Now Playing** [{self.nowplaying[n]["name"]}]({self.nowplaying[n]["url"]})', color=discord.Color.blurple())
        await ctx.send(embed=embed)

    def test_next(self, ctx):
        n = self.get_n(ctx)
        try:
            if len(self.container[n]['queue']) > self.container[n]['count']:
                self.container[n]['is_playing'] = True
                count = self.container[n]['count']
                print(f">>>> {count}")
                if self.songlist[n]['loop'] != 'one':
                    self.container[n]['count'] += 1

                server = ctx.message.guild
                vc = server.voice_client
                if type(self.container[n]['queue'][count]) != dict:
                    s_dict = self.search_yt(self.container[n]['queue'][count])
                else:
                    s_dict = self.container[n]['queue'][count]
                url = s_dict['url']
                self.nowplaying[n]['name'] = s_dict['title']
                self.nowplaying[n]['url'] = s_dict['web_url']
                self.nowplaying[n]['duration'] = time.strftime(
                    '%M:%S', time.gmtime(s_dict['duration']))
                self.sent_id[n]['start_time'] = time.time()

                vc.play(discord.FFmpegPCMAudio(url, **ffmpeg_options),
                        after=lambda e: self.test_next(ctx))
                vc.source = discord.PCMVolumeTransformer(vc.source)

            else:
                if self.songlist[n]['loop'] == True:
                    self.container[n]['count'] = 0
                    count = self.container[n]['count']
                    self.test_next(ctx)
                else:
                    self.container[n]['is_playing'] = False
        except:
            self.container.pop(n)
            self.songlist.pop(n)

    @commands.command(aliases=['pause', 'stop', 's'])
    async def tpause_(self, ctx):
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.pause()
            await ctx.message.add_reaction("⏸")

    @commands.command(aliases=['np', 'song'])
    async def now_playing(self, ctx):
        n = self.get_n(ctx)
        y = int(time.time())
        x = int(self.sent_id[n]['start_time'])
        tp = time.strftime('%M:%S', time.gmtime(y-x))
        tn = self.nowplaying[n]['duration']
        m, s = int(tn.split(':')[0]), int(tn.split(':')[1])
        msg = ' '
        for i in range(20):
            fraction = (int(y-x)/(m*60 + s))*20
            if fraction >= i and fraction < i+1:
                msg = f"{msg}🔵"
            else:
                msg = f"{msg}▬"
        song = self.nowplaying[n]["name"]
        song = f"{song[:44]}.." if len(song) > 43 else song
        embed = discord.Embed(
            description=f"**Now Playing** [{song}]({self.nowplaying[n]['url']})", color=discord.Color.blurple())
        embed.set_footer(text=f"{msg} {tp}/{self.nowplaying[n]['duration']}")
        await ctx.send(embed=embed)

    @commands.command(aliases=['loop', 'l'])
    async def tloop_(self, ctx):
        n = self.get_n(ctx)
        if self.songlist[n]['loop'] == False:
            self.songlist[n]['loop'] = True
            await ctx.message.add_reaction("🔁")

        elif self.songlist[n]['loop'] == True:
            self.songlist[n]['loop'] = 'one'
            self.container[n]['count'] -= 1
            print(f">>> {self.container[n]['count']}")
            await ctx.message.add_reaction("🔂")

        else:
            self.songlist[n]['loop'] = False
            self.container[n]['count'] += 1
            await ctx.message.add_reaction("↪")

    @commands.command(aliases=['shuffle'])
    async def tsuffle_(self, ctx):
        n = self.get_n(ctx)
        if self.songlist[n]['shuffle'] == False:
            self.songlist[n]['shuffle'] = True
            await ctx.message.add_reaction("🔀")
        else:
            self.songlist[n]['shuffle'] = False
            await ctx.message.add_reaction("👍")

    @commands.command(aliases=['next', 'n', 'skip'])
    async def tnext_(self, ctx):
        n = self.get_n(ctx)
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if len(self.songlist[n]['s_list']) >= self.container[n]['count']:
            # ADD THE CONDITION IF IS_PLAYING, IF NEEDED
            voice.stop()
            await ctx.message.add_reaction('👌')
            await asyncio.sleep(4)
            embed = discord.Embed(
                description=f'**Now Playing** [{self.nowplaying[n]["name"]}]({self.nowplaying[n]["url"]})', color=discord.Color.blurple())
            await ctx.send(embed=embed)
        else:
            pass

    @commands.command(aliases=['prev', 'ps', 'previous'])
    async def tprevious_(self, ctx):
        n = self.get_n(ctx)
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if self.container[n]['count'] > 1:
            self.container[n]['count'] -= 2
            voice.stop()
            await ctx.message.add_reaction('👌')
            await asyncio.sleep(4)
            embed = discord.Embed(
                description=f'**Now Playing** [{self.nowplaying[n]["name"]}]({self.nowplaying[n]["url"]})', color=discord.Color.blurple())
            await ctx.send(embed=embed)
        else:
            pass

    @commands.command(aliases=['jump', 'j'])
    async def tjump_(self, ctx, num: int = None):
        if num != None:
            n = self.get_n(ctx)
            voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
            try:
                self.container[n]['count'] = num - 1
                voice.stop()
                await ctx.message.add_reaction('👌')
                await asyncio.sleep(4)
                embed = discord.Embed(
                    description=f'**Now Playing** [{self.nowplaying[n]["name"]}]({self.nowplaying[n]["url"]})', color=discord.Color.blurple())
                await ctx.send(embed=embed)
            except:
                await ctx.send(embed=discord.Embed(description="Jump index not valid !", color=discord.Color.red()))
        else:
            await ctx.send(embed=discord.Embed(description="Jump index not given !", color=discord.Color.red()))

    @commands.command(aliases=['grab'])
    async def tgrab_(self, ctx):
        n = self.get_n(ctx)
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice != None:
            embed = discord.Embed(title='Your Requesed Song :',
                                  description=f"[{self.nowplaying[n]['name']}]({self.nowplaying[n]['url']})", color=discord.Color.blurple())
            await ctx.author.send(embed=embed)
            msg = await ctx.send(embed=discord.Embed(description="Direct Message sent !!", color=discord.Color.greyple()))
            await asyncio.sleep(5)
            await msg.delete()
        else:
            await ctx.message.add_reaction("⚠")
            await ctx.send(embed=discord.Embed(description="No songs playing !!", color=discord.Color.red()))

    @commands.command(aliases=['q', 'queue'])
    async def tqueue_(self, ctx):
        n = self.get_n(ctx)
        count = self.container[n]['count'] - 1
        # count = self.container[n]['count']
        vc_id = ctx.author.voice.channel.id
        embed = await self.queue_create(vc_id, n, count)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🔼")
        await msg.add_reaction("🔽")
        self.sent_id[n]['queue_id'] = msg.id

    async def queue_create(self, vc_id, n, count):
        # print(f">> n: {n}, count-1 : {count}")
        if self.songlist[n]['loop'] == 'one':
            count += 1
        if len(self.container[n]['queue']) > 10:
            num = 10
        else:
            num = len(self.container[n]['queue'])

        songs, duration = "\n", "\n"
        start = int(count/10)*10
        end = int(count+num)
        print(f"count:{count},num:{num}")
        print(f"start: {start}, end: {end}")
        if len(self.container[n]['queue']) < end:
            end = len(self.container[n]['queue'])

        for i in range(start, end):
            if i+1 == self.container[n]["count"]:
                name = self.songlist[n]['s_list'][i]
                y = int(time.time())
                x = int(self.sent_id[n]['start_time'])
                tp = time.strftime('%M:%S', time.gmtime(y-x))
                tdelta = datetime.strptime(
                    self.nowplaying[n]['duration'], '%M:%S') - datetime.strptime(tp, '%M:%S')
                name = f'{name[:45]}..' if len(name) > 47 else name
                songs = f"{songs}\n⬐ now playing\n> {i+1}) [**{name}**]({self.nowplaying[n]['url']})\n⬑ now playing"
                duration = f"{duration}\n\u200b\n{str(tdelta)[2:]} **left**\n \u200b "
            else:
                name = self.songlist[n]['s_list'][i]
                name = f'{name[:45]}..' if len(name) > 47 else name
                songs = f"{songs}\n {i+1}) {name}"
                duration = f"{duration}\n {self.songlist[n]['d_list'][i]}"

        embed = discord.Embed(
            title='🎵 | Queued Songs', description=f'Join  <#{vc_id}>', color=discord.Color.blurple())
        embed.add_field(name='__Song Name__',
                        value=f'\n{songs}\n', inline=True)
        embed.add_field(name="__Duration__",
                        value=f'\n{duration}\n', inline=True)
        embed.add_field(
            name="\u200b", value=f'\n**{len(self.songlist[n]["s_list"])-end}** more Track(s)', inline=False)
        embed.set_footer(
            text=f"Loop : {'🔁'if self.songlist[n]['loop']== True else ('🔄' if self.songlist[n]['loop']=='one' else '❌')}      Shuffle: {'🔀'if self.songlist[n]['shuffle']== True else '❌'}")
        return embed

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            pass
        else:
            try:
                n = self.get_n(reaction)
                vc_id = user.voice.channel.id
                if reaction.message.id == self.sent_id[n]['queue_id']:
                    count = self.container[n]['count'] - 1
                    if reaction.emoji == '🔽':
                        embed = await self.queue_create(vc_id, n, count+10)
                    elif reaction.emoji == '🔼':
                        embed = await self.queue_create(vc_id, n, count)

                    await reaction.message.edit(embed=embed)
                else:
                    pass
            except:
                pass


    @commands.command(aliases=['leave'])
    async def tleave_(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        n = self.get_n(ctx)
        self.container.pop(n)
        self.songlist.pop(n)
        self.order.pop(n)

        voice.stop()
        await voice_channel.disconnect()
        await ctx.message.add_reaction("👋")

    @commands.command(aliases=['clear'])
    async def tclear_(self, ctx):
        n = self.get_n(ctx)
        self.container[n]['queue'].clear()
        self.container[n]['count'] = 0
        self.songlist[n]['s_list'].clear()
        self.songlist[n]['d_list'].clear()
        self.container[n]['is_playing'] = False
        # self.order.append(ctx.guild.id)
        print(self.order)

        voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        voice.stop()
        await ctx.send(embed=discord.Embed(description="Queue is cleared !", color=discord.Color.orange()))

    @commands.command(aliases=['remove', 'pop'])
    async def remove_(self, ctx, num: int = None):
        n = self.get_n(ctx)
        if num != None:
            song = self.songlist[n]['s_list'][num-1]
            self.container[n]['queue'].pop(num-1)
            self.songlist[n]['s_list'].pop(num-1)
            self.songlist[n]['d_list'].pop(num-1)
            if num == self.container[n]['count']-1:
                pass
            else:
                pass
            await ctx.send(embed=discord.Embed(description=f"**Removed** {song}"))
        else:
            await ctx.send(embed=discord.Embed("Argument missing ! **<number>**", color=discord.Color.red()))

    # LIKED SONGS
    @commands.command(aliases=['like'])
    async def tlike_(self, ctx):
        conn = sqlite3.connect('fav_disc.db')
        c = conn.cursor()
        x = ctx.message.author.id
        n = self.get_n(ctx)
        if self.container[n]['is_playing'] == True:
            song = self.nowplaying[n]['name']
            url = self.nowplaying[n]['url']
            duration = self.nowplaying[n]['duration']
            # ADDED URL TO
            try:
                c.execute("""CREATE TABLE liked{}(
                    id integer,
                    song text,
                    url text,
                    duration text
                    )""".format(x))
            except:
                print('db already there')
            c.execute("INSERT INTO liked{} VALUEs (?,?,?,?)".format(
                x), (x, song, url, duration))
            conn.commit()
            conn.close()
            await ctx.send(embed=discord.Embed(description="Added to Liked Songs.", color=discord.Color.green()))
        else:
            await ctx.send(embed=discord.Embed(description="No song's playing !", color=discord.Color.red()))

    @commands.command(aliases=['get'])
    async def tgetlist(self, ctx):
        id = ctx.message.author.id
        songs = " "
        conn = sqlite3.connect('fav_disc.db')
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM liked{}".format(id))
            dict = c.fetchall()
            print(dict)
            for i in range(len(dict)):
                song = dict[i][1]
                songs = f"{songs}\n{i+1}. {song}"
            conn.commit()
            conn.close()
            # print(songs)
            await ctx.send(embed=discord.Embed(description=f"**Liked Songs | {ctx.author.mention}**\n{songs}", color=discord.Color.orange()))
        except:
            await ctx.send(embed=discord.Embed(description="No Songs Found, Add songs using `.like` to see it.", color=discord.Color.red()))

    @commands.command(aliases=['dislike', 'dl'])
    async def tremove_song(self, ctx, num=None):
        id = ctx.message.author.id
        if num != None:
            num = int(num)
            conn = sqlite3.connect('fav_disc.db')
            c = conn.cursor()
            c.execute("SELECT * FROM liked{}".format(id))
            dict = c.fetchall()
            song = dict[num - 1][1]
            print(f'removed song >> {song}')
            conn.commit()
            #
            c.execute("DELETE from liked{} WHERE song='{}'".format(id, song))
            conn.commit()
            conn.close()
            await ctx.send(
                embed=discord.Embed(description="Removed from Liked Songs !", color=discord.Color.from_rgb(157, 207, 209)))

    @commands.command(aliases=['p_liked', 'play_liked', 'pliked', 'plike'])
    async def play_liked_(self, ctx, num=None):
        n = self.get_n(ctx)
        id = ctx.message.author.id
        if num != None:
            num = int(num)
            conn = sqlite3.connect('fav_disc.db')
            c = conn.cursor()
            c.execute("SELECT * FROM liked{}".format(id))
            dict = c.fetchall()
            # DELETE IF DOESN'T WORK
            url = dict[num-1][2]
            await self.test_play(ctx, url)

        else:
            conn = sqlite3.connect('fav_disc.db')
            c = conn.cursor()
            c.execute("SELECT * FROM liked{}".format(id))
            dict = c.fetchall()
            voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
            if voice == None:
                await ctx.send(embed=discord.Embed(description=f"**Queued** {len(dict)} songs.", color=discord.Color.orange()))
                await self.test_play(ctx, dict[0][2])
                n = self.get_n(ctx)
                for i in range(1, len(dict)):
                    song, url, duration = dict[i][1], dict[i][2], dict[i][3]
                    self.container[n]['queue'].append(url)
                    self.songlist[n]['s_list'].append(song)
                    self.songlist[n]['d_list'].append(duration)
            else:
                try:
                    if self.container[n]['is_playing'] == True:
                        for i in range(len(dict)):
                            self.container[n]['queue'].append(dict[i][2])
                            self.songlist[n]['s_list'].append(dict[i][1])
                            self.songlist[n]['d_list'].append(dict[i][3])
                        await ctx.send(embed=discord.Embed(description=f"**Queued** {len(dict)} songs.", color=discord.Color.orange()))
                    else:
                        await ctx.send(embed=discord.Embed(description=f"**Queued** {len(dict)} songs.", color=discord.Color.orange()))
                        await self.test_play(ctx, dict[0][2])
                        n = self.get_n(ctx)
                        for i in range(1, len(dict)):
                            self.container[n]['queue'].append(dict[i][2])
                            self.songlist[n]['s_list'].append(dict[i][1])
                            self.songlist[n]['d_list'].append(dict[i][3])

                except:
                    print('cant play !')

    @commands.command(aliases=['spotifyp', 'spp'])
    async def spotify_playlist_search(self, ctx, *, arg):
        spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id='854409f9458641bfa015c5fe8ebfb1e2', client_secret='79c4d1f14c8540629294eb6ed163e881'))
        msg = await ctx.send(embed=discord.Embed(description=f"**Searching** - {arg} on Spotify", color=discord.Color.gold()))
        var = arg
        arg = arg.split(" ")
        q = " "
        for i in range(len(arg)):
            q = f"{q}{arg[i]}%"
        q = q[1:-1]
        try:
            search = spotify.search(
                q, limit=1, offset=0, type='playlist', market='IN')
            url = search['playlists']['items'][0]['external_urls']['spotify']
            await ctx.send(url)
            await msg.delete()
            await self.test_play(ctx, url)
        except:
            await msg.edit(embed=discord.Embed(description=f"Failed to get playlist named `{var}`", color=discord.Color.orange()))

def setup(client):
    client.add_cog(Test(client))
