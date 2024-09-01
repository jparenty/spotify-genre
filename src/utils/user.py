import json
import click

from .spotify import SpotifyApi

CACHE_PATH = "../../cache"

class User:

    def __init__(self, user_name: str, spotify_id: str):
        self.user_name = user_name
        self.spotify_id = spotify_id,
        self.connection = SpotifyApi(user_name=user_name)

    @staticmethod
    def get_user(user_name):
        breakpoint()
        try:
            with open(f"{CACHE_PATH}/{user_name}/user.json") as f:
                user = json.load(f)
                user = User(
                    user_name = user["user_name"],
                    spotify_id = user["spotify_id"],
                )
        except FileNotFoundError:
            user = None
        except Exception as e:
            print(f"An error occurred: {e}")

        return user
