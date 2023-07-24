# Song Recommender

## Introduction
This is one of the projects in Ironhack Bootcamp 2023. Its main purpose is to create an app of Song Recommender by using the technique of web scraping and K-means clustering. In the end, the app is created by Streamlit.  



## Project 
Name: Song Recommender 

The data of recent popular songs which are used to reccomend are collected by Billbord Hot 100 (https://www.billboard.com/charts/hot-100/) and Kaggle (https://www.kaggle.com/). After the data of Billbord Hot 100 were extracted by web scraping, all the data were linked through Spotify library. Next, the data were divided into groups through scaling and K-means.  

To execute app.py in the repository of `main` by the command `streamlit run app.py` on your terminal, your 'credential-id' and 'client secret' given by Spotify are required. 


The demonstration of the app is given in the 'slides' file.


## Material 
-`main`: a python file to execute by Streamlit 

-`note`: files of Jupyter Notebook.

-`data`: the data of songs.

-`pickle`: files of K-means which were used to choose the 'K'.

-`src`: python files which were used as functions on Jupyter Notebook files.

-`slides`: a demonstration (PDF).

