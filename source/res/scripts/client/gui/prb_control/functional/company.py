# Embedded file name: scripts/client/gui/prb_control/functional/company.py
import BigWorld
from PlayerEvents import g_playerEvents
from account_helpers import gameplay_ctx
from constants import PREBATTLE_TYPE, PREBATTLE_CACHE_KEY
from constants import PREBATTLE_COMPANY_DIVISION
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.prb_control import prb_cooldown, prb_getters
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.context import prb_ctx
from gui.prb_control.functional.decorators import vehicleAmmoCheck
from gui.prb_control.functional.interfaces import IPrbListRequester
from gui.prb_control.items import prb_seqs, prb_items, SelectResult
from gui.prb_control.restrictions.limits import CompanyLimits
from gui.prb_control.settings import REQUEST_TYPE, PREBATTLE_ROSTER, PREBATTLE_ACTION_NAME, PREBATTLE_RESTRICTION
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.prb_control.settings import PREBATTLE_SETTING_NAME
from gui.prb_control.functional.default import PrbEntry, PrbFunctional, IntroPrbFunctional, PrbRosterRequester
from gui.prb_control.restrictions.permissions import CompanyPrbPermissions
from gui.prb_control.context.prb_ctx import LeavePrbCtx
from gui.prb_control.prb_helpers import prbDispatcherProperty
from gui.server_events import g_eventsCache
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ChannelCarouselEvent
from prebattle_shared import decodeRoster

class CompanyEntry(PrbEntry):

    def create(self, ctx, callback = None):
        if prb_cooldown.validatePrbCreationCooldown():
            if callback is not None:
                callback(False)
        elif prb_getters.getClientPrebattle() is None or ctx.isForced():
            ctx.startProcessing(callback=callback)
            BigWorld.player().prb_createCompany(ctx.isOpened(), ctx.getComment(), ctx.getDivision())
            prb_cooldown.setPrbCreationCooldown()
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle', prb_getters.getPrebattleType())
            if callback is not None:
                callback(False)
        return


class _CompanyListRequester(IPrbListRequester):

    def __init__(self):
        self.__callback = None
        self.__ctx = None
        self.__cooldown = prb_cooldown.PrbCooldownManager()
        return

    def isInCooldown(self):
        return self.__cooldown.isInProcess(REQUEST_TYPE.PREBATTLES_LIST)

    def getCooldown(self):
        return self.__cooldown.getTime(REQUEST_TYPE.PREBATTLES_LIST)

    def fireCooldownEvent(self):
        self.__cooldown.fireEvent(REQUEST_TYPE.PREBATTLES_LIST, self.__cooldown.getTime(REQUEST_TYPE.PREBATTLES_LIST))

    def start(self, callback):
        if callback is not None and callable(callback):
            self.__callback = callback
        else:
            LOG_ERROR('Callback is None or is not callable')
            return
        g_playerEvents.onPrebattlesListReceived += self.__pe_onPrebattlesListReceived
        return

    def stop(self):
        g_playerEvents.onPrebattlesListReceived -= self.__pe_onPrebattlesListReceived
        self.__callback = None
        if self.__ctx:
            self.__ctx.stopProcessing(False)
            self.__ctx = None
        return

    def request(self, ctx = None):
        if self.__cooldown.validate(REQUEST_TYPE.PREBATTLES_LIST):
            if ctx:
                ctx.stopProcessing(False)
            return
        LOG_DEBUG('Request prebattle', ctx)
        self.__cooldown.process(REQUEST_TYPE.PREBATTLES_LIST)
        self.__ctx = ctx
        if ctx.byDivision():
            BigWorld.player().requestPrebattlesByDivision(ctx.isNotInBattle, ctx.division)
        elif ctx.byName():
            BigWorld.player().requestPrebattlesByName(PREBATTLE_TYPE.COMPANY, ctx.isNotInBattle, ctx.creatorMask)
        else:
            BigWorld.player().requestPrebattles(PREBATTLE_TYPE.COMPANY, PREBATTLE_CACHE_KEY.CREATE_TIME, ctx.isNotInBattle, -50, 0)

    def __pe_onPrebattlesListReceived(self, prbType, _, prebattles):
        if prbType != PREBATTLE_TYPE.COMPANY:
            return
        else:
            if self.__ctx:
                self.__ctx.stopProcessing(True)
                self.__ctx = None
            self.__callback(prb_seqs.PrbListIterator(reversed(prebattles)))
            return


