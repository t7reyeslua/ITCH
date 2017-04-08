from channels import Group
from channels.sessions import channel_session
import logging
import json
import pprint
from ams.ws.APIs.contentHandler import ContentAPIHandler

logger = logging.getLogger('django.request')

clients_group = 'itch_clients'

handlers = {'content': ContentAPIHandler()}

logger.info('STARTING WS Listener')

# Connected to websocket.connect
@channel_session
def ws_add(message):
    # Accept the connection
    message.reply_channel.send({"accept": True})

    try:
        headers  = message.content['headers']
        client_ip = None
        for x in headers:
            if x[0].decode('utf-8') == 'x-real-ip':
                client_ip = x[1].decode('utf-8')
        logger.info('Connecting client from IP %s' % client_ip)
        message.channel_session['ip'] = client_ip
    except Exception as e:
        logger.error('Connection with no headers')

    # Add to the all clients group
    Group(clients_group).add(message.reply_channel)
    return

# Connected to websocket.receive
@channel_session
def ws_message(message):
    msgHandler = MessageHandler(message)
    return

# Connected to websocket.disconnect
@channel_session
def ws_disconnect(message):
    Group(clients_group).discard(message.reply_channel)
    return


def broadcastWS(group_name, message, respond_id=None, starter=None):
    '''
    Send a message to a group
    '''
    logger.info(
        '>>>Sending to group %s - message: %s' % (group_name, str(message)))

    ppmessage = pprint.pformat(message)
    logger.debug(
        '>>>Sending<<<\n' +
        '\treceiver_group:\t\t%s\n' % group_name +
        '\tstarter_channel:\t%s\n' % str(starter) +
        '\t=============================================\n'
        '\t%s\n' % str(ppmessage) +
        '\t=============================================')

    Group(group_name).send({'text': json.dumps(message)})
    return

