from io import BufferedReader
from typing import Final
import pytube as pt
import openai, dotenv, os
from abc import ABC, abstractmethod
from enum import Enum, auto

import video_downloader as vd

""" 

TODO: Faire un menu complet selon les différents stratégies de téléchargement


"""


DEFAULT_VIDEO_PATH : Final[str] = "./outputs/videos/"
DELFAUT_TRANSCRIPT_PATH : Final[str] = "./outputs/transcripts/"

class SingleItemList(list):
    """Type Hint for a list with a single item"""
    pass

TranscriptText = str





def save_transcript_to_file(transcript : TranscriptText, path : str) -> None:
    with open(path, "w") as file:
        file.write(transcript)
    
    return None


def load_whisper() -> None:
    dotenv.load_dotenv()
    openai.api_key = os.getenv("OPENAI_KEY")

    return None


def get_audio_file_transcript(audio_file : BufferedReader) -> TranscriptText:
    transcript = openai.Audio.transcribe(model="whisper-1", file=audio_file)
    text = transcript["text"]

    return text


def get_youtube_video_by_url(url : str) -> pt.YouTube:
    video = pt.YouTube(url, use_oauth=True, allow_oauth_cache=True)

    return video

def get_youtube_videos_by_urls(urls : list[str] | SingleItemList) -> list[pt.YouTube]:
    videos = []
    for url in urls:
        videos.append(get_youtube_video_by_url(url))

    return videos



def ask_for_url() -> str:
    url = input("Enter the url of the video: ")

    return url


def ask_for_multiple_urls() -> list[str]:
    urls = []
    print("Enter the url of the video (leave blank to stop):")
    url = input("Enter the url of the video: ")

    while len(url) > 0:
        urls.append(url)
        url = input("Enter the url of the video: ")

    return urls



def ask_for_urls_based_on_strategy(strategy : vd.VideoDownloadStrategyTypes) -> list[str] | SingleItemList:
    if strategy == vd.VideoDownloadStrategyTypes.SINGLE_VIDEO:
        return [ask_for_url()]
    
    elif strategy == vd.VideoDownloadStrategyTypes.MULTIPLE_VIDEOS:
        return ask_for_multiple_urls()

def ask_for_download_strategy() -> vd.VideoDownloadStrategyTypes:
    strategies = {
        1: vd.VideoDownloadStrategyTypes.SINGLE_VIDEO,
        2: vd.VideoDownloadStrategyTypes.MULTIPLE_VIDEOS
    }

    choice = 0
    while choice not in strategies:
        print("Choose a download strategy:")
        print("1. Download a single video")
        print("2. Download multiple videos")

        choice = int(input("Enter the option: "))

        if not choice in strategies:
            print("Invalid option\n")

        

    return strategies[choice]


def menu() -> None:
    strategy = ask_for_download_strategy()
    urls = ask_for_urls_based_on_strategy(strategy)

    videos = get_youtube_videos_by_urls(urls)

    print("Downloading videos...")

    vd.DownloadStrategyFactory.create(strategy, videos).download(DEFAULT_VIDEO_PATH)

    print("Download completed")



def main() -> None:

    print("Welcome to the YouTube video downloader\n")

    menu()



if __name__ == "__main__":
    load_whisper()
    main()