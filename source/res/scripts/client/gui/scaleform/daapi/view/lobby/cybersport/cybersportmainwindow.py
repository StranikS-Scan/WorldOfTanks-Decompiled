# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/CyberSportMainWindow.py
from UnitBase import UNIT_BROWSER_ERROR
from adisp import process
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui import DialogsInterface, SystemMessages
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.dialogs.rally_dialog_meta import UnitConfirmDialogMeta
from gui.Scaleform.daapi.view.lobby.rally import NavigationStack
from gui.Scaleform.daapi.view.lobby.cyberSport.CyberSportIntroView import CyberSportIntroView
from gui.Scaleform.daapi.view.meta.CyberSportMainWindowMeta import CyberSportMainWindowMeta
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.clubs.club_helpers import ClubListener
from gui.clubs import contexts as club_ctx, formatters as club_fmts
from gui.clubs.settings import CLIENT_CLUB_STATE
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.context import unit_ctx
from gui.prb_control.formatters import messages
from gui.prb_control.prb_helpers import prbPeripheriesHandlerProperty
from gui.prb_control import settings
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES, FUNCTIONAL_FLAG, CREATOR_ROSTER_SLOT_INDEXES
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.events import OpenLinkEvent
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from helpers import i18n
from gui.Scaleform.managers.windows_stored_data import DATA_TYPE, TARGET_ID
from gui.Scaleform.managers.windows_stored_data import stored_window
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS

@stored_window(DATA_TYPE.UNIQUE_WINDOW, TARGET_ID.CHANNEL_CAROUSEL)

