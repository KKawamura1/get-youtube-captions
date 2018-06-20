#!/usr/bin/env python3

from pathlib import Path
from logging import getLogger, basicConfig, DEBUG, INFO, WARNING
from movie_and_captions.authentication import build_youtube_service
from movie_and_captions.youtube_api import YoutubeAPI, DirtyYoutubeAPI
from movie_and_captions.caption_updater import CaptionUpdater
from movie_and_captions.caption_with_mecab import CaptionWithMecab


def main() -> None:
    basicConfig(level=WARNING)
    logger = getLogger(__name__)
    youtube = build_youtube_service()
    youtube_api = YoutubeAPI(youtube, logger.getChild('YoutubeAPI'))
    dirty_youtube_api = DirtyYoutubeAPI(logger.getChild('DirtyYoutubeAPI'))
    caption_updater = CaptionUpdater(youtube_api, dirty_youtube_api,
                                     logger.getChild('CaptionUpdater'))
    caption_with_mecab = CaptionWithMecab(logger.getChild('CaptionWithMecab'))

    target_channel_id = 'UCLhUvJ_wO9hOvv_yYENu4fQ'
    output_dir = Path('__file__').resolve().parent / 'output'

    caption_updater.do(target_channel_id, output_dir)
    caption_with_mecab.do(output_dir)


if __name__ == '__main__':
    main()
