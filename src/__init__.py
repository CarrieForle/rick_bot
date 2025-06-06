import discord
from discord.ext import commands
from discord import app_commands
from download import download, get_title
from util import *
from yt_dlp.utils import YoutubeDLError
import os
import asyncio
import random

token = os.environ.get('TOKEN')
assert token is not None

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents, command_prefix='/')
sone_queue = []

@bot.tree.command(description="播放音樂")
@discord.app_commands.rename(url="網址")
async def play(interaction: discord.Interaction, url: str):
    v = interaction.user.voice
    vc = v.channel if v is not None else None
    
    if vc is None:
        await interaction.response.send_message("你必須在語音頻道才能使用指令")
        return
    
    await interaction.response.defer(thinking=True)
    audio_name_task = asyncio.create_task(get_title(url))
    
    voice_client: discord.VoiceClient = interaction.guild.voice_client
    
    if voice_client:
        await voice_client.move_to(vc)
    else:
        voice_client = await vc.connect()
     
    try:
        audio_name = await audio_name_task
        await interaction.followup.send(f"播放： {audio_name}")
    except YoutubeDLError as ex:
        await interaction.followup.send(f"我無法讀取到音樂")
        
        return
        
    try:
        filepath = await download(url)
    except YoutubeDLError as ex:
        await interaction.followup.send(f"下載音樂發生錯誤: {ex}")
        
        return
    
    print(f"Downloaded '{filepath}'")
    
    source = discord.FFmpegOpusAudio(source=filepath)
    voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)
    
@bot.tree.command(description="停止播放")
async def stop(interaction: discord.Interaction):
    if not await checkInSameVC(interaction):
        return
    
    voice_client: discord.VoiceClient = interaction.guild.voice_client
    
    if not voice_client.is_playing():
        await interaction.response.send_message("我沒在播音樂啊", ephemeral=True)
        return
    
    voice_client.stop()    
    await interaction.response.send_message("已停止播放")
    
@bot.tree.command(description="暫停播放")
async def pause(interaction: discord.Interaction):
    if not await checkInSameVC(interaction):
        return
    
    voice_client: discord.VoiceClient = interaction.guild.voice_client
    
    if voice_client.is_paused():
        await interaction.response.send_message("我已經暫停了啊", ephemeral=True)
        return
    
    # In case of precedent voice_client.stop(), 
    # the check above would pass
    if not voice_client.is_playing():
        await interaction.response.send_message("我沒在播音樂啊", ephemeral=True)
        return
        
    voice_client.pause()
    await interaction.response.send_message("已暫停播放")

@bot.tree.command(description="繼續播放")
async def resume(interaction: discord.Interaction):
    if not await checkInSameVC(interaction):
        return
    
    voice_client: discord.VoiceClient = interaction.guild.voice_client
    
    if voice_client.is_playing():
        await interaction.response.send_message("我已經在播放了啊", ephemeral=True)
        return
    
    voice_client.resume()
    await interaction.response.send_message("繼續播放")
    
@bot.tree.command(description="離開語音頻道")
async def leave(interaction: discord.Interaction):
    if not await checkInSameVC(interaction):
        return
    
    voice_client: discord.VoiceClient = interaction.guild.voice_client
    
    voice_client.disconnect()
    await interaction.response.send_message("")

@bot.tree.command(description="擲骰子")
@discord.app_commands.rename(min="最小值", max="最大值")
async def roll(interaction: discord.Interaction, min: app_commands.Range[int, 1, 1_000_000]=1, max: app_commands.Range[int, 1, 1_000_000]=100):
    if min > max:
        interaction.response.send_message("最小值不能大於最大值", ephemeral=True)
        return
    
    rd = random.randrange(min, max + 1)
    await interaction.response.send_message(f"{min} ~ {max}\n🎲 {rd} 🎲")
    
@bot.tree.command(name="yesorno", description="有選擇障礙嗎？")
async def roll(interaction: discord.Interaction):
    rd = random.randrange(0, 2)
    msg = "好" if rd == 0 else "不好"
    await interaction.response.send_message(msg)
    
@bot.command()
async def sync(ctx: commands.Context):
    """
    Call `bot.tree.sync()` manually
    """
    print("sync command")
    if ctx.author.id == 274145940229718020:
        await bot.tree.sync()
        await ctx.send('Command tree synced.')
    else:
        await ctx.send('You must be the owner to use this command!')
        
@bot.event
async def on_ready():
    await bot.tree.sync()
    print('ready')

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    await interaction.response.send_message(f"發生錯誤: {error}")

bot.run(token)