from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional
import pytube as pt

class VideoDownloadStrategy(ABC):
    def download(self, path : str) -> None:
        pass


class SingleVideoDownloadStrategy(VideoDownloadStrategy):
    def __init__(self, *, video : pt.YouTube):
        self.video = video


    def download(self, path : str) -> None:
        self.video.streams \
            .filter(progressive=True, file_extension='mp4') \
            .order_by('resolution') \
            .desc() \
            .first() \
            .download(path, filename="video.mp3")
        
        return None


class MultipleVideoDownloadStrategy(VideoDownloadStrategy):
    def __init__(self, *, videos : list[pt.YouTube]):
        self.videos = videos

    
    def download(self, path : str) -> None:
        for video in self.videos:
            download_strategy = SingleVideoDownloadStrategy(video)
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