import logging
from ams.ws.APIs.baseAPIHandler import BaseAPIHandler
logger = logging.getLogger('django.request')

class ContentAPIHandler(BaseAPIHandler):
    name = 'content'

    def __init__(self):
        '''Overwrite BaseAPIHandler message handlers.'''
        self.message_handlers = {
            'get_details': self.handle_get_details,
        }

    def authenticate(self, client, msgid, data, uid, msgtype):
        return True

    def handle_get_details(self, client, msgid, msg, uid):


        data = {'response': 'get_details'}
        return ('content', None, 'details', data, msgid)


