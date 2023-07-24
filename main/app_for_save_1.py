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


def get_user_song_cluster(scaled_audio_features_df: pd.DataFrame, filename="../pickle/kmeans_20.pickle"):
    
    try:
        with open(filename, "rb") as file:
            model = pickle.load(file)
    except FileNotFound:
        print("Model not found!!!")
              
    user_song_cluster = model.predict(scaled_audio_features_df)[0]
              
    return user_song_cluster
    
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

    if ( is_hot == "Yes" ): # Recommend another hot song from the the same cluster:
        subset = df[(df['set'] == "H") & (df['K20'] == user_song_cluster)]
        if len(subset) < 5:
            rec_song = df[(df['set'] == "H") & (df['K20'] == user_song_cluster) ].sample(len(subset))
        else:
            rec_song = df[(df['set'] == "H") & (df['K20'] == user_song_cluster) ].sample(5)
    else: # Recommend another not hot song from the same cluster
        subset = df[(df['set'] == "H") & (df['K20'] == user_song_cluster)]
        if len(subset) < 5:
            rec_song = df[(df['set'] == "N") &(df['K20'] == user_song_cluster)].sample(len(subset))
        else:
            rec_song = df[(df['set'] == "N") &(df['K20'] == user_song_cluster)].sample(5)
        
    rec_song['Listen to Your Songs Now'] = 'https://open.spotify.com/track/' + rec_song['id']
    
    st.subheader("We recommend you the following songs")
              
    #with pd.option_context('display.max_colwidth', None):
    #    st.table(rec_song[['Title','Artist','Listen to Your Songs Now']])   

    for i in range(len(rec_song)):
        one_song = rec_song.iloc[i, :]

        # Get the URL
        ID = search_song(one_song['Title'], one_song['Artist'])
        url = 'https://open.spotify.com/track/' + ID

        # Get the image
        image_url = get_track_image_url(ID)

        # Display the image on Streamlit
        if image_url == None:
            st.write('Image not available.')
        else:
            st.image(image_url, caption='Album Cover', use_column_width=True)

        st.subheader(f"Title: {one_song['Title']}, Artist: {one_song['Artist']}, Listen Now: {url}")







def ask_user_for_another_song():

    answer = st.text_input("Do you want another recommendation? (yes/no): ",key="yes_or_no")
    answer = answer.lower()
              
    while answer not in ["yes","no"]:
        st.subheader("Invalid input. Please enter 'yes' or 'no'.")

        
        answer = st.text_input("Do you want another recommendation? (yes/no): ", key="2ask_again")
        answer = answer.lower()
    
    return answer



            
def song_recommender(df, song_title, artist_name):
    
    song_title = song_title    
    artist_name = artist_name

    recommend_song(df, song_title, artist_name)
    #answer = ask_user_for_another_song()
    answer = st.text_input("Do you want another recommendation? (yes/no): ",key="yes_or_no")
    answer = answer.lower()





    #answer = "yes"
   # while answer == "yes":
    #    song_title = st.text_input("Enter the song title:", key="song_title_input_again")
    #    artist_name = st.text_input("Enter the artist name:", key="artist_name_input_again")
     #   recommend_song(df, song_title, artist_name)
     #   answer = ask_user_for_another_song()
        
        
        
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
        rec_songs_df = song_recommender(df, song_title, artist_name)

        # Display the recommendations
        #st.subheader("We recommend you the following songs:")
        #st.table(rec_songs_df[['Title', 'Artist', 'Listen to Your Songs Now']])

if __name__ == "__main__":
    main()