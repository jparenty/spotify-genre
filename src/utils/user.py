import json
import click

from .spotify import SpotifyApi

from .definitions import CACHE_PATH

class User:

    def __init__(self, user_name: str, spotify_id: str):
        self.user_name = user_name
        self.spotify_id = spotify_id
        self.connection = SpotifyApi(user_name=user_name, spotify_id=spotify_id)

    @staticmethod
    def get_user(user_name):
        try:
            with open(f"{CACHE_PATH}/{user_name}/user.json") as f:
                user = json.load(f)
                user = User(
                    user_name = user["user_name"],
                    spotify_id = user["spotify_id"]
                )
                #! attention list pourquoi?
                user.spotify_id = user.spotify_id
            
        except FileNotFoundError:
            user = None
        except Exception as e:
            return e
        
        return user
    
    def to_json(self):
        user = {
            "user_name" : self.user_name,
            "spotify_id" : self.spotify_id
        }
        return user
