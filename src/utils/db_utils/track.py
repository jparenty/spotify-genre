import click

def _clean_tracks(raw_tracks):
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

def _get_tracks_genre_from_artist(db, clean_tracks):
    genre_tracks, artist = db.user.connection.get_tracks_genre_from_artist(clean_tracks)
    # cache_artist_data
    if artist:
        db._cache_data("/artist_info.json", artist)

    return genre_tracks

def get_user_tracks(db, songs_number):
        
    ##!! à revoir
    # check if songs by genre cache exists
    if db._check_cache_exists(f"{db.user.user_name}/genre_clean_songs.json"):
        click.secho("Reading cache genre songs...", fg="green")
        genre_liked_songs = db._read_cache(f"{db.user.user_name}/genre_clean_songs.json") 

    else:
        #check if cache liked songs exists
        if db._check_cache_exists(f"{db.user.user_name}/clean_songs.json"):
            click.secho("Reading cache liked songs...", fg="yellow")
            clean_liked_songs = db._read_cache(f"{db.user.user_name}/clean_songs.json") 

        else:
            # fetch liked songs from spotify account with api
            click.secho("No cache! Fetching recent liked songs...", fg="red")
            liked_songs = db.user.connection.fetch_liked_songs(songs_number)
            
            clean_liked_songs = _clean_tracks(liked_songs)
            click.secho("Caching data...", fg="green")
            db._cache_data(f"{db.user.user_name}/clean_songs.json", clean_liked_songs)

        #assign genres to song based on artists genre
        genre_liked_songs = _get_tracks_genre_from_artist(db, clean_liked_songs)

        # cache songs with genre information
        db._cache_data(f"{db.user.user_name}/genre_clean_songs.json", genre_liked_songs)


    return genre_liked_songs

def update_liked_songs(db):
    
    if db._check_cache_exists(f"{db.user.user_name}/genre_clean_songs.json"):
        last_track = db._get_last_track()
        new_tracks_raw = db.user.connection.get_new_tracks(last_track)
        new_tracks_clean = _clean_tracks(new_tracks_raw)
        new_tracks = _get_tracks_genre_from_artist(db, new_tracks_clean)
        db._user_add_tracks(new_tracks)

        click.secho(f"Liked tracks successfully updated for {db.user.user_name}", fg="green")
    
    else:
        click.secho(f"No saved songs to update for {db.user.user_name}", fg="red")
        