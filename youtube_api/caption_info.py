from typing import NamedTuple


class CaptionInfo(NamedTuple):
    caption_id: str
    name: str
    last_updated: str
    language: str
    track_kind: str