class CompanyIntroFunctional(IntroPrbFunctional):

    def __init__(self):
        handlers = {REQUEST_TYPE.PREBATTLES_LIST: self.requestList,
         REQUEST_TYPE.GET_ROSTER: self.requestRoster}
        super(CompanyIntroFunctional, self).__init__(PREBATTLE_TYPE.COMPANY, _CompanyListRequester(), handlers)
        self._rosterReq = PrbRosterRequester()

    def init(self, clientPrb = None, ctx = None):
        result = super(CompanyIntroFunctional, self).init()
        self._rosterReq.start(self._onPrbRosterReceived)
        g_eventDispatcher.loadCompany()
        result = FUNCTIONAL_FLAG.addIfNot(result, FUNCTIONAL_FLAG.LOAD_WINDOW)
        g_eventDispatcher.updateUI()
        g_eventsCache.companies.onCompanyStateChanged += self.onCompanyStateChanged
        return result

    def fini(self, clientPrb = None, woEvents = False):
        super(CompanyIntroFunctional, self).fini()
        if self._flags & FUNCTIONAL_FLAG.SWITCH == 0:
            if not woEvents:
                g_eventDispatcher.unloadCompany()
            else:
                g_eventDispatcher.removeCompanyFromCarousel()
            g_eventDispatcher.updateUI()
        g_eventsCache.companies.onCompanyStateChanged -= self.onCompanyStateChanged

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def onCompanyStateChanged(self, state):
        if not state:
            DialogsInterface.showDialog(rally_dialog_meta.createCompanyExpariedMeta(), self.__companyExpiredCallback)

    def canPlayerDoAction(self):
        return (not self._hasEntity, '')

    def doSelectAction(self, action):
        result = False
        if action.actionName == PREBATTLE_ACTION_NAME.COMPANY:
            g_eventDispatcher.showCompanyWindow()
            result = True
        return SelectResult(result, None)

    def requestList(self, ctx, callback = None):
        if self._listReq.isInCooldown():
            self._listReq.fireCooldownEvent()
            if callback:
                callback(True)
        else:
            ctx.startProcessing(callback)
            self._listReq.request(ctx)

    def requestRoster(self, ctx, callback = None):
        ctx.startProcessing(callback)
        self._rosterReq.request(ctx)

    def _onPrbRosterReceived(self, prbID, roster):
        self._invokeListeners('onPrbRosterReceived', prbID, roster)

    def __companyExpiredCallback(self, _):
        ctx = LeavePrbCtx(waitingID='prebattle/leave')
        if self.prbDispatcher.setRequestCtx(ctx):
            self.leave(ctx)


