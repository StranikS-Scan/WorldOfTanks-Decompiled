# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/CyberSportMainWindow.py
from UnitBase import UNIT_BROWSER_ERROR
from adisp import process
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui import DialogsInterface, SystemMessages
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.dialogs.rally_dialog_meta import UnitConfirmDialogMeta
from gui.Scaleform.daapi.view.meta.CyberSportMainWindowMeta import CyberSportMainWindowMeta
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.managers.windows_stored_data import DATA_TYPE, TARGET_ID
from gui.Scaleform.managers.windows_stored_data import stored_window
from gui.prb_control import settings, prbPeripheriesHandlerProperty
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.formatters import messages
from gui.prb_control.entities.base.unit.ctx import AutoSearchUnitCtx, JoinUnitCtx, AcceptSearchUnitCtx, DeclineSearchUnitCtx, BattleQueueUnitCtx, CreateUnitCtx
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES, CREATOR_ROSTER_SLOT_INDEXES, PREBATTLE_ACTION_NAME
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from helpers import i18n

@stored_window(DATA_TYPE.UNIQUE_WINDOW, TARGET_ID.CHANNEL_CAROUSEL)
class CyberSportMainWindow(CyberSportMainWindowMeta):

    def __init__(self, _=None):
        super(CyberSportMainWindow, self).__init__()
        self.__currentState = ''
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.UNIT)

    def getIntroViewAlias(self):
        return CYBER_SPORT_ALIASES.INTRO_VIEW_UI

    def getBrowserViewAlias(self, prbType):
        return CYBER_SPORT_ALIASES.UNITS_LIST_VIEW_UI

    def getRoomViewAlias(self, prbType):
        return CYBER_SPORT_ALIASES.UNIT_VIEW_UI

    def getFlashAliases(self):
        return CYBER_SPORT_ALIASES.FLASH_ALIASES

    def getPythonAliases(self):
        return CYBER_SPORT_ALIASES.PYTHON_ALIASES

    def getPrbType(self):
        return PREBATTLE_TYPE.E_SPORT_COMMON

    @prbPeripheriesHandlerProperty
    def prbPeripheriesHandler(self):
        return None

    def onUnitRejoin(self):
        if not self.prbEntity.getFlags().isInIdle():
            self.__clearState()

    def onUnitFlagsChanged(self, flags, timeLeft):
        if self.prbEntity.hasLockedState():
            if flags.isInSearch():
                self.as_enableWndCloseBtnS(False)
                self.__currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_WAITING_PLAYERS_STATE
            elif flags.isInQueue() or flags.isInArena():
                self.as_enableWndCloseBtnS(False)
                self.__currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_ENEMY_STATE
            else:
                LOG_ERROR('View for modal state is not resolved', flags)
            self.__initState(timeLeft=timeLeft)
        else:
            self.__clearState()
        self.__updateChatAvailability()

    def onUnitPlayerStateChanged(self, pInfo):
        if self.prbEntity.getFlags().isInIdle():
            self.__initState()

    def onUnitMembersListChanged(self):
        self.__updateChatAvailability()

    def onUnitPlayersListChanged(self):
        self.__updateChatAvailability()

    def onUnitErrorReceived(self, errorCode):
        self.as_autoSearchEnableBtnS(True)

    def onUnitPlayerOnlineStatusChanged(self, pInfo):
        if pInfo.isOffline():
            key = settings.UNIT_NOTIFICATION_KEY.PLAYER_OFFLINE
        else:
            key = settings.UNIT_NOTIFICATION_KEY.PLAYER_ONLINE
        self.__addPlayerNotification(key, pInfo)

    def onUnitPlayerAdded(self, pInfo):
        if not pInfo.isInvite():
            self.__addPlayerNotification(settings.UNIT_NOTIFICATION_KEY.PLAYER_ADDED, pInfo)

    def onUnitPlayerRemoved(self, pInfo):
        if not pInfo.isInvite():
            self.__addPlayerNotification(settings.UNIT_NOTIFICATION_KEY.PLAYER_REMOVED, pInfo)

    def onUnitPlayerBecomeCreator(self, pInfo):
        if pInfo.isCurrentPlayer():
            self._showLeadershipNotification()
        chat = self.chat
        if chat:
            chat.as_addMessageS(messages.getUnitPlayerNotification(settings.UNIT_NOTIFICATION_KEY.GIVE_LEADERSHIP, pInfo))

    def onUnitAutoSearchStarted(self, timeLeft):
        self.__currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_COMMANDS_STATE
        self.as_enableWndCloseBtnS(False)
        self.__initState(timeLeft=timeLeft)

    def onUnitAutoSearchFinished(self):
        self.__clearState()

    def onUnitAutoSearchSuccess(self, acceptDelta):
        self.__currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_CONFIRMATION_STATE
        self.__initState(acceptDelta=acceptDelta)
        from BigWorld import WGWindowsNotifier
        WGWindowsNotifier.onInvitation()

    def onUnitBrowserErrorReceived(self, errorCode):
        if errorCode == UNIT_BROWSER_ERROR.ACCEPT_TIMEOUT:
            self.__currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_ERROR_STATE
            self.__initState()
        else:
            self.as_autoSearchEnableBtnS(True)

    def onWindowMinimize(self):
        self.destroy()
        g_eventDispatcher.showUnitProgressInCarousel(self.getPrbType())

    def onAutoMatch(self, value, vehTypes):
        if value == CYBER_SPORT_ALIASES.INTRO_VIEW_UI:
            self.prbEntity.request(AutoSearchUnitCtx(vehTypes=vehTypes))

    def onBrowseRallies(self):
        self._doSelect(PREBATTLE_ACTION_NAME.PUBLICS_LIST)

    def onCreateRally(self):
        self.__requestToCreate()

    def onJoinRally(self, rallyId, slotIndex, peripheryID):
        ctx = JoinUnitCtx(rallyId, self.prbEntity.getEntityType(), slotIndex, waitingID='prebattle/join')
        if g_lobbyContext.isAnotherPeriphery(peripheryID):
            if g_lobbyContext.isPeripheryAvailable(peripheryID):
                self.__requestToReloginAndJoin(peripheryID, ctx)
            else:
                SystemMessages.pushI18nMessage('#system_messages:periphery/errors/isNotAvailable', type=SystemMessages.SM_TYPE.Error)
        else:
            self.__requestToJoin(ctx)

    def autoSearchApply(self, value):
        if value == CYBER_SPORT_ALIASES.AUTO_SEARCH_CONFIRMATION_STATE:
            self.prbEntity.request(AcceptSearchUnitCtx())
        elif value == CYBER_SPORT_ALIASES.AUTO_SEARCH_ERROR_STATE:
            self.__currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_COMMANDS_STATE
            self.prbEntity.request(AutoSearchUnitCtx())

    def autoSearchCancel(self, value):
        self.__currentState = value
        if value == CYBER_SPORT_ALIASES.AUTO_SEARCH_COMMANDS_STATE or value == CYBER_SPORT_ALIASES.AUTO_SEARCH_ERROR_STATE or value == CYBER_SPORT_ALIASES.AUTO_SEARCH_WAITING_PLAYERS_STATE:
            self.prbEntity.request(AutoSearchUnitCtx(action=0))
        elif value == CYBER_SPORT_ALIASES.AUTO_SEARCH_CONFIRMATION_STATE:
            self.prbEntity.request(DeclineSearchUnitCtx())
        elif value == CYBER_SPORT_ALIASES.AUTO_SEARCH_ENEMY_STATE:
            self.prbEntity.request(BattleQueueUnitCtx(action=0))

    def _populate(self):
        super(CyberSportMainWindow, self)._populate()
        self.addListener(events.HideWindowEvent.HIDE_UNIT_WINDOW, self.__handleUnitWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        self.prbEntity.initEvents(self)
        g_eventDispatcher.hideUnitProgressInCarousel(self.getPrbType())

    def _dispose(self):
        self._itemIdMap = None
        super(CyberSportMainWindow, self)._dispose()
        self.removeListener(events.HideWindowEvent.HIDE_UNIT_WINDOW, self.__handleUnitWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        return

    @process
    def __requestToCreate(self):
        yield self.prbDispatcher.create(CreateUnitCtx(PREBATTLE_TYPE.UNIT, waitingID='prebattle/create'))

    @process
    def __requestToJoin(self, ctx):
        yield self.prbDispatcher.join(ctx)

    @process
    def __requestToReloginAndJoin(self, peripheryID, ctx):
        result = yield DialogsInterface.showDialog(UnitConfirmDialogMeta(PREBATTLE_TYPE.UNIT, 'changePeriphery', messageCtx={'host': g_lobbyContext.getPeripheryName(peripheryID)}))
        if result:
            self.prbPeripheriesHandler.join(peripheryID, ctx)

    def __handleUnitWindowHide(self, _):
        self.destroy()

    def __initState(self, timeLeft=0, acceptDelta=0):
        model = None
        if self.__currentState == CYBER_SPORT_ALIASES.AUTO_SEARCH_COMMANDS_STATE:
            message = i18n.makeString(CYBERSPORT.WINDOW_AUTOSEARCH_SEARCHCOMMAND_CXTDNMMESSAGE, settings.AUTO_SEARCH_UNITS_ARG_TIME)
            model = self.__createAutoUpdateModel(self.__currentState, timeLeft, message, [])
        elif self.__currentState == CYBER_SPORT_ALIASES.AUTO_SEARCH_CONFIRMATION_STATE:
            model = self.__createAutoUpdateModel(self.__currentState, acceptDelta, '', [])
        elif self.__currentState == CYBER_SPORT_ALIASES.AUTO_SEARCH_WAITING_PLAYERS_STATE:
            model = self.__createAutoUpdateModel(self.__currentState, timeLeft, '', self.prbEntity.getReadyStates())
            idx, unit = self.prbEntity.getUnit()
            if unit and unit.isRosterSet(ignored=CREATOR_ROSTER_SLOT_INDEXES):
                model['extraData'] = {'showAlert': True,
                 'alertTooltip': TOOLTIPS.CYBERSPORT_WAITINGPLAYERS_CONFIGALERT,
                 'alertIcon': RES_ICONS.MAPS_ICONS_LIBRARY_GEAR}
            else:
                model['extraData'] = {'showAlert': False,
                 'alertTooltip': '',
                 'alertIcon': ''}
        elif self.__currentState == CYBER_SPORT_ALIASES.AUTO_SEARCH_ENEMY_STATE:
            model = self.__createAutoUpdateModel(self.__currentState, timeLeft, '', [])
        elif self.__currentState == CYBER_SPORT_ALIASES.AUTO_SEARCH_ERROR_STATE:
            model = self.__createAutoUpdateModel(self.__currentState, 0, '', [])
        if model is not None:
            self.as_changeAutoSearchStateS(model)
        return

    def __clearState(self):
        self.__currentState = ''
        self.as_enableWndCloseBtnS(True)
        self.as_hideAutoSearchS()

    def __createAutoUpdateModel(self, state, countDownSeconds, ctxMessage, playersReadiness):
        permissions = self.prbEntity.getPermissions(unitIdx=self.prbEntity.getUnitIdx())
        model = {'state': state,
         'countDownSeconds': countDownSeconds,
         'contextMessage': ctxMessage,
         'playersReadiness': playersReadiness,
         'canInvokeAutoSearch': permissions.canInvokeAutoSearch(),
         'canInvokeBattleQueue': permissions.canStopBattleQueue()}
        return model

    def __addPlayerNotification(self, key, pInfo):
        chat = self.chat
        if chat and not pInfo.isCurrentPlayer():
            chat.as_addMessageS(messages.getUnitPlayerNotification(key, pInfo))

    def __updateChatAvailability(self):
        state = self.prbEntity.getFlags()
        pInfo = self.prbEntity.getPlayerInfo()
        isJoined = pInfo.isInSlot
        if self.chat is not None and self.chat.isJoined() is not isJoined:
            self.chat.as_setJoinedS(isJoined)
        return
