# Embedded file name: scripts/client/messenger/proto/bw/errors.py
import BigWorld
from chat_shared import CHAT_RESPONSES
from debug_utils import LOG_ERROR, LOG_WARNING
from helpers import i18n
from helpers.time_utils import makeLocalServerTime
import messenger
from messenger.m_constants import MESSENGER_I18N_FILE
from messenger.proto.bw.cooldown import getOperationInCooldownMsg
from messenger.proto.interfaces import IChatError

class ChannelNotFound(messenger.error):

    def __init__(self, cid, *args, **kwargs):
        super(ChannelNotFound, self).__init__(*args, **kwargs)
        self.cid = cid

    def __str__(self):
        return 'Not found a channel with id = %d, the first request from the server information on the channel with this id' % self.cid


class ChatActionError(IChatError):

    def __init__(self, title, message, isModal = False):
        super(ChatActionError, self).__init__()
        self._title = title
        self._message = message
        self._isModal = isModal

    def getTitle(self):
        return self._title

    def getMessage(self):
        return self._message

    def isModal(self):
        return self._isModal

    @classmethod
    def _makeTitle(cls, name):
        return i18n.makeString('#{0:>s}:server/errors/{1:>s}/title'.format(MESSENGER_I18N_FILE, name))

    @classmethod
    def _makeMessage(cls, name):
        return i18n.makeString('#{0:>s}:server/errors/{1:>s}/message'.format(MESSENGER_I18N_FILE, name))

    @classmethod
    def create(cls, chatAction):
        actionResponse = CHAT_RESPONSES[chatAction['actionResponse']]
        if actionResponse is None:
            LOG_WARNING('__onResponse. action response index %d not found' % chatAction['actionResponse'])
            return
        else:
            name = actionResponse.name()
            title = cls._makeTitle(name)
            message = cls._makeMessage(name)
            auxInfo = chatAction['data'] if chatAction.has_key('data') else None
            if auxInfo is not None and isinstance(auxInfo, dict):
                for key, item in auxInfo.items():
                    if isinstance(item, basestring) and item.startswith('#'):
                        auxInfo[key] = i18n.makeString(item)

                try:
                    fullMessage = message % auxInfo
                except TypeError:
                    LOG_WARNING('__onResponse. An exception occurred during message formatting: %s %% (%s)' % (message[1], auxInfo))
                    fullMessage = message

            else:
                fullMessage = message
            return ChatActionError(title, fullMessage, isModal=False)


class MemberBannedError(ChatActionError):

    @classmethod
    def create(cls, chatAction):
        banInfo = chatAction['data']
        banEndTime = makeLocalServerTime(banInfo.get('banEndTime', None))
        if banEndTime is None:
            if banEndTime in banInfo:
                del banInfo['banEndTime']
            bannedMessage = i18n.makeString('#chat:errors/bannedpermanent', **banInfo)
        else:
            banInfo['banEndTime'] = BigWorld.wg_getLongDateFormat(banEndTime) + ' ' + BigWorld.wg_getShortTimeFormat(banEndTime)
            bannedMessage = i18n.makeString('#chat:errors/banned', **banInfo)
        return MemberBannedError(cls._makeTitle('memberBanned'), bannedMessage, isModal=True)


class ChatBannedError(ChatActionError):

    @classmethod
    def create(cls, chatAction):
        banInfo = chatAction['data']
        banEndTime = makeLocalServerTime(banInfo.get('banEndTime', None))
        if banEndTime is None:
            if banEndTime in banInfo:
                del banInfo['banEndTime']
            bannedMessage = i18n.makeString('#chat:errors/chatbannedpermanent', **banInfo)
        else:
            banInfo['banEndTime'] = BigWorld.wg_getLongDateFormat(banEndTime) + ' ' + BigWorld.wg_getShortTimeFormat(banEndTime)
            bannedMessage = i18n.makeString('#chat:errors/chatbanned', **banInfo)
        return ChatBannedError(cls._makeTitle('chatBanned'), bannedMessage, isModal=True)


class CommandInCooldownError(ChatActionError):

    @classmethod
    def create(cls, chatAction):
        chatActionDict = dict(chatAction)
        data = chatActionDict.get('data', {'command': None,
         'cooldownPeriod': -1})
        result = None
        if data['command'] is not None:
            result = CommandInCooldownError(cls._makeTitle('commandInCooldown'), getOperationInCooldownMsg(data['command'], data['cooldownPeriod']), isModal=False)
        else:
            LOG_ERROR('CommandInCooldown', chatActionDict)
        return result
