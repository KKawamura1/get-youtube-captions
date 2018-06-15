import webvtt
from typing import List
import datetime
import re
from .caption import Caption
from .video_info import VideoInfo
from .caption_info import CaptionInfo


TIMESTAMP_PATTERN = re.compile('^(\d+)?:?(\d{2}):(\d{2})[.,](\d{3})$')


def _webvtt_string_to_parsed_original_structure(webvtt_string: str) -> List[webvtt.Caption]:
    parser = webvtt.parsers.WebVTTParser()
    lines = webvtt_string.split('\n')
    parser._validate(lines)
    parser._parse(lines)
    return parser.captions


def _timestamp_to_time(timestamp: str) -> datetime.time:
    m = TIMESTAMP_PATTERN.match(timestamp)
    assert m is not None
    hours, minutes, seconds, milisecs = m.groups()
    if hours is None:
        hours = '0'
    assert all([elem is not None for elem in [minutes, seconds, milisecs]])
    return datetime.time(int(hours), int(minutes), int(seconds), int(milisecs) * 1000)


def _original_caption_to_my_caption(
        original_caption: webvtt.Caption,
        video_info: VideoInfo,
        caption_info: CaptionInfo
) -> Caption:
    return Caption(video_info, caption_info,
                   _timestamp_to_time(original_caption.start),
                   _timestamp_to_time(original_caption.end),
                   original_caption.text)


def webvtt_string_to_parsed(
        webvtt_string: str,
        video_info: VideoInfo,
        caption_info: CaptionInfo
) -> List[Caption]:
    original_captions = _webvtt_string_to_parsed_original_structure(webvtt_string)
    return [_original_caption_to_my_caption(caption, video_info, caption_info)
            for caption in original_captions]
