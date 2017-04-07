import logging

logger = logging.getLogger('django.request')

class BaseAPIHandler:
    '''
    Base class for an API Handler. To be used by the other API's. The handle
    function shown here will remain to be used, but the message_handlers
    variable will be overwritten with a dict specifying the handler to call
    for a certain message type.
    '''
    name = ''
    message_handlers = {}

    def authenticate(self, client, msgid, data, uid, msgtype):
        pass

    def handle(self, msgid, msgtype, data, client, uid=None):
        '''
        Find the right handler and distribute the incoming message to there.
        '''
        try:
            if not self.authenticate(client, msgid, data, uid, msgtype):
                return (self.name, None, 'error',
                        {'msg': 'User not authenticated to use function ' +
                                'in API ' + self.name},
                        msgid)

            func = self.message_handlers[msgtype]
            try:
                return func(client, msgid, data, uid)
            except KeyError as e:
                logger.error('Keyerror inside function:', e.args[0])
                return (self.name, None, 'error',
                        {'msg': 'Missing parameter "' + str(e.args[0]) + '"'},
                        msgid)
            except TypeError as e:
                logger.error('TypeError inside function: ' + str(e))
                return (self.name, None, 'error',
                        {'msg': 'Invalid command syntax'},
                        msgid)
            except AttributeError as e:
                logger.error('AttributeError inside function: ' + str(e))
                return (self.name, None, 'error',
                        {'msg': 'Invalid command syntax'},
                        msgid)
            except Exception as e:
                logger.error('Exception inside function: ' + str(e))
                return (self.name, None, 'error',
                        {'msg': 'Invalid command syntax'},
                        msgid)
        except KeyError:
            logger.error('Unknown command %s' % msgtype)
            return (self.name, None, 'error', {'msg': 'Unknown command'},
                    msgid)
