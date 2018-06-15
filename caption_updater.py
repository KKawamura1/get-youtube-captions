import datetime
from logging import getLogger, Logger
from typing import Sequence, Optional, Union
from pathlib import Path
from tqdm import tqdm
from youtube_api import YoutubeAPI, CaptionInfo


class CaptionUpdater:
    def __init__(
            self,
            youtube_api: YoutubeAPI,
            logger: Logger = getLogger(__name__)
    ) -> None:
        self._youtube_api = youtube_api
        self._logger = logger

    def _iso_8601_string_to_time(
            self,
            string: str
    ) -> datetime.datetime:
        accepts_format = 'YYYY-MM-DDThh:mm:ss'
        time_format = '%Y-%m-%dT%H:%M:%S'

        assert len(string) >= len(accepts_format)
        string = string[:len(accepts_format)]
        return datetime.datetime.strptime(string, time_format)

    def _check_caption(
            self,
            caption_info: CaptionInfo,
            last_updated: datetime.datetime
    ) -> bool:
        # last update time check
        caption_updated_time = self._iso_8601_string_to_time(caption_info.last_updated)
        if caption_updated_time <= last_updated:
            self._logger.debug('Last update for this caption is {} <= memorized last update is {}'
                               .format(caption_updated_time, last_updated))
            return False
        # language check
        if caption_info.language[:2] != 'ja':
            self._logger.debug('caption is written in {}, not {}'
                               .format(caption_info.language, 'ja'))
            return False
        # auto generated check
        if caption_info.track_kind == 'ASR':
            self._logger.debug('caption is automatically generated')
            return False
        self._logger.info('caption {} is matched.'.format(caption_info))
        return True

    def _get_valid_caption(
            self,
            caption_infos: Sequence[CaptionInfo],
            last_updated: datetime.datetime
    ) -> Optional[CaptionInfo]:
        valid_caption_infos = [info for info in caption_infos
                               if self._check_caption(info, last_updated)]
        if len(valid_caption_infos) == 0:
            return None
        else:
            assert len(valid_caption_infos) == 1
            return valid_caption_infos[0]

    def do(
            self,
            target_channel_id: str,
            output_dir: Union[Path, str]
    ) -> None:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        playlist_id = self._youtube_api.get_playlist_id_from_channel_id(target_channel_id)
        video_ids = self._youtube_api.get_video_ids_from_playlist_id(playlist_id)

        for video_id in tqdm(video_ids):
            caption_infos = self._youtube_api.get_caption_infos_from_video_id(video_id)
            caption_info = self._get_valid_caption(caption_infos, datetime.datetime.min)
            if caption_info is not None:
                self._logger.debug('valid caption is found. downloading.')
                caption = self._youtube_api.download_caption(caption_info.caption_id)
                video_info = self._youtube_api.get_video_info_from_video_id(video_id)
                print(caption_info, video_info, caption)
                break
