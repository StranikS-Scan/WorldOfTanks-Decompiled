# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/company/legacy/entity.py
import BigWorld
from account_helpers import gameplay_ctx
from adisp import process
from constants import PREBATTLE_COMPANY_DIVISION, QUEUE_TYPE
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control import prb_getters, prbDispatcherProperty
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base import vehicleAmmoCheck, cooldown
from gui.prb_control.entities.base.legacy.ctx import LeaveLegacyCtx, SetPlayerStateCtx, SetTeamStateCtx
from gui.prb_control.entities.base.legacy.entity import LegacyEntryPoint, LegacyIntroEntryPoint, LegacyIntroEntity, LegacyEntity
from gui.prb_control.entities.base.legacy.requester import LegacyRosterRequester
from gui.prb_control.entities.company.legacy.limits import CompanyLimits
from gui.prb_control.entities.company.legacy.permissions import CompanyPermissions
from gui.prb_control.entities.company.legacy.requester import CompanyListRequester
from gui.prb_control.items import prb_items, SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.prb_control.settings import PREBATTLE_SETTING_NAME
from gui.prb_control.settings import REQUEST_TYPE, PREBATTLE_ROSTER, PREBATTLE_ACTION_NAME
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ChannelCarouselEvent
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

class CompanyEntryPoint(LegacyEntryPoint):
    """
    Company entry point class
    """

    def __init__(self):
        super(CompanyEntryPoint, self).__init__(FUNCTIONAL_FLAG.COMPANY)

    def create(self, ctx, callback=None):
        if not self.canCreate():
            if callback is not None:
                callback(False)
        elif prb_getters.getClientPrebattle() is None or ctx.isForced():
            ctx.startProcessing(callback=callback)
            BigWorld.player().prb_createCompany(ctx.isOpened(), ctx.getComment(), ctx.getDivision())
            cooldown.setPrbCreationCooldown()
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle', prb_getters.getPrebattleType())
            if callback is not None:
                callback(False)
        return

    def canCreate(self):
        return not cooldown.validatePrbCreationCooldown()


class CompanyIntroEntryPoint(LegacyIntroEntryPoint):
    """
    Companies intro entry point class
    """

    def __init__(self):
        super(CompanyIntroEntryPoint, self).__init__(FUNCTIONAL_FLAG.COMPANY, PREBATTLE_TYPE.COMPANY)


class CompanyIntroEntity(LegacyIntroEntity):
    """
    Companies intro entity class
    """
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        handlers = {REQUEST_TYPE.PREBATTLES_LIST: self.requestList,
         REQUEST_TYPE.GET_ROSTER: self.requestRoster}
        super(CompanyIntroEntity, self).__init__(FUNCTIONAL_FLAG.COMPANY, PREBATTLE_TYPE.COMPANY, CompanyListRequester(), handlers)
        self._rosterReq = LegacyRosterRequester()

    @prbDispatcherProperty
    def prbDispatcher(self):
        """
        Dispatcher getter property
        """
        return None

    def init(self, clientPrb=None, ctx=None):
        result = super(CompanyIntroEntity, self).init(clientPrb=clientPrb, ctx=ctx)
        self._rosterReq.start(self._onRosterReceived)
        g_eventDispatcher.loadCompany()
        result = FUNCTIONAL_FLAG.addIfNot(result, FUNCTIONAL_FLAG.LOAD_WINDOW)
        self.eventsCache.companies.onCompanyStateChanged += self.__onCompanyStateChanged
        return result

    def fini(self, clientPrb=None, ctx=None, woEvents=False):
        result = super(CompanyIntroEntity, self).fini(clientPrb=clientPrb, ctx=ctx, woEvents=woEvents)
        if not woEvents:
            if not self.canSwitch(ctx):
                g_eventDispatcher.removeCompanyFromCarousel()
        else:
            g_eventDispatcher.removeCompanyFromCarousel(closeWindow=False)
        self.eventsCache.companies.onCompanyStateChanged -= self.__onCompanyStateChanged
        return result

    def doSelectAction(self, action):
        if action.actionName == PREBATTLE_ACTION_NAME.COMPANIES_LIST:
            g_eventDispatcher.showCompanyWindow()
            return SelectResult(True)
        return super(CompanyIntroEntity, self).doSelectAction(action)

    def requestList(self, ctx, callback=None):
        """
        Requests companies list
        Args:
            ctx: companies list request context
            callback: operation's callback
        """
        if self._listReq.isInCooldown():
            self._listReq.fireCooldownEvent()
            if callback:
                callback(True)
        else:
            ctx.startProcessing(callback)
            self._listReq.request(ctx)

    def requestRoster(self, ctx, callback=None):
        """
        Requests roster for selected company
        Args:
            ctx: legacy roster request context
            callback: operation's callback
        """
        ctx.startProcessing(callback)
        self._rosterReq.request(ctx)

    def __onCompanyStateChanged(self, state):
        """
        Listener for company state changed event
        Args:
            state: new state
        """
        if not state:
            DialogsInterface.showDialog(rally_dialog_meta.createCompanyExpariedMeta(), self.__companyExpiredCallback)

    def _onRosterReceived(self, prbID, roster):
        """
        Callback for roster request opertaion
        Args:
            prbID: prebattle ID
            roster: roster itterator
        """
        self._invokeListeners('onLegacyRosterReceived', prbID, roster)

    def __companyExpiredCallback(self, result):
        """
        Callback for company expired dialog.
        Args:
            result: confirmation result
        """
        ctx = LeaveLegacyCtx(waitingID='prebattle/leave')
        if not self.prbDispatcher.isRequestInProcess():
            self.leave(ctx)


