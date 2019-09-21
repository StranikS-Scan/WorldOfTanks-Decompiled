# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/messages/formatters.py
from messenger.formatters.chat_message import LobbyMessageBuilder
from messenger.m_constants import USER_GUI_TYPE
from messenger.proto.xmpp.xmpp_constants import XMPP_MUC_USER_TEMPLATE_GROUPS, XMPP_MUC_USER_TYPE_PRIORITY
from messenger.proto.xmpp.xmpp_constants import XMPP_MUC_USER_GUI_TYPE_OVERRIDE_TRIGGER

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
        affiliationOrder = XMPP_MUC_USER_TYPE_PRIORITY[self.__affiliation]
        roleOrder = XMPP_MUC_USER_TYPE_PRIORITY[self.__role]
        guiType = self.getGuiType()
        if guiType == USER_GUI_TYPE.CURRENT_PLAYER:
            return
        if guiType == USER_GUI_TYPE.OTHER or affiliationOrder >= XMPP_MUC_USER_GUI_TYPE_OVERRIDE_TRIGGER or roleOrder >= XMPP_MUC_USER_GUI_TYPE_OVERRIDE_TRIGGER:
            if affiliationOrder >= roleOrder:
                self.setGroup(XMPP_MUC_USER_TEMPLATE_GROUPS[self.__affiliation])
            else:
                self.setGroup(XMPP_MUC_USER_TEMPLATE_GROUPS[self.__role])


class XmppLobbyUsersChatBuilder(LobbyMessageBuilder):

    def setAffiliation(self, _):
        return self

    def setRole(self, _):
        return self
