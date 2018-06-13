#!/usr/bin/env python3

from apiclient.discovery import Resource
from authentication import build_youtube_service
from typing import List, Mapping, Sequence, NamedTuple, Optional
from pathlib import Path
import datetime


class VideoInfo(NamedTuple):
    video_id: str
    title: str


class CaptionInfo(NamedTuple):
    caption_id: str
    last_updated: str
    language: str
    track_kind: str


def get_list_result_with_fields(
        collection: Resource,
        filters: Mapping[str, str],
        field_selectors: Sequence[str]
) -> List[str]:
    assert field_selectors
    part = field_selectors[0]
    fields = '/'.join(['items'] + list(field_selectors))
    request = collection.list(part=part, fields=fields, **filters)
    response = request.execute()
    results = []
    for item in response['items']:
        tmp = item
        for field_selector in field_selectors:
            tmp = tmp[field_selector]
        results.append(tmp)
    return results


def get_playlist_id_from_channel_id(
        service: Resource,
        target_channel_id: str
) -> str:
    collection = service.channels()
    filters = dict(id=target_channel_id)
    field_selectors = ['contentDetails', 'relatedPlaylists', 'uploads']

    return get_list_result_with_fields(collection, filters, field_selectors)[0]


def get_video_ids_from_playlist_id(
        service: Resource,
        target_playlist_id: str,
        num_max_results: int = None
) -> List[str]:
    collection = service.playlistItems()
    filters = dict(playlistId=target_playlist_id)
    if num_max_results is not None:
        filters['maxResults'] = str(num_max_results)
    field_selectors = ['contentDetails', 'videoId']

    return get_list_result_with_fields(collection, filters, field_selectors)


def get_video_info_from_video_id(
        service: Resource,
        target_video_id: str
) -> VideoInfo:
    collection = service.videos()
    filters = dict(id=target_video_id)
    parts = ['snippet']
    part = ','.join(parts)
    fields = 'items(snippet(title))'
    request = collection.list(part=part, fields=fields, **filters)
    response = request.execute()['items'][0]
    video_info = VideoInfo(target_video_id, response['snippet']['title'])
    return video_info


def iso_8601_string_to_time(string: str) -> datetime.datetime:
    accepts_format = 'YYYY-MM-DDThh:mm:ss'
    time_format = '%Y-%m-%dT%H:%M:%S'

    assert len(string) >= len(accepts_format)
    string = string[:len(accepts_format)]
    return datetime.datetime.strptime(string, time_format)


def check_caption(
        caption_info: CaptionInfo,
        last_updated: datetime.datetime
) -> bool:
    # last update time check
    caption_updated_time = iso_8601_string_to_time(caption_info.last_updated)
    if caption_updated_time <= last_updated:
        return False
    # language check
    if caption_info.language[:2] != 'ja':
        return False
    # auto generated check
    if caption_info.track_kind == 'ASR':
        return False
    return True


def get_caption_info_from_video_id(
        service: Resource,
        target_video_id: str,
        last_updated: datetime.datetime
) -> Optional[CaptionInfo]:
    # caution: this method takes more amount of `quota` than other APIs!
    collection = service.captions()
    filters = dict(videoId=target_video_id)
    parts = ['id', 'snippet']
    part = ','.join(parts)
    fields = 'items(id,snippet(lastUpdated,language,trackKind))'
    request = collection.list(part=part, fields=fields, **filters)
    response = request.execute()
    caption_infos = [
        CaptionInfo(item['id'], item['snippet']['lastUpdated'],
                    item['snippet']['language'], item['snippet']['trackKind'])
        for item in response['items']
    ]
    # remove unnecessary infos
    results = [info for info in caption_infos if check_caption(info, last_updated)]
    if results:
        assert len(results) == 1
        return results[0]
    return None


def main() -> None:
    youtube = build_youtube_service()
    target_channel_id = 'UCLhUvJ_wO9hOvv_yYENu4fQ'
    playlist_id = get_playlist_id_from_channel_id(youtube, target_channel_id)
    video_ids = get_video_ids_from_playlist_id(youtube, playlist_id)

    output_dir = Path('__file__').resolve().parent / 'output'
    output_dir.mkdir(exist_ok=True)

    caption_infos = dict()
    for video_id in video_ids:
        caption_info = get_caption_info_from_video_id(youtube, video_id, datetime.datetime.min)
        if caption_info is not None:
            video_info = get_video_info_from_video_id(youtube, video_id)
            # TODO: use video info
            caption_infos[video_id] = caption_info
    print(caption_infos)


if __name__ == '__main__':
    main()
