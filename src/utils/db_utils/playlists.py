import click
import json
import pandas as pd

def _clean_playlists(playlists):
    click.secho("Cleaning playlists...", fg="green")

    playlists_to_remove = []

    for playlist in playlists:
        artists = []
        albums = []

        for track in playlists[playlist]["tracks"]:
            albums.append(track["album"])
            #only consider 1st artist of the track
            artists.append(track["artist"][0]["name"])

        if len(set(artists)) < 3 and len(set(albums)) < 4:
            playlists_to_remove.append(playlist)
    
    for playlist in playlists_to_remove:
        print("Removing playlist " + playlist + " from playlists.")
        playlists.pop(playlist)
    
    print("Total playlists removed: " + str(len(playlists_to_remove)))

    return playlists

def generate_playlists(db, tracks):

    click.secho("Generating playlists by genre...", fg="green")
    
    if db._check_cache_exists("playlists.json"):
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

    playlists = _clean_playlists(playlists)

    db._cache_data(f"{db.user.user_name}/playlists.json", playlists)

    return playlists

def get_playlists_stats(db, playlists):
    playlists_stats = pd.DataFrame()
    playlist_genre = []
    playlist_size = []
    for playlist in playlists:
        playlist_genre.append(playlist)
        playlist_size.append(playlists[playlist]["size"])

    playlists_stats["genre"] = playlist_genre
    playlists_stats["size"] = playlist_size

    playlists_stats = playlists_stats.sort_values(by=["size"], ascending=False).reset_index(drop=True)
    db._cache_data(f"{db.user.user_name}/playlists_stats.csv", playlists_stats)

    return playlists_stats

# not very useful
def update_user_delete_playlists(db, user_playlists, playlists: dict):
    for playlist in list(playlists.keys()):
        try:
            user_playlists[playlist].pop(f"{playlist}")
        except:
            click.secho("ERROR: genre playlist not in user's playlist", fg="red")
    
    # update db
    db._cache_data(f"{db.user.user_name}/playlists.json", user_playlists)