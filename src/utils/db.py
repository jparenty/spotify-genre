import json
import os
import click

from utils.spotify import SpotifyApi
from utils.user import User
from utils.definitions import CACHE_PATH
# DB is local json files

import utils.db_utils.track as track
import utils.db_utils.playlists as playlist

class DbUtil(SpotifyApi):

    def __init__(self, user_name) -> None:
        #@click.command()
        def _get_user(user_name):
            user = User.get_user(user_name)

            if user == None:
                new_user = click.prompt(click.style("Unknown user, create user? (True/False)", fg='yellow'), type=bool)
                if new_user:
                    spotify_id = click.prompt(click.style("Enter spotify ID", fg='yellow'), type=str)
                    user = User(user_name=user_name, spotify_id=spotify_id)
                    self._cache_data(f"{user_name}/user.json", user.to_json())
                else:
                    return Exception("Unknown user, exiting...")

            return user       

        self.user = _get_user(user_name)
        

    def _cache_data(self, path, data):

        extension = path.split(".")[-1]
        if extension == "json":
            file = open(f"{CACHE_PATH}/{path}", "w")
            file.write(json.dumps(data, indent=4))
            file.close
            return
        elif extension == "csv":
            data.to_csv(f"{CACHE_PATH}/{path}")
            return
        else:
            return TypeError("Data type not supported by cache_data method")
    
    def _check_cache_exists(self, path):
        if os.path.exists(f"{CACHE_PATH}/{path}"):
            return True
        else:
            return False
    
    def _read_cache(self, path):
        with open(f"{CACHE_PATH}/{path}") as f:
            data = json.load(f)
            return data

    def _add_songs_details(clean_tracks):
        pass

    def _update_user_add_playlists(self, playlists: dict):
        ## flag user playlists that are written on the spotify account

        # read db
        with open("playlists.json") as f_in:
                user_playlists = json.load(f_in)  

        # try to flag the user playlists
        for playlist in list(playlists.keys()):
            try:
                user_playlists[playlist] = playlists[playlist]["spotify_id"]
            except:
                click.secho("ERROR: genre playlist not in user's playlist", fg="red")
        
        # update db
        self._cache_data(f"{self.user.user_name}/playlists.json", playlists)
    
    def get_user_tracks(self, tracks_number):
        genre_liked_songs = track.get_user_tracks(self, tracks_number)
        return genre_liked_songs

    # not very useful
    def update_user_delete_playlists(self, playlists: dict):
        user_playlists = self._read_cache(f"{self.user.user_name}/playlists.json")
        playlist.update_user_delete_playlists(user_playlists)

    def generate_playlists(self, tracks):
        playlists = playlist.generate_playlists(self, tracks)
        return playlists

    def get_playlists_stats(self, playlists):
        playlists_stats = playlist.get_playlists_stats(self, playlists)
        return playlists_stats

    def user_write_spotify_playlists(self, playlists):
        self.user.connection.write_spotify_playlist(self.user.spotify_id, playlists)

    def user_delete_all_playlists(self):
        user_playlists = self.user.connection.update_user_delete_all_playlists()
        # update user playlists 
        self._cache_data(f"{self.user.user_name}/playlists.json", user_playlists)

    def _get_last_track(self):
        user_tracks = self._read_cache(f"{self.user.user_name}/clean_songs.json")
        return user_tracks[0]

    def _user_add_tracks(self, new_tracks):
        user_tracks = self._read_cache(f"{self.user.user_name}/genre_clean_songs.json")
        user_tracks.extend(new_tracks)
    
        self._cache_data(f"{self.user.user_name}/genre_clean_songs.json", user_tracks)

    def update_liked_songs(self):
        track.update_liked_songs()