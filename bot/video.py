import youtube_dl as ytdl
import discord

YTDL_OPTS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": "in_playlist"
}

# Class containing information about a particular video.
class Video:

    def __init__(self, url_or_search):
        # Plays audio from (or searches for) a URL.
        video = self._get_info(url_or_search)
        video_format = video["formats"][0]
        self.stream_url = video_format["url"]
        self.video_url = video["webpage_url"]
        self.video_code = self.video_url.split("?v=", 1)[1]
        self.title = video["title"]
        self.uploader = video["uploader"] if "uploader" in video else ""
        self.thumbnail = video["thumbnail"] if "thumbnail" in video else None

    def _get_info(self, video_url):
        with ytdl.YoutubeDL(YTDL_OPTS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video = None
            if "_type" in info and info["_type"] == "playlist":
                return self._get_info(
                    info["entries"][0]["url"])  # get info for first video
            else:
                video = info
            return video

    def get_embed(self, author=None, state=None):
        # Makes an embed out of this Video's information.
        embed = discord.Embed( title=self.title, description="Song by: " + self.uploader, url=self.video_url)
        if author != None:
            embed.set_author(name="Song queued by " + author.display_name + ": ", url="https://tinyurl.com/boomermusic", icon_url=author.avatar_url)
        if state != None:
            embed.set_footer(text=f"Song is #{len(state.playlist)} in queue on page {state.pages}.")
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        return embed
