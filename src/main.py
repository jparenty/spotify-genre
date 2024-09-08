import click

from utils.db import DbUtil

@click.command()
@click.option("-u",'--user_name')
@click.option("-s",'--songs_number')
def main(user_name, songs_number):
    songs_number = int(songs_number)
    #print current user information
    user = DbUtil(user_name=user_name)
    
    breakpoint()

    genres_liked_songs = user.get_user_tracks(songs_number)
    
    breakpoint()
    user.update_liked_songs()

    #create playlists based on genre
    playlists = user.generate_playlists(genres_liked_songs)

    playlists_stats = user.get_playlists_stats(playlists)
    
    print("Filtering playlists ...")
    # filter playlists to keep only biggest playlists
    playlists_keep = playlists_stats.loc[playlists_stats["size"] > 3].loc[0:69]["genre"].to_list()
    #playlists_keep = playlists_stats.loc[playlists_stats["size"] > 3]

    #playlists_keep = playlists_stats["genre"].loc[0:79].to_list()
    extra_playlist = ["balkan post-punk", "metropopolis", "polish post-punk","hypnagogic pop","afrofuturism","deconstructed club","hyperpop","afropop","neue deutsche welle","neo-kraut","malian blues","croatian rock"]
    playlists_keep = playlists_keep + extra_playlist
    #playlists_filtered = keep_popular_playlist(threshold)

    key_to_remove = set(playlists_stats["genre"].to_list()) - set(playlists_keep)

    # remove key that are not in playlists_keep
    for key in list(key_to_remove):
        playlists.pop(key)

    click.secho("Ready to write playlists!", fg="green")
    breakpoint()
    user.user_write_spotify_playlists(playlists)
    #recap(playlists)
    return



if __name__ == '__main__':
    main()