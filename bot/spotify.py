# ---------------------------------- Imports --------------------------------- #
import logging

import discord
from discord.ext import commands
from discord_slash import SlashContext
from lavalink import DefaultPlayer
import spotipy
from spotipy import SpotifyClientCredentials
import pandas as pd

from . import config
from . import util

# ---------------------------------- Config ---------------------------------- #
cfg = config.load_config()

client_credentials_manager = SpotifyClientCredentials(
    client_id=cfg['spotify']['id'], 
    client_secret=cfg['spotify']['secret']
)
spotify = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

# ---------------------------------------------------------------------------- #
#                              Methods / Commands                              #
# ---------------------------------------------------------------------------- #

# --------------------------- ANCHOR SPOTIFY self --------------------------- #
# Gets spotify playlist info and returns a pandas dataframe of all the songs in
# the playlist.

def sp_get_playlist(playlist_id: str) -> dict:
    playlist_features = ['artist', 'track_name', 'album']
    playlist_df = pd.DataFrame(columns=playlist_features)

    # playlist = spotify.user_playlist_tracks(creator, playlist_id)['items']
    playlist = spotify.playlist_tracks(playlist_id)['items']
    playlist_title = spotify.playlist(
        playlist_id, 
        fields="name"
    )['name']

    for track in playlist:
        playlist_features = {}

        playlist_features["artist"] = track["track"]["album"]["artists"][0]["name"]
        playlist_features["album"] = track["track"]["album"]["name"]
        playlist_features["track_name"] = track["track"]["name"]

        track_df = pd.DataFrame(playlist_features, index=[0])
        playlist_df = pd.concat([playlist_df, track_df], ignore_index=True)

    playlist = {'title': playlist_title, 'data': playlist_df}

    return playlist

# ----------------------- ANCHOR SPOTIFY QUERY HANDLER ----------------------- #
# Takes spotify playlist link, processes it into pandas data, and uses that data
# to search youtube for all the songs. list of songs returned as a dict in a
# format readable by lavalink as if it were a normal youtube playlist.

async def spotify_query_handler(ctx: SlashContext, player: DefaultPlayer, query: str) -> dict:
    if "playlist" in query:
        playlist_id = query.split("/")[-1].split("?")[0]
        playlist = sp_get_playlist(playlist_id)
        tracks = []

        embed = discord.Embed(color=discord.Color.blurple())
        embed.set_author(
            name=f"Loading spotify playlist: {playlist['title']}",
            url="https://tinyurl.com/boomermusic",
            icon_url="https://i.imgur.com/dpVBIer.png"
        )
        embed.description = util.progress_bar(
            0, 
            len(playlist['data'])
        )
        embed.set_footer(
            text="Please note: This can take a long time for playlists larger than 20 songs - sorry!"
        )

        logging.info("Trying to get spotify playlist. Better get some popcorn while you wait.")
        loading_msg = await ctx.send(embed=embed)
        await loading_msg.edit(embeds=[embed])

        for index, row in playlist['data'].iterrows():
            track = await player.node.get_tracks(f"ytsearch:{row['track_name']} by {row['artist']}")
            try:
                track = track['tracks'][0]
            except:
                logging.warn("Play failed! Track not found.")

            tracks.append(track)
            if len(tracks) % 1 == 0:
                embed.description = util.progress_bar(
                    len(tracks), 
                    len(playlist['data'])
                )
                await loading_msg.edit(embeds=[embed])

        embed.description = util.progress_bar(
            len(tracks), 
            len(playlist['data'])
        )
        await loading_msg.edit(content="Playlist loaded! :tada:")
        logging.info("Finished gathering spotify tracks. Finally.")

        results = {
            'playlistInfo': {
                'selectedTrack': 0,
                'name': playlist['title']
            },
            'loadType': 'PLAYLIST_LOADED',
            'tracks': tracks
        }
        
        return results