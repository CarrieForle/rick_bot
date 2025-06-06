import asyncio
from download import get_title
from yt_dlp.utils import YoutubeDLError

async def foo():
    url = 'https://www.youtube.'
    
    audio_name_task = asyncio.create_task(get_title(url))
    
    try:
        await audio_name_task
    except YoutubeDLError as e:
        print(e)
    
asyncio.run(foo())