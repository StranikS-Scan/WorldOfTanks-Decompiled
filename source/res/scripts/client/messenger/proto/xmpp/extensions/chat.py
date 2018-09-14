# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/chat.py
import calendar
import time
from debug_utils import LOG_CURRENT_EXCEPTION
from messenger.proto.xmpp.extensions import PyExtension, PyHandler, PyMessage
from messenger.proto.xmpp.extensions.contact_item import WgContactInfoExtension
from messenger.proto.xmpp.extensions.ext_constants import XML_NAME_SPACE as _NS
from messenger.proto.xmpp.extensions.ext_constants import XML_TAG_NAME as _TAG
from messenger.proto.xmpp.gloox_constants import MESSAGE_TYPE

class MESSAGE_TYPE_ATTR(object):
    CHAT = 'chat'
    GROUPCHAT = 'groupchat'


class CHAT_STATE(object):
    UNDEFINED = ''
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    GONE = 'gone'
    COMPOSING = 'composing'
    PAUSED = 'paused'
    RANGE = (ACTIVE,
     INACTIVE,
     GONE,
     COMPOSING,
     PAUSED)


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
        return 0

    def parseTag(self, pyGlooxTag):
        stamp = pyGlooxTag.findAttribute('stamp')
        if stamp:
            try:
                tm = time.strptime(stamp, '%Y-%m-%dT%H:%M:%SZ')
                tm = tm[0:8] + (0,)
                sentAt = calendar.timegm(tm)
            except ValueError:
                LOG_CURRENT_EXCEPTION()
                sentAt = self.getDefaultData()

        else:
            sentAt = self.getDefaultData()
        return sentAt


class _MessageCustomExtension(PyExtension):

    def __init__(self, msgType, state = CHAT_STATE.UNDEFINED):
        super(_MessageCustomExtension, self).__init__(_TAG.MESSAGE)
        self.setAttribute('type', msgType)
        self.setChild(WgContactInfoExtension(False))
        self.setChild(ChatStateExtension(state))
        self.setChild(DelayExtension())

    def parseTag(self, pyGlooxTag):
        info = self._getChildData(pyGlooxTag, 0, WgContactInfoExtension.getDefaultData())
        state = self._getChildData(pyGlooxTag, 1, ChatStateExtension.getDefaultData())
        sentAt = self._getChildData(pyGlooxTag, 2, time.time())
        return (state, info, sentAt)

    def getDefaultData(self):
        return (CHAT_STATE.UNDEFINED, {}, 0)


class ChatMessageHolder(PyMessage):

    def __init__(self, to, msgBody = '', state = CHAT_STATE.UNDEFINED):
        if state:
            ext = ChatStateExtension(state)
        else:
            ext = None
        super(ChatMessageHolder, self).__init__(MESSAGE_TYPE.CHAT, to, msgBody, ext)
        return


class ChatMessageHandler(PyHandler):

    def __init__(self):
        super(ChatMessageHandler, self).__init__(_MessageCustomExtension(MESSAGE_TYPE_ATTR.CHAT, CHAT_STATE.UNDEFINED))

    def getFilterString(self):
        return "/{0}[@type='{1}']".format(self._ext.getName(), MESSAGE_TYPE_ATTR.CHAT)
