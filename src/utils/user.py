import json
import click

from .spotify import SpotifyApi

from .definitions import CACHE_PATH

class User:

    def __init__(self, user_name: str, spotify_id: str):
        self.user_name = user_name
        self.spotify_id = spotify_id,
        self.connection = SpotifyApi(user_name=user_name)

    @staticmethod
    def get_user(user_name):
        try:
            with open(f"{CACHE_PATH}/{user_name}/user.json") as f:
                user = json.load(f)
                breakpoint()
                user = User(
                    user_name = user["user_name"],
                    spotify_id = user["spotify_id"]
                )
                user.spotify_id = user.spotify_id[0]
                breakpoint()
            
        except FileNotFoundError:
            user = None
        except Exception as e:
            return e
        
        return user

    def get_last_song(self):
        try:
            with open(f"{CACHE_PATH}/{self.user_name}/genre_clean_songs.json") as f:
                songs = json.load(f)
                last_song = songs[songs.keys[0]]
                breakpoint()
        except FileNotFoundError:
            return f"No saved songs for {self.user_name}"
        except Exception as e:
            return e
