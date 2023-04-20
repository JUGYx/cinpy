import sys
import requests
import json
from utils import *

Headers = {"user-agent":"Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0"}

def get(url, stream=False):
    try:
        with requests.session() as s:
            response = s.get(url, headers=Headers, stream=stream)
            if response.ok:
                return response
            else:
                die(-1, f"\nHTTP request returned {response.status_code}.\n")
    except requests.exceptions.ConnectionError:
        die(-1, "\nHTTP request failed, check your network connection.\n")

def look(query, page_number, genre):
    url = f"https://cinemana.shabakaty.com/api/android/AdvancedSearch?level=0&videoTitle={query}&staffTitle={query}&type={genre}&page={page_number}&="
    response = get(url)
    result = json.loads(response.text)
    return result

def season(show):
    url = "https://cinemana.shabakaty.com/api/android/videoSeason/id/"+show['nb']
    response = get(url)
    result = json.loads(response.text)
    seasons={}
    for i in result:
        seasons[i['season']]={}
    for i in result:
        seasons[i['season']][i['episodeNummer']]=i
    return seasons

def media(data):
    subtitles_response = get("https://cinemana.shabakaty.com/api/android/allVideoInfo/id/"+data['nb'])
    videos_response = get("https://cinemana.shabakaty.com/api/android/transcoddedFiles/id/"+data['nb'])
   
    videos_result = json.loads(videos_response.text)
    subtitles_result = json.loads(subtitles_response.text)

    try:
        subtitles = subtitles_result['translations'][0]['file']
    except KeyError:
        subtitles = None

    return {"t":subtitles, "v": videos_result}
        
