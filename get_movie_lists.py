#!/usr/bin/env python3

from authentication import build_youtube_service
import json


def main() -> None:
    youtube = build_youtube_service()
    target_channel_id = 'UCLhUvJ_wO9hOvv_yYENu4fQ'
    get_channel_request = youtube.channels().list(part='snippet', id=target_channel_id)
    channel_data = get_channel_request.execute()
    print(json.dumps(channel_data, indent=4))


if __name__ == '__main__':
    main()
