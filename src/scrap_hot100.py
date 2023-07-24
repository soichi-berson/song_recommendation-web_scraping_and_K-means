#Functrion

def scrape_hot100() -> pd.DataFrame:
    '''
    This functions create the DataFrame of artist and titles from Top song 100.
    
    Input: None
    Output: pd.DataFrame
    '''
    import requests 
    from bs4 import BeautifulSoup # to navigate through the html code
    import pandas as pd
    import numpy as np
    import re
    url = "https://www.billboard.com/charts/hot-100"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    #create the list of artists
    artists = [artist.text.strip() for artist in soup.select('span.c-label.a-no-trucate')]
    
    #create the list of titles
    titles = [title.text.strip() for title in soup.select('h3.c-title.a-no-trucate')]
    
    data = {
    'Artist': artists,
    'Title': titles,}

    df = pd.DataFrame(data)
    
    return df