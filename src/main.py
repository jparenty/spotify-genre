import click

from utils.db import DbUtil
#user_name = "Max Germano"
#user_id = "1275902458"
#user_name = "11170137944" # antoine
#user_id = "hippolyte"
user_name = "12165665581"


@click.command()
@click.option("-u",'--user_name')
@click.option("-s",'--songs_number')
def main(user_name, songs_number):
    songs_number = int(songs_number)
    #print current user information
    user = DbUtil(user_name=user_name)
    
    

    genres_liked_songs = user.get_liked_songs(songs_number)

    #create playlists based on genre
    playlists = user.generate_playlists(genres_liked_songs)

    playlists_stats = user.get_playlists_stats(playlists)

    breakpoint()
    
    print("Filtering playlists ...")
    # filter playlists to keep only biggest playlists
    playlists_keep = playlists_stats.loc[playlists_stats["size"] > 3].loc[0:69]["genre"].to_list()
    #playlists_keep = playlists_stats.loc[playlists_stats["size"] > 3]

    #playlists_keep = playlists_stats["genre"].loc[0:79].to_list()
    playlists_keep.append("israeli indie")
    jazz_playlists = playlists_stats.loc[playlists_stats["genre"].str.contains("jazz")]["genre"].to_list()

    playlists_keep = playlists_keep + jazz_playlists
    #playlists_filtered = keep_popular_playlist(threshold)

    key_to_remove = set(playlists_stats["genre"].to_list()) - set(playlists_keep)

    # remove key that are not in playlists_keep
    for key in list(key_to_remove):
        playlists.pop(key)


    #recap(playlists)
    breakpoint()
    return



if __name__ == '__main__':
    main()