# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/BasePrebattleRoomView.py
from CurrentVehicle import g_currentVehicle
from adisp import process
from gui.Scaleform.daapi.view.meta.BasePrebattleRoomViewMeta import BasePrebattleRoomViewMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.prb_control.formatters import messages
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.prb_control.entities.base.legacy.ctx import SetPlayerStateCtx
from gui.prb_control.entities.base.legacy.listener import ILegacyListener
from gui.prb_control.items import prb_items
from gui.prb_control.settings import CTRL_ENTITY_TYPE
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from helpers import int2roman
from messenger import g_settings
from messenger.ext import channel_num_gen
from messenger.gui import events_dispatcher
from messenger.gui.Scaleform.view.lobby import MESSENGER_VIEW_ALIAS
from messenger.m_constants import USER_GUI_TYPE
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from prebattle_shared import decodeRoster
from skeletons.gui.lobby_context import ILobbyContext

class BasePrebattleRoomView(BasePrebattleRoomViewMeta, ILegacyListener):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, prbName='prebattle'):
        super(BasePrebattleRoomView, self).__init__()
        self.__prbName = prbName
        self.__clientID = channel_num_gen.getClientID4Prebattle(self.prbEntity.getEntityType())

    def onSourceLoaded(self):
        state = self.prbDispatcher.getFunctionalState()
        if not state.isInLegacy():
            self.destroy()

    @storage_getter('users')
    def usersStorage(self):
        return None

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    @process
    def requestToReady(self, value):
        if value:
            waitingID = 'prebattle/player_ready'
        else:
            waitingID = 'prebattle/player_not_ready'
        result = yield self.prbDispatcher.sendPrbRequest(SetPlayerStateCtx(value, waitingID=waitingID))
        if result:
            self.as_toggleReadyBtnS(not value)

    def requestToLeave(self):
        self._doLeave(False)

    def showPrebattleSendInvitesWindow(self):
        if self.canSendInvite():
            self.fireEvent(events.LoadViewEvent(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY, ctx={'prbName': self.__prbName,
             'ctrlType': CTRL_ENTITY_TYPE.LEGACY}), scope=EVENT_BUS_SCOPE.LOBBY)

    def getClientID(self):
        return self.__clientID

    def requestToKickPlayer(self, value):
        pass

    def canSendInvite(self):
        return self.prbEntity.getPermissions().canSendInvite()

    def isPlayerReady(self):
        return self.prbEntity.getPlayerInfo().isReady()

    def isPlayerCreator(self):
        return self.prbEntity.isCommander()

    def isReadyBtnEnabled(self):
        entity = self.prbEntity
        _, assigned = decodeRoster(entity.getRosterKey())
        return g_currentVehicle.isReadyToPrebattle() and not (entity.getTeamState().isInQueue() and assigned)

    def isLeaveBtnEnabled(self):
        entity = self.prbEntity
        _, assigned = decodeRoster(entity.getRosterKey())
        return not (entity.getTeamState().isInQueue() and entity.getPlayerInfo().isReady() and assigned)

    def startListening(self):
        self.startPrbListening()
        g_currentVehicle.onChanged += self._handleCurrentVehicleChanged
        g_messengerEvents.users.onUserActionReceived += self._onUserActionReceived

    def stopListening(self):
        self.stopPrbListening()
        g_currentVehicle.onChanged -= self._handleCurrentVehicleChanged
        g_messengerEvents.users.onUserActionReceived -= self._onUserActionReceived

    @property
    def chat(self):
        chat = None
        if MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT in self.components:
            chat = self.components[MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT]
        return chat

    def onPlayerAdded(self, entity, playerInfo):
        chat = self.chat
        if chat and not playerInfo.isCurrentPlayer():
            chat.as_addMessageS(messages.getPlayerAddedMessage(self.__prbName, playerInfo))

    def onPlayerRemoved(self, entity, playerInfo):
        chat = self.chat
        if chat and not playerInfo.isCurrentPlayer():
            chat.as_addMessageS(messages.getPlayerRemovedMessage(self.__prbName, playerInfo))

    def onPlayerRosterChanged(self, entity, actorInfo, playerInfo):
        chat = self.chat
        if chat:
            chat.as_addMessageS(messages.getPlayerAssignFlagChanged(actorInfo, playerInfo))

    def onPlayerStateChanged(self, entity, roster, playerInfo):
        team, assigned = decodeRoster(roster)
        data = {'dbID': playerInfo.dbID,
         'state': playerInfo.state,
         'igrType': playerInfo.igrType,
         'icon': '',
         'vShortName': '',
         'vLevel': '',
         'vType': ''}
        if playerInfo.isVehicleSpecified():
            vehicle = playerInfo.getVehicle()
            data.update({'icon': vehicle.iconContour,
             'vShortName': vehicle.shortUserName,
             'vLevel': int2roman(vehicle.level),
             'vType': vehicle.type})
        self.as_setPlayerStateS(team, assigned, data)
        if playerInfo.isCurrentPlayer():
            self.as_toggleReadyBtnS(not playerInfo.isReady())
        else:
            chat = self.chat
            if chat:
                chat.as_addMessageS(messages.getPlayerStateChangedMessage(self.__prbName, playerInfo))

    def _populate(self):
        super(BasePrebattleRoomView, self)._populate()
        self.startListening()
        self.as_enableReadyBtnS(self.isReadyBtnEnabled())

    def _dispose(self):
        self.stopListening()
        self._closeSendInvitesWindow()
        super(BasePrebattleRoomView, self)._dispose()

    def _closeSendInvitesWindow(self):
        container = self.app.containerManager.getContainer(ViewTypes.WINDOW)
        if container is not None:
            window = container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY})
            if window is not None:
                window.destroy()
        return

    def _setRosterList(self, rosters):
        raise NotImplementedError

    def _makeAccountsData(self, accounts):
        result = []
        isPlayerSpeaking = self.bwProto.voipController.isPlayerSpeaking
        getUser = self.usersStorage.getUser
        getColors = g_settings.getColorScheme('rosters').getColors
        accounts = sorted(accounts, cmp=prb_items.getPlayersComparator())
        for account in accounts:
            vContourIcon = ''
            vShortName = ''
            vLevel = ''
            vType = ''
            user = getUser(account.dbID)
            if user is not None:
                key = user.getGuiType()
            else:
                key = USER_GUI_TYPE.OTHER
            if account.isVehicleSpecified():
                vehicle = account.getVehicle()
                vContourIcon = vehicle.iconContour
                vShortName = vehicle.shortUserName
                vLevel = int2roman(vehicle.level)
                vType = vehicle.type
            result.append({'accID': account.accID,
             'dbID': account.dbID,
             'userName': account.name,
             'clanAbbrev': account.clanAbbrev,
             'region': self.lobbyContext.getRegionCode(account.dbID),
             'fullName': account.getFullName(),
             'igrType': account.igrType,
             'time': account.time,
             'isCreator': account.isCreator,
             'state': account.state,
             'icon': vContourIcon,
             'vShortName': vShortName,
             'vLevel': vLevel,
             'vType': vType,
             'tags': list(user.getTags()) if user else [],
             'isPlayerSpeaking': isPlayerSpeaking(account.dbID),
             'colors': getColors(key)})

        return result

    def _handleCurrentVehicleChanged(self):
        self.as_enableReadyBtnS(self.isReadyBtnEnabled())

    def _onUserActionReceived(self, actionID, user):
        self._setRosterList(self.prbEntity.getRosters())

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT:
            events_dispatcher.rqActivateChannel(self.__clientID, viewPy)

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT:
            events_dispatcher.rqDeactivateChannel(self.__clientID)

    @process
    def _doLeave(self, isExit=True):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction(isExit))
