# Embedded file name: scripts/client/messenger/gui/Scaleform/channels/bw_chat2/lobby_controllers.py
from gui.prb_control.prb_helpers import PrbListener
from gui.prb_control.settings import PREBATTLE_ROSTER
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import MessengerEvent
from messenger.formatters.users_messages import getBroadcastIsInCoolDownMessage
from messenger.gui.Scaleform.channels._layout import _LobbyLayout
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.bw_chat2.entities import BWMemberEntity
from messenger_common_chat2 import MESSENGER_LIMITS

class UnitChannelController(_LobbyLayout):

    def __init__(self, channel, mBuilder = None):
        super(UnitChannelController, self).__init__(channel, mBuilder)
        self.fireInitEvent()

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def proto(self):
        return None

    def setView(self, view):
        super(UnitChannelController, self).setView(view)
        self.proto.unitChat.addHistory()

    def canSendMessage(self):
        result, errorMsg = True, ''
        if self.proto.unitChat.isBroadcastInCooldown():
            result, errorMsg = False, getBroadcastIsInCoolDownMessage(MESSENGER_LIMITS.BROADCASTS_FROM_CLIENT_COOLDOWN_SEC)
        return (result, errorMsg)

    def _broadcast(self, message):
        self.proto.unitChat.broadcast(message)

    def _format(self, message, doFormatting = True):
        if not doFormatting:
            return message.text
        dbID = message.accountDBID
        return self._mBuilder.setGuiType(dbID).setName(dbID, message.accountName).setTime(message.sentAt).setText(message.text).build()

    def _fireInitEvent(self):
        g_eventBus.handleEvent(MessengerEvent(MessengerEvent.PRB_CHANNEL_CTRL_INITED, {'prbType': self._channel.getPrebattleType(),
         'controller': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _fireDestroyEvent(self):
        g_eventBus.handleEvent(MessengerEvent(MessengerEvent.PRB_CHANNEL_CTRL_DESTROYED, {'prbType': self._channel.getPrebattleType(),
         'controller': self}), scope=EVENT_BUS_SCOPE.LOBBY)


class TrainingChannelController(UnitChannelController, PrbListener):

    def __init__(self, channel, mBuilder = None):
        super(TrainingChannelController, self).__init__(channel, mBuilder)
        self.__isListening = False

    def setView(self, view):
        if not self.__isListening:
            self.__isListening = True
            self.startPrbListening()
            self._buildMembersList()
        super(TrainingChannelController, self).setView(view)

    def onPlayerAdded(self, functional, pInfo):
        self._channel.addMembers([BWMemberEntity(pInfo.dbID, pInfo.name)])
        self._refreshMembersDP()

    def onPlayerRemoved(self, functional, pInfo):
        self._channel.removeMembers([pInfo.dbID])
        self._refreshMembersDP()

    def onPlayerStateChanged(self, functional, roster, pInfo):
        if pInfo.isOffline():
            self._channel.removeMembers([pInfo.dbID])
            self._refreshMembersDP()
        elif not self._channel.hasMember(pInfo.dbID):
            self._channel.addMembers([BWMemberEntity(pInfo.dbID, pInfo.name)])
            self._refreshMembersDP()

    def _removeListeners(self):
        super(UnitChannelController, self)._removeListeners()
        if self.__isListening:
            self.__isListening = False
            self.stopPrbListening()

    def _fireInitEvent(self):
        g_eventBus.handleEvent(MessengerEvent(MessengerEvent.LOBBY_CHANNEL_CTRL_INITED, {'controller': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _fireDestroyEvent(self):
        g_eventBus.handleEvent(MessengerEvent(MessengerEvent.LOBBY_CHANNEL_CTRL_DESTROYED, {'controller': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _buildMembersList(self):
        if not self.prbFunctional:
            return
        rosters = self.prbFunctional.getRosters()

        def __convert(pInfo):
            return BWMemberEntity(pInfo.dbID, pInfo.name)

        members = map(__convert, rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1])
        members.extend(map(__convert, rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2]))
        members.extend(map(__convert, rosters[PREBATTLE_ROSTER.UNASSIGNED]))
        self._channel.addMembers(members)
        self._refreshMembersDP()
