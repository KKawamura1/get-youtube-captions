import datetime
from logging import getLogger, Logger
from typing import Sequence, Optional, Union
from pathlib import Path
from tqdm import tqdm
import pickle
from youtube_api import YoutubeAPI, DirtyYoutubeAPI, CaptionInfo


class CaptionUpdater:
    def __init__(
            self,
            youtube_api: YoutubeAPI,
            dirty_youtube_api: DirtyYoutubeAPI = None,
            logger: Logger = getLogger(__name__)
    ) -> None:
        self._youtube_api = youtube_api
        self._logger = logger
        self._dirty_youtube_api = dirty_youtube_api

    def _check_caption(
            self,
            caption_info: CaptionInfo,
            last_updated: datetime.datetime
    ) -> bool:
        # last update time check
        if caption_info.last_updated <= last_updated:
            self._logger.debug('Last update for this caption is {} <= memorized last update is {}'
                               .format(caption_info.last_updated, last_updated))
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
            # make a directory for this video
            video_dir = output_dir / video_id
            caption_info_path = video_dir / 'caption_info.pkl'
            video_info_path = video_dir / 'video_info.pkl'
            captions_path = video_dir / 'captions.pkl'

            if caption_info_path.exists():
                with caption_info_path.open('rb') as f:
                    old_caption_info: CaptionInfo = CaptionInfo(**pickle.load(f))
                last_updated = old_caption_info.last_updated
            else:
                last_updated = datetime.datetime.min
            caption_infos = self._youtube_api.get_caption_infos_from_video_id(video_id)
            caption_info = self._get_valid_caption(caption_infos, last_updated)
            if caption_info is not None:
                self._logger.debug('valid caption is found. downloading.')
                video_info = self._youtube_api.get_video_info_from_video_id(video_id)
                assert self._dirty_youtube_api is not None
                captions = self._dirty_youtube_api.download_caption(video_info, caption_info)

                # write into files
                video_dir.mkdir(exist_ok=True)
                with caption_info_path.open('wb') as f:
                    pickle.dump(caption_info._asdict(), f)
                with video_info_path.open('wb') as f:
                    pickle.dump(video_info._asdict(), f)
                with captions_path.open('wb') as f:
                    pickle.dump([caption._asdict() for caption in captions], f)
