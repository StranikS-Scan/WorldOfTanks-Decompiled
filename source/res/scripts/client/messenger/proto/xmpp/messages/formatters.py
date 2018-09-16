# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/messages/formatters.py
from messenger.formatters.chat_message import LobbyMessageBuilder
from messenger.proto.xmpp.xmpp_constants import XMPP_MUC_USER_TEMPLATE_GROUPS, XMPP_MUC_USER_TYPE_PRIORITY

class XmppLobbyMessageBuilder(LobbyMessageBuilder):
    __slots__ = ('__affiliation', '__role')

    def __init__(self):
        super(XmppLobbyMessageBuilder, self).__init__()
        self.__affiliation = 'none'
        self.__role = 'none'

    def setAffiliation(self, affiliation):
        if affiliation in XMPP_MUC_USER_TEMPLATE_GROUPS.keys():
            self.__affiliation = affiliation
            self.__updateTemplateKey()
        return self

    def setRole(self, role):
        if role in XMPP_MUC_USER_TEMPLATE_GROUPS.keys():
            self.__role = role
            self.__updateTemplateKey()
        return self

    def __updateTemplateKey(self):
        if XMPP_MUC_USER_TYPE_PRIORITY[self.__affiliation] >= XMPP_MUC_USER_TYPE_PRIORITY[self.__role]:
            self.setGroup(XMPP_MUC_USER_TEMPLATE_GROUPS[self.__affiliation])
        else:
            self.setGroup(XMPP_MUC_USER_TEMPLATE_GROUPS[self.__role])


class XmppLobbyUsersChatBuilder(LobbyMessageBuilder):

    def setAffiliation(self, _):
        return self

    def setRole(self, _):
        return self
