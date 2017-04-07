import requests
import json
from django.conf import settings
import logging

logger = logging.getLogger('django.request')
import concurrent.futures


def send_post_request(server_url, command):
    command_dict = [command]
    response = {'error': False, 'message': 'ack'}

    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(post_data,
                                         server_url, command):
                             command for command in command_dict}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                response = future.result()
                # logger.debug(str(response))
            except Exception as exc:
                logger.debug('%r generated an exception: %s' % (url, exc))
                response = {'error': True, 'message': 'Service possibly offline'}
    return response


def post_data(device_url, command):
    POST_data = json.dumps(command)
    try:
        logger.info('POST to %s' % device_url)
        logger.debug(POST_data)
        post = requests.post(device_url, data=POST_data, timeout=1)
        return json.loads(post.text)
    except requests.exceptions.ConnectionError as e:
        return {'error': True, 'message': 'Service possibly offline'}
    except requests.exceptions.Timeout as e:
        return {'error': True, 'message': 'Service possibly offline'}
    except requests.exceptions.RequestException as e:
        return {'error': True, 'message': 'Service possibly offline'}