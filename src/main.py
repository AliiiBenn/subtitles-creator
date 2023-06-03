from io import BufferedReader
from typing import Callable, Final
import pytube as pt
import openai, dotenv, os, re
import logging

import video_downloader as vd

""" 

TODO: Faire un menu complet selon les différents stratégies de téléchargement


"""

logging.basicConfig(level=logging.DEBUG, filename="logs.log", filemode="w", format="%(asctime)s - %(levelname)s | %(message)s", encoding="utf-8")


DEFAULT_VIDEO_PATH : Final[str] = "./outputs/videos/"
DELFAUT_TRANSCRIPT_PATH : Final[str] = "./outputs/transcripts/"



TranscriptText = str


def save_transcript_to_file(transcript : str, path : str) -> None: # ! Finished
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path {path} does not exist")
    
    if not os.path.isdir(path):
        raise FileNotFoundError(f"Path {path} must be a file. Your path is a directory")
    
    with open(path, "w") as file:
        file.write(transcript)
    
    return None


def load_whisper() -> None: # ! Finished
    dotenv.load_dotenv()
    openai.api_key = os.getenv("OPENAI_KEY")

    if openai.api_key is None:
        raise EnvironmentError("OPENAI_KEY environment variable is not set, try to check your .env file or your environment variables.")

    return None


def get_audio_file_transcript(audio_file : BufferedReader) -> TranscriptText: # ! Finished
    transcript = openai.Audio.transcribe(model="whisper-1", file=audio_file)

    if not isinstance(transcript, dict):
        raise TypeError("transcript must be a dictionary")

    text = transcript["text"]

    return text


def get_youtube_video_by_url(url : str) -> pt.YouTube: # ! Finished
    logging.info(f"Getting video from url: {url}") # TODO : Remove this line

    video = pt.YouTube(url=url, use_oauth=True, allow_oauth_cache=True)

    return video

def get_youtube_videos_by_urls(urls : list[str]) -> list[pt.YouTube]: # ! Finished
    return [get_youtube_video_by_url(url) for url in urls]



def is_valid_youtube_video_url(url : str) -> bool: 
    regex = r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|live\/|v\/)?)([\w\-]+)(\S+)?$'
    match = re.match(regex, url)

    return match is not None



class SubtitlesCreatorModel:
    def ask_for_single_url(self) -> str:
        finished = False
        url = ""

        while not finished:
            url = input("Enter the url of the video: ")

            finished = is_valid_youtube_video_url(url)

            if not finished:
                print("This url is not a valid youtube video url, please try again")

        logging.info(f"User entered url: {url}") # TODO : Remove this line
        return url
    

    def ask_for_multiple_urls(self) -> list[str]:
        urls = []
        print("You can now enter all urls (leave blank to stop)")
        finished = False

        while not finished:
            url = self.ask_for_single_url()

            if url == "":
                finished = True

            urls.append(url)

        return urls
    

    def get_strategy_dict(self) -> dict[int, vd.VideoDownloadStrategyTypes]:
        strategies = {
            1: vd.VideoDownloadStrategyTypes.SINGLE_VIDEO,
            2: vd.VideoDownloadStrategyTypes.MULTIPLE_VIDEOS
        }

        return strategies
    
    def get_url_input_function(self, strategy : vd.VideoDownloadStrategyTypes) -> Callable[[], str | list[str]]:
        strategy_to_function = {
            vd.VideoDownloadStrategyTypes.SINGLE_VIDEO: self.ask_for_single_url,
            vd.VideoDownloadStrategyTypes.MULTIPLE_VIDEOS: self.ask_for_multiple_urls
        }

        if strategy in strategy_to_function:
            return strategy_to_function[strategy]
        
        raise ValueError(f"Invalid strategy {strategy}")



class SubtitlesCreatorView:
    def __init__(self, model : SubtitlesCreatorModel) -> None:
        self.model = model

    def display_menu(self) -> None:
        print("Welcome to the subtitles creator\n")
        print("Choose an option:")
        print("1. Create subtitles for a single video")
        print("2. Create subtitles for multiple videos")


    def display_strategy_menu(self) -> None:
        print("Choose a download strategy:")
        print("1. Download a single video")
        print("2. Download multiple videos")


class SubtitlesCreatorController:
    def __init__(self, model : SubtitlesCreatorModel, view : SubtitlesCreatorView) -> None:
        self.model = model
        self.view = view


    def get_download_strategy(self) -> vd.VideoDownloadStrategyTypes:
        strategies = self.model.get_strategy_dict()
        choice = 0

        while choice not in strategies:
            self.view.display_strategy_menu()

            choice = int(input("Enter the option: "))

            if not choice in strategies:
                print("Invalid option\n")

        return strategies[choice]    
    
    def get_urls(self, strategy : vd.VideoDownloadStrategyTypes) -> list[str] | str:
        url_function = self.model.get_url_input_function(strategy)

        return url_function()
    

    def download_videos(self, strategy : vd.VideoDownloadStrategyTypes, urls : list[str] | str) -> None:
        logging.info(f"Current url is {urls} and is of type {type(urls)}")

        if strategy == vd.VideoDownloadStrategyTypes.SINGLE_VIDEO:
            if not isinstance(urls, str):
                raise TypeError("urls must be a string")

            url : str = urls
            video = [get_youtube_video_by_url(url)]
            vd.DownloadStrategyFactory.create(strategy, videos=video).download(DEFAULT_VIDEO_PATH)
        else:
            if isinstance(urls, str):
                raise TypeError("urls must be a list of strings")
            
            videos = get_youtube_videos_by_urls(urls)
            vd.DownloadStrategyFactory.create(strategy, videos=videos).download(DEFAULT_VIDEO_PATH)


    def transcripts_all_videos(self, path : str) -> None:
        all_videos = os.listdir(path)
        
        logging.info(f"Videos in path {path} are {all_videos}")

        for video in all_videos:
            open(os.path.join(path, video), "rb")
            transcript = get_audio_file_transcript(open(os.path.join(path, video), "rb"))

            save_transcript_to_file(transcript, os.path.join(DELFAUT_TRANSCRIPT_PATH, video[:-4] + ".txt"))
            
            




def main() -> None:
    model = SubtitlesCreatorModel()
    view = SubtitlesCreatorView(model)
    controller = SubtitlesCreatorController(model, view)

    strategy = controller.get_download_strategy()
    urls = controller.get_urls(strategy)

    controller.download_videos(strategy, urls)

    controller.transcripts_all_videos(DEFAULT_VIDEO_PATH)



if __name__ == "__main__":
    load_whisper()
    main()