class CompanyEntity(LegacyEntity):
    """
    Company room entity
    """
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, settings):
        requests = {REQUEST_TYPE.ASSIGN: self.assign,
         REQUEST_TYPE.SET_TEAM_STATE: self.setTeamState,
         REQUEST_TYPE.SET_PLAYER_STATE: self.setPlayerState,
         REQUEST_TYPE.CHANGE_OPENED: self.changeOpened,
         REQUEST_TYPE.CHANGE_COMMENT: self.changeComment,
         REQUEST_TYPE.CHANGE_DIVISION: self.changeDivision,
         REQUEST_TYPE.KICK: self.kickPlayer,
         REQUEST_TYPE.SEND_INVITE: self.sendInvites}
        super(CompanyEntity, self).__init__(FUNCTIONAL_FLAG.COMPANY, settings, permClass=CompanyPermissions, limits=CompanyLimits(self), requestHandlers=requests)
        self.__doTeamReady = False

    def init(self, clientPrb=None, ctx=None):
        result = super(CompanyEntity, self).init(clientPrb=clientPrb, ctx=ctx)
        playerInfo = self.getPlayerInfo()
        if self.getTeamState(team=1).isInQueue() and playerInfo.isReady() and playerInfo.roster == PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1:
            g_eventDispatcher.loadBattleQueue()
        else:
            g_eventDispatcher.loadHangar()
        g_eventDispatcher.loadCompany()
        result = FUNCTIONAL_FLAG.addIfNot(result, FUNCTIONAL_FLAG.LOAD_WINDOW)
        result = FUNCTIONAL_FLAG.addIfNot(result, FUNCTIONAL_FLAG.LOAD_PAGE)
        g_eventBus.addListener(ChannelCarouselEvent.CAROUSEL_INITED, self.__handleCarouselInited, scope=EVENT_BUS_SCOPE.LOBBY)
        self.eventsCache.companies.onCompanyStateChanged += self.__onCompanyStateChanged
        return result

    @prbDispatcherProperty
    def prbDispatcher(self):
        """
        Dispatcher getter property
        """
        return None

    def isGUIProcessed(self):
        return True

    def fini(self, clientPrb=None, ctx=None, woEvents=False):
        result = super(CompanyEntity, self).fini(clientPrb=clientPrb, ctx=ctx, woEvents=woEvents)
        if not woEvents:
            if not self.canSwitch(ctx):
                g_eventDispatcher.removeCompanyFromCarousel()
        else:
            g_eventDispatcher.removeCompanyFromCarousel(closeWindow=False)
        g_eventBus.removeListener(ChannelCarouselEvent.CAROUSEL_INITED, self.__handleCarouselInited, scope=EVENT_BUS_SCOPE.LOBBY)
        self.eventsCache.companies.onCompanyStateChanged -= self.__onCompanyStateChanged
        return result

    def getQueueType(self):
        return QUEUE_TYPE.COMPANIES

    @vehicleAmmoCheck
    def setPlayerState(self, ctx, callback=None):
        super(CompanyEntity, self).setPlayerState(ctx, callback)

    def getPlayersStateStats(self):
        return self._getPlayersStateStats(PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1)

    def getRosters(self, keys=None):
        rosters = prb_getters.getPrebattleRosters()
        if keys is None:
            result = {PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1: [],
             PREBATTLE_ROSTER.UNASSIGNED_IN_TEAM1: []}
        else:
            result = {}
            for key in keys:
                if key in [PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1, PREBATTLE_ROSTER.UNASSIGNED_IN_TEAM1]:
                    result[key] = []

        for key, roster in rosters.iteritems():
            if key in result:
                result[key] = map(lambda accInfo: prb_items.PlayerPrbInfo(accInfo[0], entity=self, roster=key, **accInfo[1]), roster.iteritems())

        return result

    def doAction(self, action=None):
        if self.isCommander():
            if self.getRosterKey() != PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1:
                DialogsInterface.showI18nInfoDialog('teamDoesNotHaveCommander', lambda result: None)
                return True
            stats = self.getPlayersStateStats()
            creatorWeight = 1 if not self.getPlayerInfo().isReady() else 0
            readyCount = stats.playersCount - stats.notReadyCount
            if readyCount < stats.limitMaxCount - creatorWeight:
                DialogsInterface.showDialog(I18nConfirmDialogMeta('teamHaveNotReadyPlayers', messageCtx={'readyCount': readyCount,
                 'playersCount': stats.playersCount}), self.__confirmCallback)
                return True
            self.__setCreatorReady()
        elif self.getPlayerInfo().isReady():
            self.setPlayerState(SetPlayerStateCtx(False, waitingID='prebattle/player_not_ready'))
        else:
            self.setPlayerState(SetPlayerStateCtx(True, waitingID='prebattle/player_ready'))
        return True

    def doSelectAction(self, action):
        if action.actionName == PREBATTLE_ACTION_NAME.COMPANIES_LIST:
            g_eventDispatcher.showCompanyWindow()
            return SelectResult(True)
        return super(CompanyEntity, self).doSelectAction(action)

    def exitFromQueue(self):
        if self.isCommander():
            self.setTeamState(SetTeamStateCtx(1, False, waitingID='prebattle/team_not_ready'))
        else:
            self.setPlayerState(SetPlayerStateCtx(False, waitingID='prebattle/player_not_ready'))
        return True

    def showGUI(self, ctx=None):
        g_eventDispatcher.loadCompany()

    def changeOpened(self, ctx, callback=None):
        """
        Changes the open/close state for company
        Args:
            ctx: change state request context
            callback: operation's callback
        """
        if ctx.getRequestType() != REQUEST_TYPE.CHANGE_OPENED:
            LOG_ERROR('Invalid context for request changeOpened', ctx)
            if callback is not None:
                callback(False)
            return
        elif not ctx.isOpenedChanged(self._settings):
            if callback is not None:
                callback(False)
            return
        elif self._cooldown.validate(REQUEST_TYPE.CHANGE_SETTINGS):
            if callback is not None:
                callback(False)
            return
        else:
            pPermissions = self.getPermissions()
            if not pPermissions.canMakeOpenedClosed():
                LOG_ERROR('Player can not change opened/closed', pPermissions)
                if callback is not None:
                    callback(False)
                return
            ctx.startProcessing(callback)
            BigWorld.player().prb_changeOpenStatus(ctx.isOpened(), ctx.onResponseReceived)
            self._cooldown.process(REQUEST_TYPE.CHANGE_SETTINGS)
            return

    def changeComment(self, ctx, callback=None):
        """
        Changes the comment for company
        Args:
            ctx: change comment request context
            callback: operation's callback
        """
        if ctx.getRequestType() != REQUEST_TYPE.CHANGE_COMMENT:
            LOG_ERROR('Invalid context for request changeComment', ctx)
            if callback is not None:
                callback(False)
            return
        elif not ctx.isCommentChanged(self._settings):
            if callback is not None:
                callback(False)
            return
        elif self._cooldown.validate(REQUEST_TYPE.CHANGE_SETTINGS):
            if callback:
                callback(False)
            return
        else:
            pPermissions = self.getPermissions()
            if not pPermissions.canChangeComment():
                LOG_ERROR('Player can not change comment', pPermissions)
                if callback is not None:
                    callback(False)
                return
            ctx.startProcessing(callback)
            BigWorld.player().prb_changeComment(ctx.getComment(), ctx.onResponseReceived)
            self._cooldown.process(REQUEST_TYPE.CHANGE_SETTINGS)
            return

    def changeDivision(self, ctx, callback=None):
        """
        Changes the division for company
        Args:
            ctx: change division request context
            callback: operation's callback
        """
        if ctx.getRequestType() != REQUEST_TYPE.CHANGE_DIVISION:
            LOG_ERROR('Invalid context for request changeDivision', ctx)
            if callback is not None:
                callback(False)
            return
        elif not ctx.isDivisionChanged(self._settings):
            if callback is not None:
                callback(False)
            return
        elif self._cooldown.validate(REQUEST_TYPE.CHANGE_SETTINGS):
            if callback is not None:
                callback(False)
            return
        elif ctx.getDivision() not in PREBATTLE_COMPANY_DIVISION.RANGE:
            LOG_ERROR('Division is invalid', ctx)
            if callback is not None:
                callback(False)
            return
        elif self.getTeamState().isInQueue():
            LOG_ERROR('Team is ready or locked', ctx)
            if callback is not None:
                callback(False)
            return
        else:
            pPermissions = self.getPermissions()
            if not pPermissions.canChangeDivision():
                LOG_ERROR('Player can not change division', pPermissions)
                if callback is not None:
                    callback(False)
                return
            ctx.startProcessing(callback)
            BigWorld.player().prb_changeDivision(ctx.getDivision(), ctx.onResponseReceived)
            self._cooldown.process(REQUEST_TYPE.CHANGE_SETTINGS)
            return

    def prb_onSettingUpdated(self, settingName):
        super(CompanyEntity, self).prb_onSettingUpdated(settingName)
        if settingName == PREBATTLE_SETTING_NAME.LIMITS:
            g_eventDispatcher.updateUI()

    def prb_onPlayerStateChanged(self, pID, roster):
        super(CompanyEntity, self).prb_onPlayerStateChanged(pID, roster)
        if self.__doTeamReady:
            self.__doTeamReady = False
            self.__setTeamReady()
        g_eventDispatcher.updateUI()

    def prb_onRosterReceived(self):
        super(CompanyEntity, self).prb_onRosterReceived()
        g_eventDispatcher.updateUI()

    def prb_onPlayerRosterChanged(self, pID, prevRoster, roster, actorID):
        super(CompanyEntity, self).prb_onPlayerRosterChanged(pID, prevRoster, roster, actorID)
        g_eventDispatcher.updateUI()

    def prb_onTeamStatesReceived(self):
        super(CompanyEntity, self).prb_onTeamStatesReceived()
        g_eventDispatcher.updateUI()
        playerInfo = self.getPlayerInfo()
        if playerInfo.isReady() or self.isCommander():
            if self.getTeamState(team=1).isInQueue() and playerInfo.roster == PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1:
                g_eventDispatcher.loadBattleQueue()
            else:
                g_eventDispatcher.loadHangar()

    def prb_onPlayerAdded(self, pID, roster):
        super(CompanyEntity, self).prb_onPlayerAdded(pID, roster)
        g_eventDispatcher.updateUI()

    def prb_onPlayerRemoved(self, pID, roster, name):
        super(CompanyEntity, self).prb_onPlayerRemoved(pID, roster, name)
        g_eventDispatcher.updateUI()

    def __confirmCallback(self, result):
        """
        Set creator ready confirm dialog callback
        Args:
            result: confirm result
        """
        if result:
            self.__setCreatorReady()

    def __setCreatorReady(self):
        """
        Set creator ready method
        """
        if self.getPlayerInfo().isReady():
            self.__setTeamReady()
        else:
            self.setPlayerState(SetPlayerStateCtx(True, waitingID='prebattle/player_ready'), callback=self.__onCreatorReady)

    def __setTeamReady(self):
        """
        Set team ready method
        """
        if self.isCommander():
            self.setTeamState(SetTeamStateCtx(1, True, waitingID='prebattle/team_ready', gamePlayMask=gameplay_ctx.getMask()))

    def __onCreatorReady(self, result):
        """
        Callback for creator's ready request
        Args:
            result: result of creator ready opertaion
        """
        self.__doTeamReady = result

    def __onCompanyStateChanged(self, state):
        """
        Listener for company state changed event
        Args:
            state: new state
        """
        if not state:
            DialogsInterface.showDialog(rally_dialog_meta.createCompanyExpariedMeta(), self.__companyExpiredCallback)

    def __handleCarouselInited(self, _):
        """
        Listener for carousel init event
        """
        g_eventDispatcher.addCompanyToCarousel()

    @process
    def __companyExpiredCallback(self, result):
        """
        Callback for company expired dialog.
        Args:
            result: confirmation result
        """
        ctx = LeaveLegacyCtx(waitingID='prebattle/leave', isForced=True, flags=FUNCTIONAL_FLAG.EXIT)
        if not self.prbDispatcher.isRequestInProcess():
            yield self.prbDispatcher.leave(ctx)
