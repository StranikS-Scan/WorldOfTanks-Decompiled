# Embedded file name: scripts/client/messenger/proto/bw/wrappers.py
from collections import namedtuple
import time as _time
import types
from chat_shared import SYS_MESSAGE_IMPORTANCE
_ChannelData = namedtuple('_ChannelData', ['id',
 'channelName',
 'owner',
 'ownerName',
 'isReadOnly',
 'isSystem',
 'isSecured',
 'greeting',
 'flags',
 'notifyFlags'])

class ChannelDataWrapper(_ChannelData):

    def __new__(cls, id = 0, channelName = 'Unknown', owner = -1L, ownerName = '', isReadOnly = False, isSystem = False, isSecured = False, greeting = '', flags = 0, notifyFlags = 0, **kwargs):
        return _ChannelData.__new__(cls, id, unicode(channelName, 'utf-8', errors='ignore'), owner, unicode(ownerName, 'utf-8', errors='ignore'), isReadOnly, isSystem, isSecured, greeting, flags, notifyFlags)


_ChatActionData = namedtuple('_ChatActionData', ' '.join(['action',
 'channel',
 'actionResponse',
 'group',
 'originator',
 'originatorNickName',
 'requestID',
 'time',
 'sentTime',
 'flags']))

class ChatActionWrapper(_ChatActionData):

    def __new__(cls, action = -1, channel = 0, actionResponse = -1, group = 0, originator = -1, originatorNickName = 'Unknown', requestID = -1, data = None, time = _time.time(), sentTime = _time.time(), flags = 0, **kwargs):
        result = _ChatActionData.__new__(cls, action, channel, actionResponse, group, originator, unicode(originatorNickName, 'utf-8', errors='ignore'), requestID, time, sentTime, flags)
        result.data = unicode(data, 'utf-8', errors='ignore') if type(data) in types.StringTypes else data
        return result


_ServiceChannelData = namedtuple('_ServiceChannelData', ' '.join(['messageId',
 'userId',
 'type',
 'importance',
 'active',
 'personal',
 'sentTime',
 'startedAt',
 'finishedAt',
 'createdAt',
 'data']))

class ServiceChannelMessage(_ServiceChannelData):
    """
    Hold sysMessage and personalSysMessage actions data in chat system
    """

    @staticmethod
    def __new__(cls, messageID = -1L, user_id = -1L, type = -1, importance = SYS_MESSAGE_IMPORTANCE.normal.index(), active = True, personal = False, sentTime = _time.time(), started_at = None, finished_at = None, created_at = None, data = None, **kwargs):
        return _ServiceChannelData.__new__(cls, messageID, user_id, type, importance, active, personal, sentTime, started_at, finished_at, created_at, data)

    @property
    def isHighImportance(self):
        return self.importance == SYS_MESSAGE_IMPORTANCE.high.index()

    @classmethod
    def fromChatAction(cls, chatAction, personal = False):
        kwargs = dict(chatAction['data']) if chatAction.has_key('data') else {}
        kwargs['personal'] = personal
        kwargs['sentTime'] = chatAction['sentTime']
        return ServiceChannelMessage.__new__(cls, **kwargs)
