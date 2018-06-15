from typing import NamedTuple
from datetime import time
from .video_info import VideoInfo
from .caption_info import CaptionInfo


class Caption(NamedTuple):
    video_info: VideoInfo
    caption_info: CaptionInfo
    begin: time
    end: time
    content: str
