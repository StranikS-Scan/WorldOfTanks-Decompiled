# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/PrebattleWindow.py
from CurrentVehicle import g_currentVehicle
from adisp import process
from debug_utils import LOG_ERROR
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.meta.PrebattleWindowMeta import PrebattleWindowMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.managers.windows_stored_data import DATA_TYPE, TARGET_ID
from gui.Scaleform.managers.windows_stored_data import stored_window
from gui.prb_control.context import prb_ctx
from gui.prb_control.formatters import messages
from gui.prb_control.items import prb_items
from gui.prb_control.prb_helpers import PrbListener
from gui.prb_control.settings import CTRL_ENTITY_TYPE
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.events import FocusEvent
from helpers import int2roman
from messenger import g_settings, MessengerEntry
from messenger.ext import channel_num_gen
from messenger.gui.Scaleform.view import MESSENGER_VIEW_ALIAS
from messenger.m_constants import USER_GUI_TYPE
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from prebattle_shared import decodeRoster

@stored_window(DATA_TYPE.CAROUSEL_WINDOW, TARGET_ID.CHANNEL_CAROUSEL)

class PrebattleWindow(PrebattleWindowMeta, PrbListener):

    def __init__(self, prbName = 'prebattle'):
        super(PrebattleWindow, self).__init__()
        self.__prbName = prbName
        self.__clientID = channel_num_gen.getClientID4Prebattle(self.prbFunctional.getEntityType())

    def onFocusIn(self, alias):
        self.fireEvent(FocusEvent(FocusEvent.COMPONENT_FOCUSED, {'clientID': self.__clientID}))

    def onWindowClose(self):
        self.requestToLeave()

    def onWindowMinimize(self):
        chat = self.chat
        if chat:
            chat.minimize()
        self.destroy()

    def onSourceLoaded(self):
        if self.prbFunctional and not self.prbFunctional.hasEntity():
            self.destroy()

    @storage_getter('users')
    def usersStorage(self):
        return None

    @process
    def requestToReady(self, value):
        if value:
            waitingID = 'prebattle/player_ready'
        else:
            waitingID = 'prebattle/player_not_ready'
        result = yield self.prbDispatcher.sendPrbRequest(prb_ctx.SetPlayerStateCtx(value, waitingID=waitingID))
        if result:
            self.as_toggleReadyBtnS(not value)

    def requestToLeave(self):
        self.prbDispatcher.doLeaveAction(prb_ctx.LeavePrbCtx(waitingID='prebattle/leave'))

    def showPrebattleSendInvitesWindow(self):
        if self.canSendInvite():
            self.fireEvent(events.LoadViewEvent(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY, ctx={'prbName': self.__prbName,
             'ctrlType': CTRL_ENTITY_TYPE.PREBATTLE}), scope=EVENT_BUS_SCOPE.LOBBY)

    def showFAQWindow(self):
        self.fireEvent(events.LoadViewEvent(MESSENGER_VIEW_ALIAS.FAQ_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)

    def getClientID(self):
        return self.__clientID

    def requestToKickPlayer(self, value):
        pass

    def canSendInvite(self):
        return self.prbFunctional.getPermissions().canSendInvite()

    def isPlayerReady(self):
        return self.prbFunctional.getPlayerInfo().isReady()

    def isPlayerCreator(self):
        return self.prbFunctional.isCreator()

    def isReadyBtnEnabled(self):
        functional = self.prbFunctional
        team, assigned = decodeRoster(functional.getRosterKey())
        return g_currentVehicle.isReadyToPrebattle() and not (functional.getTeamState().isInQueue() and assigned)

    def isLeaveBtnEnabled(self):
        functional = self.prbFunctional
        team, assigned = decodeRoster(functional.getRosterKey())
        return not (functional.getTeamState().isInQueue() and functional.getPlayerInfo().isReady() and assigned)

    def startListening(self):
        self.startPrbListening()
        g_currentVehicle.onChanged += self._handleCurrentVehicleChanged
        g_messengerEvents.users.onUserActionReceived += self._onUserActionReceived

    def stopListening(self):
        self.stopPrbListening()
        self.removeListener(events.MessengerEvent.PRB_CHANNEL_CTRL_INITED, self.__handlePrbChannelControllerInited, scope=EVENT_BUS_SCOPE.LOBBY)
        g_currentVehicle.onChanged -= self._handleCurrentVehicleChanged
        g_messengerEvents.users.onUserActionReceived -= self._onUserActionReceived

    @property
    def chat(self):
        chat = None
        if MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT in self.components:
            chat = self.components[MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT]
        return chat

    def onPrbFunctionalFinished(self):
        self._closeSendInvitesWindow()

    def onPlayerAdded(self, functional, playerInfo):
        chat = self.chat
        if chat and not playerInfo.isCurrentPlayer():
            chat.as_addMessageS(messages.getPlayerAddedMessage(self.__prbName, playerInfo))

    def onPlayerRemoved(self, functional, playerInfo):
        chat = self.chat
        if chat and not playerInfo.isCurrentPlayer():
            chat.as_addMessageS(messages.getPlayerRemovedMessage(self.__prbName, playerInfo))

    def onPlayerRosterChanged(self, functional, actorInfo, playerInfo):
        chat = self.chat
        if chat:
            chat.as_addMessageS(messages.getPlayerAssignFlagChanged(actorInfo, playerInfo))

    def onPlayerStateChanged(self, functional, roster, playerInfo):
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
        super(PrebattleWindow, self)._populate()
        self.startListening()
        self.as_enableReadyBtnS(self.isReadyBtnEnabled())

    def _dispose(self):
        super(PrebattleWindow, self)._dispose()
        self.stopListening()

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
        isPlayerSpeaking = self.app.voiceChatManager.isPlayerSpeaking
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
             'region': g_lobbyContext.getRegionCode(account.dbID),
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

    def _onUserActionReceived(self, actionIndex, user):
        self._setRosterList(self.prbFunctional.getRosters())

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT:
            channels = MessengerEntry.g_instance.gui.channelsCtrl
            controller = None
            if channels:
                controller = channels.getController(self.__clientID)
            if controller is not None:
                controller.setView(viewPy)
            else:
                self.addListener(events.MessengerEvent.PRB_CHANNEL_CTRL_INITED, self.__handlePrbChannelControllerInited, scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def __handlePrbChannelControllerInited(self, event):
        ctx = event.ctx
        prbType = ctx.get('prbType', 0)
        if prbType is 0:
            LOG_ERROR('Prebattle type is not defined', ctx)
            return
        else:
            controller = ctx.get('controller')
            if controller is None:
                LOG_ERROR('Channel controller is not defined', ctx)
                return
            if prbType is self.prbFunctional.getEntityType():
                chat = self.chat
                if chat is not None:
                    controller.setView(chat)
            return
