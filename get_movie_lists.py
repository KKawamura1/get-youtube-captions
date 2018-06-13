#!/usr/bin/env python3

from apiclient.discovery import Resource
from authentication import build_youtube_service
import json
from typing import List, Mapping, Sequence


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


def main() -> None:
    youtube = build_youtube_service()
    target_channel_id = 'UCLhUvJ_wO9hOvv_yYENu4fQ'
    playlist_id = get_playlist_id_from_channel_id(youtube, target_channel_id)
    print(playlist_id)


if __name__ == '__main__':
    main()