class MessageHandler():

    def __init__(self, channel):
        self.channel = channel
        self.message = self.channel.content['text']
        self.ip = self.channel.channel_session.get('ip', None)
        self.channeltype = self.channel.channel_session.get('channel_type', 'miscellaneous')
        self.handle_message(self.message)
        return

    # UNPACK message ==================================================================
    def handle_message(self, message):
        '''
        Handle an incoming message on the websocket.
        '''
        try:
            message = self.unpack_json(message)
            if message is None:
                # Either malformed JSON or stacked and handled separately
                return

            unpacked = self.unpack_message(message)
            if unpacked is None:
                # Invalid data in message, already handled
                return

            msgid, handler, msgtype, data = unpacked

            self.process_message(handler, msgid, msgtype, data, message)
        except OSError as e:
            if e.errno == 9:
                pass
            else:
                logger.exception("Uncaught and unhandled internal error: " +
                                 str(type(e)) + ': ' + str(e))
        except Exception as e:
            logger.exception("Uncaught and unhandled internal error: " +
                             str(type(e)) + ': ' + str(e))
        return

    def unpack_json(self, message):
        '''
        Try to unpack the message into a Python dict. If it fails, reply with
        an error message to the client.
        '''
        try:
            message = json.loads(message)
            return message
        except Exception as e:
            logger.error(str(e))
            logger.warning('Client %s, channel %d: ' % (
                self.ip, self.channel.reply_channel) +
                           'Malformed JSON packet received')
            self.send('handler_unknown', 'error',
                      {'msg': 'Malformed JSON packet received'},
                      -1)
            return

    def unpack_message(self, message):
        '''
        Try to unpack the message into variables. If it fails, respond to the
        client that there is a missing parameter.
        '''
        try:
            msgid = int(message['msgid'])
            handler = message['handler']
            msgtype = message['command']
            data = message['data']
            return msgid, handler, msgtype, data
        except KeyError as e:
            try:
                handler = message['handler']
            except KeyError:
                handler = 'handler_unknown'

            try:
                respond_id = int(message['msgid'])
            except KeyError:
                respond_id = -1
            except ValueError:
                respond_id = -1

            logger.warning('Client %s, channel %s: ' % (self.ip, self.channel.reply_channel) +
                           'Malformed packet received - Missing parameter')
            self.send(handler, 'error',
                      {'msg': 'Missing parameter "' + e.args[0] + '"'},
                      respond_id)
            return

    def process_message(self, handler, msgid, msgtype, data, message):
        self.assign_user(message)
        logger.info(
            '>>>Receiving from %s - msgid: %d, handler: %s, command: %s' %
            (self.ip, msgid, handler, msgtype))

        ppdata = pprint.pformat(data)
        logger.debug('>>>Receiving<<<\n' +
                     '\tsender:\t\t%s\n' % self.ip +
                     '\tuid:\t\t%s\n' % str(self.uid) +
                     '\tuser:\t\t%s\n' % str(self.username) +
                     '\tchannelid:\t%s\n' % self.channel.reply_channel +
                     '\thandler:\t%s\n\tmessage id:\t%d\n' % (handler, msgid) +
                     '\tmessagetype:\t%s\n' % (msgtype) +
                     '\t=============================================\n'
                     '\t%s\n' % str(ppdata) +
                     '\t=============================================')
        # Determine what to do with this message

        # Execute message handler, if any. Otherwise request is malformed
        try:
            response = handlers[handler].handle(msgid, msgtype, data, self.channel, self.uid)
        except KeyError as e:
            logger.error('Unknown handler %s' % handler)
            self.send(handler, 'error', {'msg': 'Unknown handler "' + e.args[0] + '"'}, msgid)
            return

        if response is not None:
            r_channel, r_receivers, r_msgtype, r_message, r_respondID = response
            if r_receivers is None:
                # Response just goes current client
                self.send(r_channel, r_msgtype, r_message, r_respondID)
            elif r_receivers == 'broadcast':
                self.send_to_group(clients_group, r_channel, r_msgtype, r_message, r_respondID)
            elif len(r_receivers) > 0:
                # Send response to list of clients
                pass
        else:
            self.send_ack(msgid, handler=handler)
        return

    def assign_user(self, message):
        try:
            self.uid = message['user']
        except KeyError:
            # No user in message. Use previously used user
            self.uid = self.channel.channel_session.get('uid', None)
            #TODO assign a uid based on IP

        # Save uid to channel_session for next times
        self.channel.channel_session['uid'] = self.uid
        self.username = '%s (unknown: using fallback uid)' % message.get('user', 'NONE')
        return

    # SEND functions ==================================================================
    def send_ack(self, respond_id, handler=None):
        '''
        Send an acknowledgement message on this channel.
        '''
        if handler is None:
            handler = self.channeltype
        self.send(handler, 'ack', None, respond_id)
        return

    def send(self, handler, msgtype, message, respond_id=None):
        '''
        Send a message on this channel.
        '''
        message = {
            'msgid': respond_id,
            'handler': handler,
            'command': msgtype,
            'data': message
        }

        logger.info(
            '>>>Sending to %s - msgid: %s, handler: %s, command: %s' %
            (self.ip, respond_id, handler, msgtype))

        ppmessage = pprint.pformat(message)
        logger.debug(
            '>>>Sending<<<\n' +
            '\treceiver:\t\t%s\n' % self.ip +
            '\tuid:\t\t%s\n' % str(self.uid) +
            '\tuser:\t\t%s\n' % str(self.username) +
            '\tchannelid:\t%s\n' % self.channel.reply_channel +
            '\thandler:\t%s\n\tmessage id:\t%d\n' % (handler, respond_id) +
            '\tmessagetype:\t%s\n' % (msgtype) +
            '\t=============================================\n'
            '\t%s\n' % str(ppmessage) +
            '\t=============================================')

        self.channel.reply_channel.send({'text': json.dumps(message)})
        return

    def send_to_group(self, group_name, handler, msgtype, message, respond_id=None):
        '''
        Send a message on this channel.
        '''
        message = {
            'msgid': respond_id,
            'handler': handler,
            'command': msgtype,
            'data': message
        }

        logger.info(
            '>>>Sending to group %s - msgid: %s, handler: %s, command: %s' %
            (group_name, respond_id, handler, msgtype))

        ppmessage = pprint.pformat(message)
        logger.debug(
            '>>>Sending<<<\n' +
            '\treceiver_group:\t\t%s\n' % group_name +
            '\tstarter_channel:\t%s\n' % self.channel.reply_channel +
            '\thandler:\t%s\n\tmessage id:\t%d\n' % (handler, respond_id) +
            '\tmessagetype:\t%s\n' % (msgtype) +
            '\t=============================================\n'
            '\t%s\n' % str(ppmessage) +
            '\t=============================================')

        Group(group_name).send({'text': json.dumps(message) })
        return

