import json
import os
import pandas as pd
import click

from .spotify import SpotifyApi
from .user import User
from .definitions import CACHE_PATH
# DB is local json files

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

    def _clean_tracks(self, raw_tracks):
        #raw_tracks = raw_tracks["items"]

        # list of dicts containing song info
        clean_tracks = []

        for song in raw_tracks:
            if song["track"]["artists"] == []:
                artists = []
            else:
                artists = [artist for artist in song["track"]["artists"] ]
            
            clean_track = {
                "artist": artists,
                "album": song["track"]["album"]["name"],
                "track_name": song["track"]["name"],
                "track_id": song["track"]["id"],
                "track_uri": song["track"]["uri"]
                #"href" = song["track"]["href"]
            }
            
            clean_tracks.append(clean_track)

        return clean_tracks

    def __add_songs_details(clean_tracks):
        pass

    def __update_user_add_playlists(self, playlists: dict):
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

    def _clean_playlists(self, playlists):
        print("Cleaning playlists...")

        playlists_to_remove = []

        for playlist in playlists:
            artists = []
            albums = []

            for track in playlists[playlist]["tracks"]:
                albums.append(track["album"])
                #only consider 1st artist of the track
                artists.append(track["artist"][0]["name"])

            if len(set(artists)) < 3 or len(set(albums)) < 2:
                playlists_to_remove.append(playlist)
        
        for playlist in playlists_to_remove:
            print("Removing playlist " + playlist + " from playlists.")
            playlists.pop(playlist)
        
        print("Total playlists removed: " + str(len(playlists_to_remove)))

        return playlists

    def _get_tracks_genre_from_artist(self, clean_tracks):
        genre_tracks, artist = self.user.connection.get_tracks_genre_from_artist(clean_tracks)
        # cache_artist_data
        if artist:
            self._cache_data("/artist_info.json", artist)

        return genre_tracks
    
    def get_liked_songs(self, songs_number):
        ##!! à revoir
        # check if songs by genre cache exists
        if self._check_cache_exists(f"{self.user.user_name}/genre_clean_songs.json"):
            print("Reading cache genre songs...")
            genre_liked_songs = self._read_cache(f"{self.user.user_name}/genre_clean_songs.json") 

        else:
            #check if cache liked songs exists
            if self._check_cache_exists(f"{self.user.user_name}/clean_songs.json"):
                print("Reading cache liked songs...")
                clean_liked_songs = self._read_cache(f"{self.user.user_name}/clean_songs.json") 

            else:
                # fetch liked songs from spotify account with api
                click.secho("No cache! Fetching recent liked songs...", fg="yellow")
                liked_songs = self.user.connection.fetch_liked_songs(songs_number)
                
                clean_liked_songs = self._clean_tracks(liked_songs)
                click.secho("Caching data...", fg="green")
                self._cache_data(f"{self.user.user_name}/clean_songs.json", clean_liked_songs)

            #assign genres to song based on artists genre
            genre_liked_songs = self._get_tracks_genre_from_artist(clean_liked_songs)
 
            # cache songs with genre information
            self._cache_data(f"{self.user.user_name}/genre_clean_songs.json", genre_liked_songs)


        return genre_liked_songs

    # not very useful
    def update_user_delete_playlists(self, playlists: dict):

        # read db
        with open("playlists.json") as f_in:
                user_playlists = json.load(f_in)  

        for playlist in list(playlists.keys()):
            try:
                user_playlists[playlist].pop(f"{playlist}")
            except:
                click.secho("ERROR: genre playlist not in user's playlist", fg="red")
        
        # update db
        self._cache_data(f"{self.user.user_name}/playlists.json", user_playlists)
        return

    def generate_playlists(self, tracks):
        click.secho("Generating playlists by genre...", fg="green")
        
        if self._check_cache_exists("playlists.json"):
            print("Reading cache playlists...")
            with open("playlists.json") as f_in:
                playlists = json.load(f_in)
        else:
            playlists = {}

        for track in tracks:
            genres = track["genres"]
            
            for genre in genres:
                if genre not in list(playlists.keys()):
                    print(f"Creating playlist {genre}")
                    playlists[genre] = {"description" : f"Automatically generated \'{genre}\' playlist :magic_jean:", "tracks" : [], "size" : 0}
                    playlists[genre]["tracks"].append(track)
                    playlists[genre]["size"] += 1
                else:
                    if track not in playlists[genre]["tracks"]:
                        # adding track to playlist
                        playlists[genre]["tracks"].append(track)
                        playlists[genre]["size"] += 1
                        print(f"Track added to playlist {genre} - now contains " + str(playlists[genre]["size"]) + " tracks.")
                    else:
                        click.secho("Track " + str(playlists[genre]["size"]) + " already exists in playlist", fg="yellow")

        playlists = self._clean_playlists(playlists)

        self._cache_data(f"{self.user.user_name}/playlists.json", playlists)

        return playlists

    def get_playlists_stats(self, playlists):
        playlists_stats = pd.DataFrame()
        playlist_genre = []
        playlist_size = []
        for playlist in playlists:
            playlist_genre.append(playlist)
            playlist_size.append(playlists[playlist]["size"])

        playlists_stats["genre"] = playlist_genre
        playlists_stats["size"] = playlist_size

        playlists_stats = playlists_stats.sort_values(by=["size"], ascending=False).reset_index(drop=True)
        self._cache_data(f"{self.user.user_name}/playlists_stats.csv", playlists_stats)

        return playlists_stats

    def user_write_spotify_playlists(self, playlists):
        self.user.connection.write_spotify_playlist(self.user.spotify_id, playlists)
        # update user playlists 
        #self.__update_user_add_playlists(playlists)

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
        if self._check_cache_exists(f"{self.user.user_name}/genre_clean_songs.json"):
            last_track = self._get_last_track()
            new_tracks_raw = self.user.connection.get_new_tracks(last_track)
            new_tracks_clean = self._clean_tracks(new_tracks_raw)
            new_tracks = self._get_tracks_genre_from_artist(new_tracks_clean)
            self._user_add_tracks(new_tracks)

            click.secho(f"Liked tracks successfully updated for {self.user.user_name}", fg="green")
        
        else:
            click.secho(f"No saved songs to update for {self.user.user_name}", fg="red")
            
        
    ## anniv anne
    def get_playlist(self, playlist_id):        
        playlist = self.user.connection.fetch_playlist(playlist_id)

        return playlist
    
    def delete_user_playlist_old(self):
        self.user.connection.delete_generated_playlist()

    def format_playlist(self, playlist):

        songs = playlist["tracks"]["items"]

        playlist_anne = {
            "HB SHEWRYYYY <3": {"description" : "À écouter en ce jour spécial. Quand j'écoute ces morceaux je pense à toi, j'espère que toi aussi. Je t'aime ❤️ Janus", "tracks" : [], "size" : 0}
        }

        for song in songs:
            clean_song = {
                "track_uri": song["track"]["uri"]
            }
            playlist_anne["HB SHEWRYYYY <3"]["tracks"].append(clean_song)
        
        return playlist_anne