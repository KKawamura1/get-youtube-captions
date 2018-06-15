#!/usr/bin/env python3

from pathlib import Path
from logging import getLogger, basicConfig, DEBUG, INFO, WARNING
from authentication import build_youtube_service
from youtube_api import YoutubeAPI
from caption_updater import CaptionUpdater


def main() -> None:
    basicConfig(level=DEBUG)
    logger = getLogger(__name__)
    youtube = build_youtube_service()
    youtube_api = YoutubeAPI(youtube, logger.getChild('YoutubeAPI'))
    caption_updater = CaptionUpdater(youtube_api, logger.getChild('CaptionUpdater'))

    target_channel_id = 'UCLhUvJ_wO9hOvv_yYENu4fQ'
    output_dir = Path('__file__').resolve().parent / 'output'

    caption_updater.do(target_channel_id, output_dir)


if __name__ == '__main__':
    main()
