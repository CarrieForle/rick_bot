from pathlib import Path
import tempfile
from yt_dlp import YoutubeDL
import asyncio

class Downloader():
    def __init__(self, ytdlp: YoutubeDL):
        self.ytdlp = ytdlp
        self.filepath = None
        self.ytdlp.add_post_hook(self._post_hook)
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.ytdlp._post_hooks.remove(self._post_hook)
        return False
    
    def get_title(self, url):
        """Get the title of audio without downloading"""
        
        return self.ytdlp.extract_info(url, download=False)['title']
    
    def download(self, url: str):
        """Download audio"""
        
        self.ytdlp.download(url)
        
        # TODO Resolve potential race condition between download() and _post_hook()
        
        return self.filepath
    
    def _post_hook(self, filepath):
        self.filepath = filepath

_ytdlp = YoutubeDL(params={
    "format": "bestaudio",
    "outtmpl": "%(title)s.%(ext)s",
    "restrictfilenames": True,
    "quiet": True,
    "no_warnings": True,
    "noprogress": True,
})

async def download(url: str):
    """Download audio from url"""
    with Downloader(_ytdlp) as downloader:
        filepath = downloader.download(url)
        
    return filepath

async def get_title(url: str):
    """Get the title of audio without downloading"""
    with Downloader(_ytdlp) as downloader:
        title = downloader.get_title(url)
        
    return title