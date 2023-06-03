from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Final, Optional
import pytube as pt

DEFAULT_VIDEO_NAME : Final[str] = "0" # Used 0 as default name because my personnal use will be to download videos based on index


class VideoDownloadStrategy(ABC):
    """Abstract class for video download strategies"""
    def download(self, path : str) -> None:
        pass


class SingleVideoDownloadStrategy(VideoDownloadStrategy):
    def __init__(self, *, video : pt.YouTube, name : Optional[str] = None):
        self.video = video
        self.name = name if name is not None else DEFAULT_VIDEO_NAME 
        self.extension = "mp3"


    def download(self, path : str) -> None:
        self.video.streams \
            .filter(progressive=True, file_extension='mp4') \
            .order_by('resolution') \
            .desc() \
            .first() \
            .download(path, filename=f"{self.name}.{self.extension}")
        
        return None


class MultipleVideoDownloadStrategy(VideoDownloadStrategy):
    def __init__(self, *, videos : list[pt.YouTube]):
        self.videos = videos

    
    def download(self, path : str) -> None:
        for index, video in enumerate(self.videos):
            download_strategy = SingleVideoDownloadStrategy(video=video, name=str(index))
            download_strategy.download(path)


class VideoDownloadStrategyTypes(Enum):
    SINGLE_VIDEO = auto()
    MULTIPLE_VIDEOS = auto()



class DownloadStrategyFactory:
    @staticmethod
    def create(type : VideoDownloadStrategyTypes, videos : list[pt.YouTube]) -> VideoDownloadStrategy:
        if type == VideoDownloadStrategyTypes.SINGLE_VIDEO:
            if not len(videos) or len(videos) > 1:
                raise ValueError("You need to specifiy a single video parameter.")

            return SingleVideoDownloadStrategy(video=videos[0])
        
        elif type == VideoDownloadStrategyTypes.MULTIPLE_VIDEOS:
            if videos is None:
                raise ValueError("You need to specifiy videos parameter.")

            return MultipleVideoDownloadStrategy(videos=videos)
        else:
            raise ValueError("Invalid download strategy type")