#!/usr/bin/env python3
import api
from questionary import (select, text, Choice, Style, Separator)
from utils import *
from subprocess import (run, CalledProcessError)
from os import (path, W_OK, access)

custom_style_fancy = Style([
    ("textred", "fg:#dd6777"),
    ("textyellow", "fg:#e6ce9d")
])

def play(video, subtitles):
    try:
        if subtitles is None or subtitles=="":
            out = run(["mpv",video], capture_output=True, check=True)
        else:
            out = run(["mpv",f"--sub-file={subtitles}",video], capture_output=True, check=True)
    except FileNotFoundError as e:
        die(e.errno,"Mpv not found. install it or add it to the environment path.")
    except CalledProcessError as e:
        die(e.returncode,"Couldn't run mpv.")

def download(video, subtitles, title):
    download_path=""
    
    while True:
        download_path = (text("Download path (enter=current | 0=cancel)")
                         .unsafe_ask()
                         .strip())

        if download_path=="":
            download_path="./"
        if download_path=="0":
            return

        download_path = path.expanduser(download_path)

        if not path.exists(download_path):
            msg("\nPath doesn't exist\n", "#dd6777")
            continue
        if not access(download_path, W_OK):
            msg(f"\n{download_path} is not accessible\n", "#dd6777")
            continue
        break

    with Progress() as progress:
        if title['kind']=='2':
            episode_info = f"_S{title['season']}E{title['episodeNummer']}"
        else:
            episode_info=""

        video_fn   = f"{title['en_title']}{episode_info}.mp4"
        video_r    = api.get(video,stream=True)
        video_size = int(video_r.headers.get("content-length", 0))
        task1      = progress.add_task("[red]Downloading video...", total=video_size)
        try: 
            video_file = open(download_path+path.sep+video_fn, "wb")
        except PermissionError:
            msg(f"\n{download_path+path.sep+video_fn} is not writable\n", "#dd6777")
        
        if subtitles is not None and subtitles != "":
            subtitles_fn   = f"{title['en_title']}{episode_info}.vtt"
            subtitles_r    = api.get(subtitles, stream=True)
            subtitles_size = int(subtitles_r.headers.get("content-length", 0))
            task2          = progress.add_task("[green]Downloading subtitles...", total=subtitles_size)
            try:
                subtitles_file = open(download_path+path.sep+subtitles_fn, "wb")
            except PermissionError:
                msg(f"\n{download_path+path.sep+subtitles_fn} is not writable\n", "#dd6777")
        for chunk in video_r.iter_content(chunk_size=8192):
            progress.update(task1, advance=8192)
            video_file.write(chunk) 
        if not subtitles is None and not subtitles=="":
            for chunk in subtitles_r.iter_content(chunk_size=8192):
                progress.update(task2, advance=8192)
                subtitles_file.write(chunk)

    clear()
     
def media_page(title):
    clear()
    
    attachments=api.media(title)
   
    options=[]
    options.append(Separator(" "))
    options.append(Choice(title=[("class:textyellow", "*Cancel*")], value="cancel"))
    options.append(Separator(" "))

    subtitles=attachments['t']
    if subtitles == None:
        subtitles = (text("This specific media doesn't have subtitles provide some.\n file/url (optional)")
                   .unsafe_ask()
                   .strip())

    for resolution in attachments['v']:
        options.append(Choice(title=[("class:textred", resolution['resolution'])],
                              value=resolution['videoUrl']))

    resolution = select(
            "Pick resolution",
            choices=options,
            style=custom_style_fancy
    ).unsafe_ask()

    if resolution == "cancel":
        return

    clear()

    options=[]
    options.append(Separator(" "))
    options.append(Choice(title=[("class:textyellow", "*Cancel*")], value="cancel"))
    options.append(Separator(" "))

    options.append(Choice(title=[("class:textred", "Watch")], value="watch"))
    options.append(Choice(title=[("class:textred", "Download")], value="download"))

    action = select(
            f"Pick Action",
            choices=options,
            style=custom_style_fancy
    ).unsafe_ask()
    
    if action == "watch":
        play(resolution, subtitles)
    elif action == "download":
        download(resolution, subtitles, title)
    elif action == "cancel":
        return

    clear()

def show_page(show):
    while True:
        clear()

        seasons = api.season(show)

        options=[]
        options.append(Separator(" "))
        options.append(Choice(title=[("class:textyellow", "*Cancel*")], value="cancel"))
        options.append(Separator(" "))

        for season in seasons.keys():
            options.append(Choice(title=[("class:textred", season)]))

        season = select(
                f"Pick season",
                choices=options,
                style=custom_style_fancy
        ).unsafe_ask()

        if season == "cancel":
            break

        while True:
            episode_number = (text("Episode number (0=cancel)")
                              .unsafe_ask()
                              .strip())

            if episode_number=="0":
                break
            elif episode_number=="":
                msg("\nProvide an episode number\n", "#dd6777")
                continue

            try:
                episode = seasons[season][episode_number]
            except KeyError:
                msg("\nEpisode not found\n", "#dd6777")
                continue

            media_page(episode)

def search_page():
    while True:
        page_number=0
        query = (text("Search title")
                 .unsafe_ask()
                 .strip())

        if query=="":
            msg("\nProvide a title\n", "#dd6777")
            continue

        options=[]

        options.append(Separator(" "))
        options.append(Choice(title=[("class:textyellow", "*Cancel*")], value="cancel"))
        options.append(Separator(" "))

        options.append(Choice(title=[("class:textred", "shows")], value="series"))
        options.append(Choice(title=[("class:textred", "movies")], value="movies"))

        clear()
        genre = select(
                f"Pick genre",
                choices=options,
                style=custom_style_fancy
        ).unsafe_ask()

        if genre == "cancel":
            continue

        while True:
            clear()
            titles = api.look(query, page_number, genre)

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
                en_title = title['en_title']
                year = title['year']
                options.append(Choice(title=[("class:textred", en_title),
                ("class:textyellow", f" {year}")],value=title))

            options.append(Separator(" "))
           
            title = select(
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
                if genre == "movies":
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
