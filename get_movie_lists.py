#!/usr/bin/env python3

from apiclient.discovery import Resource
from authentication import build_youtube_service
import json
from typing import List, Mapping, Sequence, Any


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


def get_caption_infos_from_video_id(
        service: Resource,
        target_video_id: str
) -> List[Any]:
    # caution: this method takes more amount of `quota` than other APIs!
    collection = service.captions()
    filters = dict(videoId=target_video_id)
    parts = ['id', 'snippet']
    part = ','.join(parts)
    fields = 'items(id,snippet(lastUpdated,language,trackKind))'
    request = collection.list(part=part, fields=fields, **filters)
    response = request.execute()
    results = response['items']
    return results


def main() -> None:
    youtube = build_youtube_service()
    target_channel_id = 'UCLhUvJ_wO9hOvv_yYENu4fQ'
    playlist_id = get_playlist_id_from_channel_id(youtube, target_channel_id)
    video_ids = get_video_ids_from_playlist_id(youtube, playlist_id, num_max_results=1)
    print(get_caption_infos_from_video_id(youtube, video_ids[0]))


if __name__ == '__main__':
    main()
