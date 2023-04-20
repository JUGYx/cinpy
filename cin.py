#!/usr/bin/env python3
import subprocess
import api
from questionary import (select, text, Choice, Style, Separator)
from utils import *

custom_style_fancy = Style([
    ("textred", "fg:#dd6777"),
    ("textyellow", "fg:#e6ce9d")
])
 
def play(video, subtitles):
    try:
        if subtitles is None or subtitles=="":
            out = subprocess.run(["mpv",video], capture_output=True, check=True)
        else:
            out = subprocess.run(["mpv",f"--sub-file={subtitles}",video], capture_output=True, check=True)
    except FileNotFoundError as e:
        die(e.errno,"Mpv not found. install it or add it to the environment path.")
    except subprocess.CalledProcessError as e:
        die(e.returncode,"Couldn't run mpv.")

def media_page(title):
    clear()
    attachments=api.media(title)
    options=[]

    options.append(Separator(" "))
    options.append(Choice(title=[("class:textyellow", "*Cancel*")], value="cancel"))
    options.append(Separator(" "))

    subtitles=attachments['t']
    if subtitles == None:
        subtitles=text("This specific media doesn't have subtitles provide some.\n file/url (optional)").unsafe_ask()
        subtitles=subtitles.strip()

    for resolution in attachments['v']:
        options.append(Choice(title=[("class:textred", resolution['resolution'])],
                              value=resolution['videoUrl']))

    resolution=select(
            "Pick resolution",
            choices=options,
            style=custom_style_fancy
    ).unsafe_ask()

    if resolution=="cancel":
        return

    play(resolution,subtitles)

def show_page(show):
    while True:
        clear()
        seasons=api.season(show)

        options=[]
        
        options.append(Separator(" "))
        options.append(Choice(title=[("class:textyellow", "*Cancel*")], value="cancel"))
        options.append(Separator(" "))

        for season in seasons.keys():
            options.append(Choice(title=[("class:textred", season)]))

        season=select(
                f"Pick season",
                choices=options,
                style=custom_style_fancy
        ).unsafe_ask()

        if season=="cancel":
            break

        while True:
            episode_number=text("Episode number (0=cancel)").unsafe_ask()
            episode_number=episode_number.strip()

            if episode_number == "0":
                break
            elif episode_number == "":
                msg("\nProvide an episode number\n","#dd6777")
                continue

            try:
                episode=seasons[season][episode_number]
            except KeyError:
                msg("\nEpisode not found\n","#dd6777")
                continue

            media_page(episode)

def search_page():
    while True:
        page_number = 0
        query=text("Search title").unsafe_ask()
        query=query.strip()

        if query=="":
            msg("\nProvide a title\n","#dd6777")
            continue

        options=[]

        options.append(Separator(" "))
        options.append(Choice(title=[("class:textyellow", "*Cancel*")], value="cancel"))
        options.append(Separator(" "))

        options.append(Choice(title=[("class:textred", "shows")], value="series"))
        options.append(Choice(title=[("class:textred", "movies")], value="movies"))

        clear()
        genre=select(
                f"Pick genre",
                choices=options,
                style=custom_style_fancy
        ).unsafe_ask()

        if genre=="cancel":
            continue

        while True:
            clear()
            titles=api.look(query, page_number, genre)

            if len(titles)<1:
                msg("\nNo titles were found\n","#dd6777")
                break

            options=[]
            options.append(Separator(" "))
            options.append(Choice(title=[("class:textyellow", "*Cancel*")], value="cancel"))
            options.append(Choice(title=[("class:textyellow", "*Next page*")], value="next"))
            if page_number>0:
                options.append(Choice(title=[("class:textyellow", "*Previous page*")], value="previous"))
            options.append(Separator(" "))

            for title in titles:
                en_title=title['en_title']
                year=title['year']
                options.append(Choice(title=[("class:textred", en_title),
                ("class:textyellow", f" {year}")],value=title))
            
            options.append(Separator(" "))
           
            title=select(
                f"Select title - Page: {page_number+1}",
                choices=options,
                style=custom_style_fancy
            ).unsafe_ask()

            if title == "cancel":
                break
            elif title == "next":
                page_number+=1
            elif title == "previous" and page_number>0:
                page_number-=1
            else:
                if genre=="movies":
                    media_page(title)
                else:
                    show_page(title)

def main():
    welcome()
    search_page()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        die()
