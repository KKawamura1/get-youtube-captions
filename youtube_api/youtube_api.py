from apiclient.discovery import Resource
from typing import Mapping, Sequence, List
from logging import Logger, getLogger
import datetime
from .caption_info import CaptionInfo
from .video_info import VideoInfo


class YoutubeAPI:
    def __init__(
            self,
            resource: Resource,
            logger: Logger = getLogger(__name__)
    ) -> None:
        self._resource = resource
        self._logger = logger

    def _get_list_result_with_fields(
            self,
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
            self,
            target_channel_id: str
    ) -> str:
        collection = self._resource.channels()
        filters = dict(id=target_channel_id)
        field_selectors = ['contentDetails', 'relatedPlaylists', 'uploads']

        return self._get_list_result_with_fields(collection, filters, field_selectors)[0]

    def get_video_ids_from_playlist_id(
            self,
            target_playlist_id: str,
            num_max_results: int = None
    ) -> List[str]:
        collection = self._resource.playlistItems()
        filters = dict(playlistId=target_playlist_id)
        if num_max_results is not None:
            filters['maxResults'] = str(num_max_results)
        field_selectors = ['contentDetails', 'videoId']

        return self._get_list_result_with_fields(collection, filters, field_selectors)

    def get_video_info_from_video_id(
            self,
            target_video_id: str
    ) -> VideoInfo:
        collection = self._resource.videos()
        filters = dict(id=target_video_id)
        parts = ['snippet']
        part = ','.join(parts)
        fields = 'items(snippet(title))'
        request = collection.list(part=part, fields=fields, **filters)
        response = request.execute()['items'][0]
        video_info = VideoInfo(target_video_id, response['snippet']['title'])
        return video_info

    def get_caption_infos_from_video_id(
            self,
            target_video_id: str,
    ) -> List[CaptionInfo]:
        # caution: this method takes more amount of `quota` than other APIs!
        collection = self._resource.captions()
        filters = dict(videoId=target_video_id)
        parts = ['id', 'snippet']
        part = ','.join(parts)
        fields = 'items(id,snippet(name,lastUpdated,language,trackKind))'
        request = collection.list(part=part, fields=fields, **filters)
        response = request.execute()
        caption_infos = [
            CaptionInfo(item['id'], item['snippet']['name'],
                        self._iso_8601_string_to_time(item['snippet']['lastUpdated']),
                        item['snippet']['language'], item['snippet']['trackKind'])
            for item in response['items']
        ]
        return caption_infos

    def _iso_8601_string_to_time(
            self,
            string: str
    ) -> datetime.datetime:
        accepts_format = 'YYYY-MM-DDThh:mm:ss'
        time_format = '%Y-%m-%dT%H:%M:%S'

        assert len(string) >= len(accepts_format)
        string = string[:len(accepts_format)]
        return datetime.datetime.strptime(string, time_format)
