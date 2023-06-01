from io import TextIOWrapper
from typing import Final
import pytube as pt
import openai, dotenv, os


DEFAULT_VIDEO_PATH : Final[str] = "./outputs/videos/"
DELFAUT_TRANSCRIPT_PATH : Final[str] = "./outputs/transcripts/"

def load_whisper() -> None:
    dotenv.load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    return None



def transcript_audio_file(audio_file : TextIOWrapper) -> str:
    transcript = openai.Audio.transcribe(model="whisper-1", file=audio_file)
    text = transcript["text"]

    return text



def get_video_by_url(url : str) -> pt.YouTube:
    video = pt.YouTube(url, use_oauth=True, allow_oauth_cache=True)

    return video

def download_video_to_path(video : pt.YouTube, path : str) -> None:
    video.streams \
        .filter(progressive=True, file_extension='mp4') \
        .order_by('resolution') \
        .desc() \
        .first() \
        .download(path, filename="video.mp3")
    
    return None


def load_video(url : str, path : str) -> pt.YouTube:
    video = get_video_by_url(url)
    download_video_to_path(video, path)

    return video


def ask_for_url() -> str:
    url = input("Enter the url of the video: ")

    return url


def main() -> None:
    load_whisper()

    url = ask_for_url()
    video = load_video(url, DEFAULT_VIDEO_PATH)

    print(f"Video {video.title} downloaded successfully")

    print("Transcripting video...")

    video = open(f'{DEFAULT_VIDEO_PATH}video.mp3', "rb")

    # transcript = transcript_audio_file(video)

    print(video)


if __name__ == "__main__":
    main()