class CyberSportMainWindow(CyberSportMainWindowMeta, ClubListener):

    def __init__(self, _ = None):
        super(CyberSportMainWindow, self).__init__()
        self.currentState = ''
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.UNIT)

    def getIntroViewAlias(self):
        return CYBER_SPORT_ALIASES.INTRO_VIEW_UI

    def getFlashAliases(self):
        return CYBER_SPORT_ALIASES.FLASH_ALIASES

    def getPythonAliases(self):
        if self.unitFunctional.getEntityType() == PREBATTLE_TYPE.CLUBS:
            return CYBER_SPORT_ALIASES.PYTHON_STATICS_ALIASES
        return CYBER_SPORT_ALIASES.PYTHON_ALIASES

    def getPrbType(self):
        return PREBATTLE_TYPE.UNIT

    def getNavigationKey(self):
        return 'CyberSportMainWindow'

    @prbPeripheriesHandlerProperty
    def prbPeripheriesHandler(self):
        return None

    def onUnitFunctionalInited(self):
        self._requestViewLoad(self.__getUnitViewAlias(self.unitFunctional), self.unitFunctional.getID())

    def onUnitFunctionalFinished(self):
        CyberSportIntroView._selectedVehicles = None
        flags = self.unitFunctional.getFunctionalFlags()
        if flags & settings.FUNCTIONAL_FLAG.UNIT_INTRO > 0:
            if self.unitFunctional.isKicked():
                self._goToNextView(closeForced=True)
        else:
            NavigationStack.clear(self.getNavigationKey())
        return

    def onUnitRejoin(self):
        if not self.unitFunctional.getFlags().isInIdle():
            self.__clearState()

    def onUnitFlagsChanged(self, flags, timeLeft):
        if self.unitFunctional.hasLockedState():
            if flags.isInSearch():
                self.as_enableWndCloseBtnS(False)
                self.currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_WAITING_PLAYERS_STATE
            elif flags.isInQueue() or flags.isInArena():
                self.as_enableWndCloseBtnS(False)
                self.currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_ENEMY_STATE
            else:
                LOG_ERROR('View for modal state is not resolved', flags)
            self.__initState(timeLeft=timeLeft)
        else:
            self.__clearState()
        self.__updateChatAvailability()

    def onUnitPlayerStateChanged(self, pInfo):
        if self.unitFunctional.getFlags().isInIdle():
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

    def onIntroUnitFunctionalFinished(self):
        flags = self.unitFunctional.getFunctionalFlags()
        if flags & settings.FUNCTIONAL_FLAG.UNIT == 0:
            NavigationStack.clear(self.getNavigationKey())

    def onUnitAutoSearchStarted(self, timeLeft):
        self.currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_COMMANDS_STATE
        self.as_enableWndCloseBtnS(False)
        self.__initState(timeLeft=timeLeft)

    def onUnitAutoSearchFinished(self):
        self.__clearState()

    def onUnitAutoSearchSuccess(self, acceptDelta):
        self.currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_CONFIRMATION_STATE
        self.__initState(acceptDelta=acceptDelta)
        from BigWorld import WGWindowsNotifier
        WGWindowsNotifier.onInvitation()

    def onUnitBrowserErrorReceived(self, errorCode):
        if errorCode == UNIT_BROWSER_ERROR.ACCEPT_TIMEOUT:
            self.currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_ERROR_STATE
            self.__initState()
        else:
            self.as_autoSearchEnableBtnS(True)

    def onWindowClose(self):
        self.prbDispatcher.doLeaveAction(unit_ctx.LeaveUnitCtx(waitingID='prebattle/leave', flags=FUNCTIONAL_FLAG.UNDEFINED))

    def onWindowMinimize(self):
        self.destroy()
        g_eventDispatcher.showUnitProgressInCarousel(PREBATTLE_TYPE.UNIT)

    def onAutoMatch(self, value, vehTypes):
        if value == CYBER_SPORT_ALIASES.INTRO_VIEW_UI:
            self.unitFunctional.request(unit_ctx.AutoSearchUnitCtx(vehTypes=vehTypes))

    def onBrowseRallies(self):
        self.unitFunctional.setEntityType(PREBATTLE_TYPE.UNIT)
        self._requestViewLoad(CYBER_SPORT_ALIASES.UNITS_LIST_VIEW_UI, None)
        return

    def onBrowseStaticsRallies(self):
        self.unitFunctional.setEntityType(PREBATTLE_TYPE.CLUBS)
        self._requestViewLoad(CYBER_SPORT_ALIASES.UNITS_LIST_VIEW_UI, None)
        return

    def onCreateRally(self):
        if self.unitFunctional.getEntityType() == PREBATTLE_TYPE.CLUBS:
            self.__requestToCreateClub()
        else:
            self.__requestToCreate()

    def onJoinRally(self, rallyId, slotIndex, peripheryID):
        if self.unitFunctional.getEntityType() == PREBATTLE_TYPE.CLUBS:
            if self.clubsState.getStateID() == CLIENT_CLUB_STATE.SENT_APP:
                if self.clubsState.getClubDbID() == rallyId:
                    self.__requestToCancelClub(rallyId)
            elif self.clubsState.getStateID() == CLIENT_CLUB_STATE.NO_CLUB:
                self.__requestToJoinClub(rallyId)
        else:
            ctx = unit_ctx.JoinUnitCtx(rallyId, self.getPrbType(), slotIndex, waitingID='prebattle/join')
            if g_lobbyContext.isAnotherPeriphery(peripheryID):
                if g_lobbyContext.isPeripheryAvailable(peripheryID):
                    self.__requestToReloginAndJoin(peripheryID, ctx)
                else:
                    SystemMessages.pushI18nMessage('#system_messages:periphery/errors/isNotAvailable', type=SystemMessages.SM_TYPE.Error)
            else:
                self.__requestToJoin(ctx)

    def autoSearchApply(self, value):
        if value == CYBER_SPORT_ALIASES.AUTO_SEARCH_CONFIRMATION_STATE:
            self.unitFunctional.request(unit_ctx.AcceptSearchUnitCtx())
        elif value == CYBER_SPORT_ALIASES.AUTO_SEARCH_ERROR_STATE:
            self.currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_COMMANDS_STATE
            self.unitFunctional.request(unit_ctx.AutoSearchUnitCtx())

    def autoSearchCancel(self, value):
        self.currentState = value
        if value == CYBER_SPORT_ALIASES.AUTO_SEARCH_COMMANDS_STATE or value == CYBER_SPORT_ALIASES.AUTO_SEARCH_ERROR_STATE or value == CYBER_SPORT_ALIASES.AUTO_SEARCH_WAITING_PLAYERS_STATE:
            self.unitFunctional.request(unit_ctx.AutoSearchUnitCtx(action=0))
        elif value == CYBER_SPORT_ALIASES.AUTO_SEARCH_CONFIRMATION_STATE:
            self.unitFunctional.request(unit_ctx.DeclineSearchUnitCtx())
        elif value == CYBER_SPORT_ALIASES.AUTO_SEARCH_ENEMY_STATE:
            self.unitFunctional.request(unit_ctx.BattleQueueUnitCtx(action=0))

    def showHelp(self, helpId):
        title = i18n.makeString(CYBERSPORT.WINDOW_TITLE)
        g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.CLUB_HELP, title=title))

    def _populate(self):
        super(CyberSportMainWindow, self)._populate()
        self.addListener(events.HideWindowEvent.HIDE_UNIT_WINDOW, self.__handleUnitWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        self.startClubListening()
        unitMgrID = self.unitFunctional.getID()
        if unitMgrID > 0:
            self._requestViewLoad(self.__getUnitViewAlias(self.unitFunctional), unitMgrID)
        else:
            self.__initIntroUnitView()
        self.unitFunctional.initEvents(self)
        g_eventDispatcher.hideUnitProgressInCarousel(PREBATTLE_TYPE.UNIT)

    def _dispose(self):
        self._itemIdMap = None
        super(CyberSportMainWindow, self)._dispose()
        self.stopClubListening()
        self.removeListener(events.HideWindowEvent.HIDE_UNIT_WINDOW, self.__handleUnitWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        return

    @process
    def __requestToCreate(self):
        yield self.prbDispatcher.create(unit_ctx.CreateUnitCtx(self.getPrbType(), flags=FUNCTIONAL_FLAG.SWITCH, waitingID='prebattle/create'))

    @process
    def __requestToCreateClub(self):
        result = yield self.clubsCtrl.sendRequest(club_ctx.CreateClubCtx(waitingID='clubs/club/create', confirmID='clubs/app/create'))
        if result.isSuccess():
            SystemMessages.pushMessage(club_fmts.getCreateClubSysMsg())

    @process
    def __requestToJoin(self, ctx):
        yield self.prbDispatcher.join(ctx)

    @process
    def __requestToCancelClub(self, clubDBID):
        result = yield self.clubsCtrl.sendRequest(club_ctx.RevokeApplicationCtx(clubDBID, waitingID='clubs/app/revoke'))
        if result.isSuccess():
            SystemMessages.pushMessage(club_fmts.getAppRevokeSysMsg(self.clubsCtrl.getClub(clubDBID)))

    @process
    def __requestToJoinClub(self, clubDBID):
        result = yield self.clubsCtrl.sendRequest(club_ctx.SendApplicationCtx(clubDBID, '', waitingID='clubs/app/send', confirmID='clubs/app/send'))
        if result.isSuccess():
            SystemMessages.pushMessage(club_fmts.getAppSentSysMsg(self.clubsCtrl.getClub(clubDBID)))

    @process
    def __requestToReloginAndJoin(self, peripheryID, ctx):
        result = yield DialogsInterface.showDialog(UnitConfirmDialogMeta(PREBATTLE_TYPE.UNIT, 'changePeriphery', messageCtx={'host': g_lobbyContext.getPeripheryName(peripheryID)}))
        if result:
            self.prbPeripheriesHandler.join(peripheryID, ctx)

    def __handleUnitWindowHide(self, _):
        self.destroy()

    def __initIntroUnitView(self):
        navKey = self.getNavigationKey()
        NavigationStack.exclude(navKey, CYBER_SPORT_ALIASES.UNIT_VIEW_UI)
        NavigationStack.exclude(navKey, CYBER_SPORT_ALIASES.STATIC_FORMATION_UNIT_VIEW_UI)
        if NavigationStack.hasHistory(navKey):
            flashAlias, _, itemID = NavigationStack.current(navKey)
            self._requestViewLoad(flashAlias, itemID)
        else:
            self._requestViewLoad(CYBER_SPORT_ALIASES.INTRO_VIEW_UI, None)
        return

    def __initState(self, timeLeft = 0, acceptDelta = 0):
        model = None
        if self.currentState == CYBER_SPORT_ALIASES.AUTO_SEARCH_COMMANDS_STATE:
            message = i18n.makeString(CYBERSPORT.WINDOW_AUTOSEARCH_SEARCHCOMMAND_CXTDNMMESSAGE, settings.AUTO_SEARCH_UNITS_ARG_TIME)
            model = self.__createAutoUpdateModel(self.currentState, timeLeft, message, [])
        elif self.currentState == CYBER_SPORT_ALIASES.AUTO_SEARCH_CONFIRMATION_STATE:
            model = self.__createAutoUpdateModel(self.currentState, acceptDelta, '', [])
        elif self.currentState == CYBER_SPORT_ALIASES.AUTO_SEARCH_WAITING_PLAYERS_STATE:
            model = self.__createAutoUpdateModel(self.currentState, timeLeft, '', self.unitFunctional.getReadyStates())
            idx, unit = self.unitFunctional.getUnit()
            if unit and unit.isRosterSet(ignored=CREATOR_ROSTER_SLOT_INDEXES):
                model['extraData'] = {'showAlert': True,
                 'alertTooltip': TOOLTIPS.CYBERSPORT_WAITINGPLAYERS_CONFIGALERT,
                 'alertIcon': RES_ICONS.MAPS_ICONS_LIBRARY_GEAR}
            else:
                model['extraData'] = {'showAlert': False,
                 'alertTooltip': '',
                 'alertIcon': ''}
        elif self.currentState == CYBER_SPORT_ALIASES.AUTO_SEARCH_ENEMY_STATE:
            model = self.__createAutoUpdateModel(self.currentState, timeLeft, '', [])
        elif self.currentState == CYBER_SPORT_ALIASES.AUTO_SEARCH_ERROR_STATE:
            model = self.__createAutoUpdateModel(self.currentState, 0, '', [])
        if model is not None:
            self.as_changeAutoSearchStateS(model)
        return

    def __clearState(self):
        self.currentState = ''
        self.as_enableWndCloseBtnS(True)
        self.as_hideAutoSearchS()

    def __createAutoUpdateModel(self, state, countDownSeconds, ctxMessage, playersReadiness):
        permissions = self.unitFunctional.getPermissions(unitIdx=self.unitFunctional.getUnitIdx())
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

    def __getUnitViewAlias(self, unitFunctional):
        if unitFunctional.getEntityType() == PREBATTLE_TYPE.CLUBS:
            return CYBER_SPORT_ALIASES.STATIC_FORMATION_UNIT_VIEW_UI
        else:
            return CYBER_SPORT_ALIASES.UNIT_VIEW_UI

    def __updateChatAvailability(self):
        state = self.unitFunctional.getFlags()
        pInfo = self.unitFunctional.getPlayerInfo()
        if self.chat is not None:
            self.chat.as_setJoinedS(not state.isInPreArena() or pInfo.isInSlot)
        return
