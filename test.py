import lavalink
import toml
import pandas as pd
import spotipy
from spotipy import SpotifyClientCredentials

cfg = toml.load("_config.toml")

client_credentials_manager = SpotifyClientCredentials(
    client_id=cfg['spotify']['id'],
    client_secret=cfg['spotify']['secret']
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def sp_get_playlist( playlist_id: str) -> pd.DataFrame:
    playlist_features = ['artist', 'track_name', 'album']
    playlist_df = pd.DataFrame(columns=playlist_features)

    # playlist = self.spotify.user_playlist_tracks(creator, playlist_id)['items']
    playlist = sp.playlist_tracks(playlist_id)['items']

    for track in playlist:
        playlist_features = {}

        playlist_features["artist"] = track["track"]["album"]["artists"][0]["name"]
        playlist_features["album"] = track["track"]["album"]["name"]
        playlist_features["track_name"] = track["track"]["name"]

        track_df = pd.DataFrame(playlist_features, index=[0])
        playlist_df = pd.concat([playlist_df, track_df], ignore_index=True)

    return playlist_df

query = "https://open.spotify.com/playlist/5nekAUrBhG8VlcMAojn3Va?si=7fa9da8013be411b"

id = query.split("/")[-1].split("?")[0]
list = sp_get_playlist(id)

f = open("./test.log", "w")
f.write(f"{results}")
f.close()