class CompanyFunctional(PrbFunctional):

    def __init__(self, settings):
        requests = {REQUEST_TYPE.ASSIGN: self.assign,
         REQUEST_TYPE.SET_TEAM_STATE: self.setTeamState,
         REQUEST_TYPE.SET_PLAYER_STATE: self.setPlayerState,
         REQUEST_TYPE.CHANGE_OPENED: self.changeOpened,
         REQUEST_TYPE.CHANGE_COMMENT: self.changeComment,
         REQUEST_TYPE.CHANGE_DIVISION: self.changeDivision,
         REQUEST_TYPE.KICK: self.kickPlayer,
         REQUEST_TYPE.SEND_INVITE: self.sendInvites}
        super(CompanyFunctional, self).__init__(settings, permClass=CompanyPrbPermissions, limits=CompanyLimits(self), requestHandlers=requests)
        self.__doTeamReady = False

    def init(self, clientPrb = None, ctx = None):
        result = super(CompanyFunctional, self).init(clientPrb=clientPrb)
        playerInfo = self.getPlayerInfo()
        if self.getTeamState(team=1).isInQueue() and playerInfo.isReady() and playerInfo.roster == PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1:
            g_eventDispatcher.loadBattleQueue()
        else:
            g_eventDispatcher.loadHangar()
        g_eventDispatcher.loadCompany()
        result = FUNCTIONAL_FLAG.addIfNot(result, FUNCTIONAL_FLAG.LOAD_WINDOW)
        result = FUNCTIONAL_FLAG.addIfNot(result, FUNCTIONAL_FLAG.LOAD_PAGE)
        g_eventBus.addListener(ChannelCarouselEvent.CAROUSEL_INITED, self.__handleCarouselInited, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventDispatcher.updateUI()
        g_eventsCache.companies.onCompanyStateChanged += self.onCompanyStateChanged
        return result

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def onCompanyStateChanged(self, state):
        if not state and not self.hasLockedState():
            DialogsInterface.showDialog(rally_dialog_meta.createCompanyExpariedMeta(), self.__companyExpiredCallback)

    def isGUIProcessed(self):
        return True

    def fini(self, clientPrb = None, woEvents = False):
        super(CompanyFunctional, self).fini(clientPrb=clientPrb, woEvents=woEvents)
        if self._flags & FUNCTIONAL_FLAG.SWITCH == 0:
            if not woEvents:
                g_eventDispatcher.unloadCompany()
            else:
                g_eventDispatcher.removeCompanyFromCarousel()
            g_eventDispatcher.updateUI()
        else:
            g_eventDispatcher.requestToDestroyPrbChannel(PREBATTLE_TYPE.COMPANY)
        g_eventBus.removeListener(ChannelCarouselEvent.CAROUSEL_INITED, self.__handleCarouselInited, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventsCache.companies.onCompanyStateChanged -= self.onCompanyStateChanged
        return FUNCTIONAL_FLAG.UNDEFINED

    @vehicleAmmoCheck
    def setPlayerState(self, ctx, callback = None):
        super(CompanyFunctional, self).setPlayerState(ctx, callback)

    def getPlayersStateStats(self):
        return self._getPlayersStateStats(PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1)

    def getRosters(self, keys = None):
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
                result[key] = map(lambda accInfo: prb_items.PlayerPrbInfo(accInfo[0], functional=self, roster=key, **accInfo[1]), roster.iteritems())

        return result

    def canPlayerDoAction(self):
        isValid, notValidReason = True, ''
        team, assigned = decodeRoster(self.getRosterKey())
        if self.getTeamState().isInQueue() and assigned:
            isValid, notValidReason = False, PREBATTLE_RESTRICTION.TEAM_IS_IN_QUEUE
        elif self.isCreator():
            isValid, notValidReason = self._limits.isTeamValid()
        return (isValid, notValidReason)

    def doAction(self, action = None):
        if self.isCreator():
            if self.getRosterKey() != PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1:
                DialogsInterface.showI18nInfoDialog('teamDoesNotHaveCommander', lambda result: None)
                return True
            stats = self.getPlayersStateStats()
            creatorWeight = 1 if not self.getPlayerInfo().isReady() else 0
            readyCount = stats.playersCount - stats.notReadyCount
            if readyCount < stats.limitMaxCount - creatorWeight:
                DialogsInterface.showDialog(I18nConfirmDialogMeta('teamHaveNotReadyPlayers', messageCtx={'readyCount': readyCount,
                 'playersCount': stats.playersCount}), self.__setCreatorReady)
                return True
            self.__setCreatorReady(True)
        elif self.getPlayerInfo().isReady():
            self.setPlayerState(prb_ctx.SetPlayerStateCtx(False, waitingID='prebattle/player_not_ready'))
        else:
            self.setPlayerState(prb_ctx.SetPlayerStateCtx(True, waitingID='prebattle/player_ready'))
        return True

    def doSelectAction(self, action):
        result = False
        if action.actionName == PREBATTLE_ACTION_NAME.COMPANY:
            g_eventDispatcher.loadCompany()
            result = True
        return SelectResult(result, None)

    def exitFromQueue(self):
        if self.isCreator():
            self.setTeamState(prb_ctx.SetTeamStateCtx(1, False, waitingID='prebattle/team_not_ready'))
        else:
            self.setPlayerState(prb_ctx.SetPlayerStateCtx(False, waitingID='prebattle/player_not_ready'))
        return True

    def showGUI(self, ctx = None):
        g_eventDispatcher.loadCompany()

    def changeOpened(self, ctx, callback = None):
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

    def changeComment(self, ctx, callback = None):
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

    def changeDivision(self, ctx, callback = None):
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
        super(CompanyFunctional, self).prb_onSettingUpdated(settingName)
        if settingName == PREBATTLE_SETTING_NAME.LIMITS:
            g_eventDispatcher.updateUI()

    def prb_onPlayerStateChanged(self, pID, roster):
        super(CompanyFunctional, self).prb_onPlayerStateChanged(pID, roster)
        if self.__doTeamReady:
            self.__doTeamReady = False
            self.__setTeamReady()
        g_eventDispatcher.updateUI()

    def prb_onRosterReceived(self):
        super(CompanyFunctional, self).prb_onRosterReceived()
        g_eventDispatcher.updateUI()

    def prb_onPlayerRosterChanged(self, pID, prevRoster, roster, actorID):
        super(CompanyFunctional, self).prb_onPlayerRosterChanged(pID, prevRoster, roster, actorID)
        g_eventDispatcher.updateUI()

    def prb_onTeamStatesReceived(self):
        super(CompanyFunctional, self).prb_onTeamStatesReceived()
        g_eventDispatcher.updateUI()
        playerInfo = self.getPlayerInfo()
        if playerInfo.isReady() or self.isCreator():
            if self.getTeamState(team=1).isInQueue() and playerInfo.roster == PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1:
                g_eventDispatcher.loadBattleQueue()
            else:
                g_eventDispatcher.loadHangar()

    def prb_onPlayerAdded(self, pID, roster):
        super(CompanyFunctional, self).prb_onPlayerAdded(pID, roster)
        g_eventDispatcher.updateUI()

    def prb_onPlayerRemoved(self, pID, roster, name):
        super(CompanyFunctional, self).prb_onPlayerRemoved(pID, roster, name)
        g_eventDispatcher.updateUI()

    def __setCreatorReady(self, result):
        if not result:
            return
        if self.getPlayerInfo().isReady():
            self.__setTeamReady()
        else:
            self.setPlayerState(prb_ctx.SetPlayerStateCtx(True, waitingID='prebattle/player_ready'), callback=self.__onCreatorReady)

    def __setTeamReady(self):
        if self.isCreator():
            self.setTeamState(prb_ctx.SetTeamStateCtx(1, True, waitingID='prebattle/team_ready', gamePlayMask=gameplay_ctx.getMask()))

    def __onCreatorReady(self, result):
        self.__doTeamReady = result

    def __handleCarouselInited(self, _):
        g_eventDispatcher.addCompanyToCarousel()

    def __companyExpiredCallback(self, _):
        ctx = LeavePrbCtx(waitingID='prebattle/leave')
        if self.prbDispatcher.setRequestCtx(ctx):
            self.leave(ctx)
