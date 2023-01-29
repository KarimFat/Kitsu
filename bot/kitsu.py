import discord
from discord.ext import commands
import subprocess
import asyncio

# Create a new bot instance
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Create an empty list to store the playlist
playlist = []

# This event will be triggered when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} is online!')

# Define the !play command
@bot.command()
async def play(ctx, *, url):
    vc = None
    if bot.voice_clients:
        vc = bot.voice_clients[0]
    else:
        channel = ctx.author.voice.channel
        if channel is not None:
            vc = await channel.connect()
        else:
            await ctx.send("Vous n'êtes pas connecté à un canal vocal.")
            return
    song = await get_stream_url(url)
    if song is None:
        await ctx.send("La chanson n'a pas pu être trouvée.")
        return
    if not vc.is_playing():
        vc.play(discord.FFmpegPCMAudio(song), after=lambda e: play_next(vc))
    else:
        playlist.append(url)
        await ctx.send("La chanson a bien été ajoutée à la playlist.")

async def get_stream_url(url):
    ydl_cmd = f"youtube-dl --extract-audio --audio-format mp3 -g {url}"
    stream_url = subprocess.run(ydl_cmd, shell=True, capture_output=True).stdout.decode()
    if stream_url:
        return stream_url
    else:
        return None

async def play_next(vc):
    if len(playlist) > 0:
        song = await get_stream_url(playlist.pop(0))
        if song is None:
            return
        current_audio_source = discord.FFmpegPCMAudio(song)    
        vc.play(discord.FFmpegPCMAudio(song), after=lambda e: play_next(vc))
    else:
        vc.disconnect()

# Define the !stop command
@bot.command()
async def stop(ctx):
    if bot.voice_clients:
        vc = bot.voice_clients[0]
        if vc.is_playing():
            vc.stop()

# Define the !skip command
@bot.command()
async def skip(ctx):
    vc = bot.voice_clients[0]
    vc.stop()
    await play_next(vc)

# Define the !list
@bot.command()
async def list(ctx):
    if playlist:
        await ctx.send("La playlist actuelle est :")
        for i,song in enumerate(playlist):
            await ctx.send(f"{i+1}. {song}")
    else:
        await ctx.send("La playlist est vide.")

# Define the !pause command
@bot.command()
async def pause(ctx):
    if bot.voice_clients:
        vc = bot.voice_clients[0]
        if vc.is_playing():
            vc.pause()

# Define the !resume command
@bot.command()
async def resume(ctx):
    vc = bot.voice_clients[0]
    if not vc.is_playing():
        vc.resume()

# Define the !remove command
@bot.command()
async def remove(ctx, number: int):
    try:
        song_removed = playlist.pop(number-1)
        await ctx.send(f"La chanson {song_removed} a bien été supprimée de la playlist.")
    except IndexError:
        await ctx.send("Une erreur s'est produite lors de la lecture de la chanson suivante dans la playlist.")

bot.run('MTA2ODU4NDQxNjkyMzg4NTYxOQ.Gch0vE.fG4FuzzIUB2Iiz3tEzEir-FwEdt6JZx4vSm0N8')