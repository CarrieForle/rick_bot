import discord

async def checkInSameVC(interaction: discord.Interaction):
    """Check whether the bot is in the same voice channel as the caller and send appropriate message when it's not"""
    voice_client = interaction.guild.voice_client
    v = interaction.user.voice
    vc = v.channel if v is not None else None
    
    if voice_client is None:
        await interaction.response.send_message("我不在語音頻道呀", ephemeral=True)
        return False
    
    if vc != voice_client.channel:
        await interaction.response.send_message("你必須跟我在同一個語音頻道", ephemeral=True)
        return False
    
    return True