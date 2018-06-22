#!/usr/bin/env python3

from pathlib import Path
from logging import getLogger, basicConfig, DEBUG, INFO, WARNING
from typing import List
import argparse
import pickle
import sys

from movie_and_captions.authentication import build_youtube_service
from movie_and_captions.youtube_api import YoutubeAPI, DirtyYoutubeAPI
from movie_and_captions.caption_updater import CaptionUpdater
from movie_and_captions.caption_with_mecab import CaptionWithMecab
from movie_and_captions.data import Data


def main(args: List[str] = None) -> None:
    basicConfig(level=WARNING)
    logger = getLogger(__name__)

    # add params to the parser
    parser = argparse.ArgumentParser()
    parser.add_argument('old_data', nargs='?', type=argparse.FileType('rb'), default=None)
    parser.add_argument('--target_channel_id', default='UCLhUvJ_wO9hOvv_yYENu4fQ')

    # get params from arguments
    if args is None:
        params = parser.parse_args()
    else:
        params = parser.parse_args(args)
    old_data: Data
    if params.old_data is not None:
        old_data_bin = params.old_data.read()
        # note: this is BAD because pickle.load is not secure for outside binary file!
        old_data = pickle.load(old_data_bin)
    else:
        old_data = []
    target_channel_id: str = params.target_channel_id

    # build youtube api service and use it to get captions
    youtube = build_youtube_service()
    youtube_api = YoutubeAPI(youtube, logger.getChild('YoutubeAPI'))
    dirty_youtube_api = DirtyYoutubeAPI(logger.getChild('DirtyYoutubeAPI'))
    caption_updater = CaptionUpdater(youtube_api, dirty_youtube_api,
                                     logger.getChild('CaptionUpdater'))
    caption_with_mecab = CaptionWithMecab(logger.getChild('CaptionWithMecab'))

    # do main
    data = caption_updater.do(target_channel_id, old_data)
    data = caption_with_mecab.do(data)

    # write to stdout
    sys.stdout.buffer.write(pickle.dumps(data))


if __name__ == '__main__':
    main()
