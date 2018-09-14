# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/chat.py
import calendar
from datetime import datetime
import json
import time
from debug_utils import LOG_CURRENT_EXCEPTION
from messenger.proto.xmpp.extensions import PyExtension, PyHandler, PyQuery
from messenger.proto.xmpp.extensions.ext_constants import XML_NAME_SPACE as _NS
from messenger.proto.xmpp.extensions.ext_constants import XML_TAG_NAME as _TAG
from messenger.proto.xmpp.extensions.shared_queries import MessageQuery
from messenger.proto.xmpp.extensions.wg_items import WgSharedExtension
from messenger.proto.xmpp.gloox_constants import MESSAGE_TYPE, IQ_TYPE, CHAT_STATE, MESSAGE_TYPE_ATTR
from messenger.proto.xmpp.wrappers import ChatMessage

class ChatStateExtension(PyExtension):

    def __init__(self, state = CHAT_STATE.UNDEFINED):
        super(ChatStateExtension, self).__init__(state)
        self.setXmlNs(_NS.CHAT_STATES)

    @classmethod
    def getDefaultData(cls):
        return CHAT_STATE.UNDEFINED

    def getXPath(self, index = None, suffix = '', name = None):
        if self.getName() == CHAT_STATE.UNDEFINED:
            paths = []
            getXPath = super(ChatStateExtension, self).getXPath
            for state in CHAT_STATE.RANGE:
                paths.append(getXPath(index, suffix, state))

            name = paths
        else:
            name = super(ChatStateExtension, self).getXPath(index, suffix, name)
        return name

    def parseTag(self, pyGlooxTag):
        result = pyGlooxTag.filterXPath('|'.join(CHAT_STATE.RANGE))
        if result:
            state = result[0].getTagName()
            if state not in CHAT_STATE.RANGE:
                state = self.getDefaultData()
        else:
            state = self.getDefaultData()
        return state


class DelayExtension(PyExtension):

    def __init__(self):
        super(DelayExtension, self).__init__(_TAG.DELAY)
        self.setXmlNs(_NS.DELAY)

    @classmethod
    def getDefaultData(cls):
        return time.time()

    def parseTag(self, pyGlooxTag):
        stamp = pyGlooxTag.findAttribute('stamp')
        if stamp:
            try:
                tm = time.strptime(stamp, '%Y-%m-%dT%H:%M:%SZ')
                tm = tm[0:8] + (0,)
                sentAt = calendar.timegm(tm)
            except ValueError:
                try:
                    dt = datetime.strptime(stamp, '%Y-%m-%dT%H:%M:%S.%fZ')
                    sentAt = calendar.timegm(dt.timetuple()) + dt.microsecond / 1000000.0
                except ValueError:
                    LOG_CURRENT_EXCEPTION()
                    sentAt = self.getDefaultData()

        else:
            sentAt = self.getDefaultData()
        return sentAt


class MessageIDExtension(PyExtension):

    def __init__(self):
        super(MessageIDExtension, self).__init__(_TAG.WG_MESSAGE_ID)
        self.setXmlNs(_NS.WG_MESSAGE_ID)

    @classmethod
    def getDefaultData(cls):
        return ''

    def parseTag(self, pyGlooxTag):
        return pyGlooxTag.findAttribute('uuid')


class ChatHistoryQuery(PyExtension):

    def __init__(self, jid, limit):
        super(ChatHistoryQuery, self).__init__(_TAG.QUERY)
        self.setXmlNs(_NS.WG_PRIVATE_HISTORY)
        self.setAttribute('with', str(jid))
        self.setAttribute('limit', limit)


class PrivateHistoryItem(PyExtension):

    def __init__(self):
        super(PrivateHistoryItem, self).__init__(_TAG.WG_PRIVATE_HISTORY)
        self.setXmlNs(_NS.WG_PRIVATE_HISTORY)

    @classmethod
    def getDefaultData(cls):
        return ('', False)

    def parseTag(self, pyGlooxTag):
        requestID = pyGlooxTag.findAttribute('request-id')
        isFinal = pyGlooxTag.findAttribute('final')
        if len(isFinal):
            isFinal = json.loads(isFinal)
        else:
            isFinal = False
        return (requestID, isFinal)


class _MessageCustomExtension(PyExtension):

    def __init__(self, msgType, state = CHAT_STATE.UNDEFINED):
        super(_MessageCustomExtension, self).__init__(_TAG.MESSAGE)
        self.setAttribute('type', msgType)
        self.setChild(ChatStateExtension(state))
        self.setChild(WgSharedExtension(False))
        self.setChild(DelayExtension())
        self.setChild(MessageIDExtension())
        self.setChild(PrivateHistoryItem())

    @classmethod
    def getDefaultData(self):
        return ChatMessage()

    def parseTag(self, pyGlooxTag):
        message = ChatMessage()
        message.state = self._getChildData(pyGlooxTag, 0, ChatStateExtension.getDefaultData())
        info = self._getChildData(pyGlooxTag, 1, WgSharedExtension.getDefaultData())
        if info:
            message.accountDBID = info['dbID']
            message.accountName = info['name']
        message.sentAt = self._getChildData(pyGlooxTag, 2, DelayExtension.getDefaultData())
        message.uuid = self._getChildData(pyGlooxTag, 3, MessageIDExtension.getDefaultData())
        message.requestID, message.isFinalInHistory = self._getChildData(pyGlooxTag, 4, PrivateHistoryItem.getDefaultData())
        return message


class ChatMessageHolder(MessageQuery):

    def __init__(self, to, msgBody = '', state = CHAT_STATE.UNDEFINED):
        if state:
            ext = ChatStateExtension(state)
        else:
            ext = None
        super(ChatMessageHolder, self).__init__(MESSAGE_TYPE.CHAT, to, msgBody, ext)
        return


class MessageHandler(PyHandler):
    __slots__ = ('_typeAttr',)

    def __init__(self, typeAttr):
        self._typeAttr = typeAttr
        super(MessageHandler, self).__init__(_MessageCustomExtension(self._typeAttr, CHAT_STATE.UNDEFINED))

    def getFilterString(self):
        return "/{0}[@type='{1}']".format(self._ext.getName(), self._typeAttr)


class ChatMessageHandler(MessageHandler):

    def __init__(self):
        super(ChatMessageHandler, self).__init__(MESSAGE_TYPE_ATTR.CHAT)


class GetChatHistoryQuery(PyQuery):

    def __init__(self, jid, limit):
        super(GetChatHistoryQuery, self).__init__(IQ_TYPE.GET, ChatHistoryQuery(jid, limit))
