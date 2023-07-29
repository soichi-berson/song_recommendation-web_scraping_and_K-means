import pandas as pd
from sklearn.preprocessing import StandardScaler
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import time
import pickle
from credentials import *
import streamlit as st



sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))
songs = pd.read_csv('../data/song_recommender.csv')
songs.isnull().sum()
songs = songs.dropna()

# Change all string values in the dataframe to lowercase
songs[['Artist', 'Title']] = songs[['Artist', 'Title']].applymap(lambda s: s.lower() if type(s) == str else s)

import pandas as pd

# assume df is your DataFrame
def search_song(title, artist):
    
    query = "tracks: "+title+" artist: "+artist

    try:
        result = sp.search(query, limit=1)
        song_id = result['tracks']['items'][0]['id']
    except:
        song_id = "not_found"

    return song_id 


# Function to get the image URL for a Spotify track ID
def get_track_image_url(track_id):
    track_info = sp.track(track_id)
    images = track_info['album']['images']
    # You can choose the image size you prefer, for example, images[0] for the largest image.
    image_url = images[0]['url'] if images else None
    return image_url



def song_is_hot(df: pd.DataFrame, song_id:str):
    if (song_id in df['id'].values):
        return "Yes"
    else:
        return "No"

def get_audio_features(song_id):
    
    # Retrieve the audio features for each chunk
    audio_features = sp.audio_features(song_id)[0]
    
    audio_features_dict = { key: [audio_features[key]] for key in list(audio_features.keys())}
    
    df = pd.DataFrame(audio_features_dict)

    return df

def scale_audio_features(df: pd.DataFrame, filename="../scaler/scaler.pickle"):
    
    try:
        with open(filename, "rb") as file:
            scaler = pickle.load(file)
    except:
        print("Scaler not found!!!")
    
    scaled_audio_features_np = scaler.transform(df[['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence','tempo']])

    scaled_audio_features_df = pd.DataFrame(scaled_audio_features_np, columns=['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence','tempo'])

    return scaled_audio_features_df


def get_user_song_cluster(scaled_audio_features_df: pd.DataFrame, filename="../pickle/kmeans_44.pickle"):
    
    try:
        with open(filename, "rb") as file:
            model = pickle.load(file)
    except FileNotFound:
        print("Model not found!!!")
              
    user_song_cluster = model.predict(scaled_audio_features_df)[0]
              
    return user_song_cluster

import sys
    
def recommend_song(df, song_title, artist_name):
    
    song_title = song_title
    artist_name = artist_name
        
    # Get user's song id
    song_id = search_song(song_title, artist_name)
        
    # Determine if the user's song is hot
    is_hot = song_is_hot(df, song_id)
        
    # Get the audio_features of user's song
    user_song_audio_features_df = get_audio_features([song_id])
    
    # Scale the user's song audio features
    user_song_scaled_audio_features_df = scale_audio_features(user_song_audio_features_df)
        
    # Determine the user's song cluster
    user_song_cluster = get_user_song_cluster(user_song_scaled_audio_features_df)

    # choose the songs
    rec_song = df[df['K44'] == user_song_cluster]
    if song_title in rec_song["Title"]:
        rec_song = rec_song[rec_song['Title'] != song_title]
    # choose sample 5 songs
    rec_song = rec_song.sample(5)

    #rec_song['Listen to Your Songs Now'] = 'https://open.spotify.com/track/' + rec_song['id']



    if len(rec_song) == 0:
        st.subheader("Sorry. There is no reccommendations from our storage. Rerun and search another one.")
        sys.exit()

    
    st.subheader("We recommend you the following songs")
              
    #with pd.option_context('display.max_colwidth', None):
    #    st.table(rec_song[['Title','Artist','Listen to Your Songs Now']])   

    for i in range(len(rec_song)):


        one_song = rec_song.iloc[i, :]

        #put index
        index = i + 1
        st.subheader(str(index) + '.')

        # Get the URL
        query = "track:{} artist:{}".format(one_song['Title'], one_song['Artist'])
        result = sp.search(q=query, limit=1, type='track')
        song = result['tracks']['items'][0]
        url = song['external_urls']['spotify']

        #ID
        ID = search_song(one_song['Title'], one_song['Artist'])
        

        # Get the image
        image_url = get_track_image_url(ID)

        # Display the image on Streamlit
        if image_url == None:
            st.write('Image not available.')
        else:
            st.image(image_url, caption='Album Cover', use_column_width=True)

        st.subheader(f"Title: {one_song['Title'].title()},    Artist: {one_song['Artist'].title()} ")
        st.subheader(f"Listen Now: {url}")
        st.subheader("   ")
        st.subheader("   ")





def get_song_info_from_spotify(song_id):
    
    track_info = sp.track(song_id)
    title = track_info['name']
    artist = track_info['artists'][0]['name']
    return title, artist


def get_artist_image(artist_name):
    # Search for the artist using the artist name
    results = sp.search(q=artist_name, type='artist', limit=1)

    # Check if any artists were found in the search results
    if results['artists']['total'] > 0:
        artist_info = results['artists']['items'][0]
        # Get the image URL of the artist
        if artist_info['images']:
            image_url = artist_info['images'][0]['url']
            return image_url
        else:
            return None
    else:
        return None

def get_artist_image_from_song_id(song_id):
    # Get track information using the song ID
    track_info = sp.track(song_id)

    # Extract the artist name from the track information
    artist_name = track_info['artists'][0]['name']

    # Search for the artist using the artist name
    results = sp.search(q=artist_name, type='artist', limit=1)

    # Check if any artists were found in the search results
    if results['artists']['total'] > 0:
        artist_info = results['artists']['items'][0]
        # Get the image URL of the artist
        if artist_info['images']:
            image_url = artist_info['images'][0]['url']
            return image_url
        else:
            return None
    else:
        return None





def confirmation(song_title, artist_name):
    song_id = search_song(song_title, artist_name)
    title, artist = get_song_info_from_spotify(song_id)
    url = 'https://open.spotify.com/track/' + song_id
    st.write(f'Do you mean Title: {title.title()}, Artist: {artist.title()}?')
    st.write(url)
    # Create "Yes" and "No" buttons
    yes_button = st.button("Yes", key="yes")
    no_button = st.button("No", key="no")

    # Get the image

    image_url = get_artist_image_from_song_id(song_id)

        # Display the image on Streamlit
    if image_url == None:
        st.write('Image not available.')
    else:
        st.image(image_url, caption='Album Cover', use_column_width=True, width=100)


    

    if yes_button:
        return 'yes'
    elif no_button:
        return 'no'
    else:
        pass






            
def song_recommender(df, song_title, artist_name):
    
    song_title = song_title.lower()    
    artist_name = artist_name.lower()

    answer = confirmation(song_title, artist_name)

    if answer == 'no':
        st.subheader('Rerun the page!!')
    elif answer == 'yes':
        recommend_song(df, song_title, artist_name)
        st.subheader("If you want other recommendations, push 'Yes' button again!")
    else:
        pass

        
        
df = songs
#ong_recommender(songs)

def main():
    st.title("Song Recommendation App")
    st.write("Enter the details of the song you want to get recommendations for.")

    # Take user inputs for song title and artist name
    song_title = st.text_input("Enter the song title:", key="song_title_input")
    artist_name = st.text_input("Enter the artist name:", key="artist_name_input")

    # Check if the user has provided inputs for both title and artist
    if song_title and artist_name:
        # Call the song_recommender function with the user inputs and the DataFrame
        song_recommender(df, song_title, artist_name)



if __name__ == "__main__":
    main()











