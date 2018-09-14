# Embedded file name: scripts/client/gui/prb_control/functional/training.py
from functools import partial
import BigWorld
import account_helpers
from PlayerEvents import g_playerEvents
from adisp import process
from constants import PREBATTLE_TYPE, PREBATTLE_CACHE_KEY
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.prb_control import prb_cooldown, prb_getters
from gui.prb_control.context import prb_ctx
from gui.prb_control.functional import default
from gui.prb_control.functional import interfaces
from gui.prb_control.items import prb_items, prb_seqs, SelectResult
from gui.prb_control.storage import prb_storage_getter
from gui.prb_control.restrictions.limits import TrainingLimits
from gui.prb_control.restrictions.permissions import TrainingPrbPermissions
from gui.prb_control.settings import PREBATTLE_ROSTER, REQUEST_TYPE
from gui.prb_control.settings import PREBATTLE_SETTING_NAME
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.utils.functions import checkAmmoLevel
from prebattle_shared import decodeRoster

class TrainingEntry(default.PrbEntry):

    def create(self, ctx, callback = None):
        if not isinstance(ctx, prb_ctx.TrainingSettingsCtx):
            LOG_ERROR('Invalid context to create training', ctx)
            if callback is not None:
                callback(False)
        elif prb_cooldown.validatePrbCreationCooldown():
            if callback is not None:
                callback(False)
        elif prb_getters.getClientPrebattle() is None or ctx.isForced():
            ctx.startProcessing(callback=callback)
            BigWorld.player().prb_createTraining(ctx.getArenaTypeID(), ctx.getRoundLen(), ctx.isOpened(), ctx.getComment())
            prb_cooldown.setPrbCreationCooldown()
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle', prb_getters.getPrebattleType())
            if callback is not None:
                callback(False)
        return

    @process
    def __loadTrainingList(self):
        result = yield checkAmmoLevel()
        if result:
            g_eventDispatcher.loadTrainingList()

    @process
    def __loadTrainingRoom(self, dispatcher):
        result = yield dispatcher.sendPrbRequest(prb_ctx.SetPlayerStateCtx(True, waitingID='prebattle/player_not_ready'))
        if result:
            g_eventDispatcher.loadTrainingRoom()


class _TrainingListRequester(interfaces.IPrbListUpdater):
    UPDATE_LIST_TIMEOUT = 5

    def __init__(self):
        super(_TrainingListRequester, self).__init__()
        self.__callbackID = None
        self.__callback = None
        return

    def start(self, callback):
        if self.__callbackID is not None:
            LOG_ERROR('TrainingListRequester already started')
            return
        else:
            if callback is not None and callable(callback):
                g_playerEvents.onPrebattlesListReceived += self.__pe_onPrebattlesListReceived
                self.__callback = callback
                self.__request()
            else:
                LOG_ERROR('Callback is None or is not callable')
                return
            return

    def stop(self):
        g_playerEvents.onPrebattlesListReceived -= self.__pe_onPrebattlesListReceived
        self.__callback = None
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __request(self):
        self.__callbackID = None
        if hasattr(BigWorld.player(), 'requestPrebattles'):
            BigWorld.player().requestPrebattles(PREBATTLE_TYPE.TRAINING, PREBATTLE_CACHE_KEY.CREATE_TIME, False, 0, 50)
        return

    def __setTimeout(self):
        self.__callbackID = BigWorld.callback(self.UPDATE_LIST_TIMEOUT, self.__request)

    def __pe_onPrebattlesListReceived(self, prbType, _, prebattles):
        if prbType != PREBATTLE_TYPE.TRAINING:
            return
        self.__callback(prb_seqs.PrbListIterator(prebattles))
        self.__setTimeout()


class TrainingIntroFunctional(default.IntroPrbFunctional):

    def __init__(self):
        super(TrainingIntroFunctional, self).__init__(PREBATTLE_TYPE.TRAINING, _TrainingListRequester())

    def init(self, clientPrb = None, ctx = None):
        result = super(TrainingIntroFunctional, self).init()
        g_eventDispatcher.loadTrainingList()
        result = FUNCTIONAL_FLAG.addIfNot(result, FUNCTIONAL_FLAG.LOAD_PAGE)
        g_eventDispatcher.updateUI()
        return result

    def fini(self, clientPrb = None, woEvents = False):
        super(TrainingIntroFunctional, self).fini()
        if self._flags & FUNCTIONAL_FLAG.SWITCH == 0 and not woEvents:
            g_eventDispatcher.loadHangar()
            g_eventDispatcher.removeTrainingFromCarousel()
            g_eventDispatcher.updateUI()
        return FUNCTIONAL_FLAG.UNDEFINED

    def doAction(self, action = None):
        g_eventDispatcher.loadTrainingList()
        return True

    def doSelectAction(self, action):
        result = False
        if action.actionName == PREBATTLE_ACTION_NAME.TRAINING:
            g_eventDispatcher.loadTrainingList()
            result = True
        return SelectResult(result, None)


class TrainingFunctional(default.PrbFunctional):
    __loadEvents = (VIEW_ALIAS.LOBBY_HANGAR,
     VIEW_ALIAS.LOBBY_INVENTORY,
     VIEW_ALIAS.LOBBY_SHOP,
     VIEW_ALIAS.LOBBY_TECHTREE,
     VIEW_ALIAS.LOBBY_BARRACKS,
     VIEW_ALIAS.LOBBY_PROFILE,
     FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_ALIAS)

    def __init__(self, settings):
        requests = {REQUEST_TYPE.ASSIGN: self.assign,
         REQUEST_TYPE.SET_TEAM_STATE: self.setTeamState,
         REQUEST_TYPE.SET_PLAYER_STATE: self.setPlayerState,
         REQUEST_TYPE.CHANGE_SETTINGS: self.changeSettings,
         REQUEST_TYPE.SWAP_TEAMS: self.swapTeams,
         REQUEST_TYPE.CHANGE_ARENA_VOIP: self.changeArenaVoip,
         REQUEST_TYPE.CHANGE_USER_STATUS: self.changeUserObserverStatus,
         REQUEST_TYPE.KICK: self.kickPlayer,
         REQUEST_TYPE.SEND_INVITE: self.sendInvites}
        super(TrainingFunctional, self).__init__(settings, permClass=TrainingPrbPermissions, limits=TrainingLimits(self), requestHandlers=requests)
        self.__settingRecords = []

    @prb_storage_getter(PREBATTLE_TYPE.TRAINING)
    def storage(self):
        return None

    def init(self, clientPrb = None, ctx = None):
        result = super(TrainingFunctional, self).init(clientPrb=clientPrb)
        add = g_eventBus.addListener
        for event in self.__loadEvents:
            add(event, self.__handleViewLoad, scope=EVENT_BUS_SCOPE.LOBBY)

        self.__enterTrainingRoom()
        result |= FUNCTIONAL_FLAG.LOAD_WINDOW
        result |= FUNCTIONAL_FLAG.LOAD_PAGE
        g_eventDispatcher.updateUI()
        return result

    def fini(self, clientPrb = None, woEvents = False):
        super(TrainingFunctional, self).fini(clientPrb=clientPrb, woEvents=woEvents)
        remove = g_eventBus.removeListener
        for event in self.__loadEvents:
            remove(event, self.__handleViewLoad, scope=EVENT_BUS_SCOPE.LOBBY)

        if not woEvents:
            if self._flags & FUNCTIONAL_FLAG.SWITCH > 0:
                g_eventDispatcher.loadTrainingList()
            else:
                g_eventDispatcher.loadHangar()
                g_eventDispatcher.removeTrainingFromCarousel(False)
                g_eventDispatcher.updateUI()
            self.storage.suspend()
        g_eventDispatcher.requestToDestroyPrbChannel(PREBATTLE_TYPE.TRAINING)
        return FUNCTIONAL_FLAG.UNDEFINED

    def reset(self):
        super(TrainingFunctional, self).reset()
        g_eventDispatcher.loadHangar()

    def getRosters(self, keys = None):
        rosters = prb_getters.getPrebattleRosters()
        if keys is None:
            result = {PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1: [],
             PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2: [],
             PREBATTLE_ROSTER.UNASSIGNED: []}
        else:
            result = {}
            for key in keys:
                if PREBATTLE_ROSTER.UNASSIGNED & key != 0:
                    result[PREBATTLE_ROSTER.UNASSIGNED] = []
                else:
                    result[key] = []

        hasTeam1 = PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 in result
        hasTeam2 = PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2 in result
        hasUnassigned = PREBATTLE_ROSTER.UNASSIGNED in result
        for key, roster in rosters.iteritems():
            accounts = map(lambda accInfo: prb_items.PlayerPrbInfo(accInfo[0], functional=self, roster=key, **accInfo[1]), roster.iteritems())
            team, assigned = decodeRoster(key)
            if assigned:
                if hasTeam1 and team is 1:
                    result[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1] = accounts
                elif hasTeam2 and team is 2:
                    result[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2] = accounts
            elif hasUnassigned:
                result[PREBATTLE_ROSTER.UNASSIGNED].extend(accounts)

        return result

    def canPlayerDoAction(self):
        return (True, '')

    def doAction(self, action = None):
        self.__enterTrainingRoom()
        return True

    def doSelectAction(self, action):
        result = False
        if action.actionName == PREBATTLE_ACTION_NAME.TRAINING:
            self.__enterTrainingRoom()
            result = True
        return SelectResult(result, None)

    def hasGUIPage(self):
        return True

    def showGUI(self, ctx = None):
        self.__enterTrainingRoom()

    def changeSettings(self, ctx, callback = None):
        if ctx.getRequestType() != REQUEST_TYPE.CHANGE_SETTINGS:
            LOG_ERROR('Invalid context for request changeSettings', ctx)
            if callback is not None:
                callback(False)
            return
        elif self._cooldown.validate(REQUEST_TYPE.CHANGE_SETTINGS):
            if callback is not None:
                callback(False)
            return
        else:
            player = BigWorld.player()
            pPermissions = self.getPermissions()
            self.__settingRecords = []
            rejected = False
            isOpenedChanged = ctx.isOpenedChanged(self._settings)
            isCommentChanged = ctx.isCommentChanged(self._settings)
            isArenaTypeIDChanged = ctx.isArenaTypeIDChanged(self._settings)
            isRoundLenChanged = ctx.isRoundLenChanged(self._settings)
            if isOpenedChanged:
                if pPermissions.canMakeOpenedClosed():
                    self.__settingRecords.append('isOpened')
                else:
                    LOG_ERROR('Player can not make training opened/closed', pPermissions)
                    rejected = True
            if isCommentChanged:
                if pPermissions.canChangeComment():
                    self.__settingRecords.append('comment')
                else:
                    LOG_ERROR('Player can not change comment', pPermissions)
                    rejected = True
            if isArenaTypeIDChanged:
                if pPermissions.canChangeArena():
                    self.__settingRecords.append('arenaTypeID')
                else:
                    LOG_ERROR('Player can not change comment', pPermissions)
                    rejected = True
            if isRoundLenChanged:
                if pPermissions.canChangeArena():
                    self.__settingRecords.append('roundLength')
                else:
                    LOG_ERROR('Player can not change comment', pPermissions)
                    rejected = True
            if rejected:
                self.__settingRecords = []
                if callback is not None:
                    callback(False)
                return
            elif not len(self.__settingRecords):
                if callback is not None:
                    callback(False)
                return
            ctx.startProcessing(callback=callback)
            if isOpenedChanged:
                player.prb_changeOpenStatus(ctx.isOpened(), partial(self.__onSettingChanged, record='isOpened', callback=ctx.stopProcessing))
            if isCommentChanged:
                player.prb_changeComment(ctx.getComment(), partial(self.__onSettingChanged, record='comment', callback=ctx.stopProcessing))
            if isArenaTypeIDChanged:
                player.prb_changeArena(ctx.getArenaTypeID(), partial(self.__onSettingChanged, record='arenaTypeID', callback=ctx.stopProcessing))
            if isRoundLenChanged:
                player.prb_changeRoundLength(ctx.getRoundLen(), partial(self.__onSettingChanged, record='roundLength', callback=ctx.stopProcessing))
            if not len(self.__settingRecords):
                if callback is not None:
                    callback(False)
            else:
                self._cooldown.process(REQUEST_TYPE.CHANGE_SETTINGS)
            return

    def changeUserObserverStatus(self, ctx, callback = None):
        if self._cooldown.validate(REQUEST_TYPE.CHANGE_USER_STATUS):
            if callback is not None:
                callback(False)
            return
        else:
            if ctx.isObserver():
                self._setPlayerReady(ctx, callback=callback)
            else:
                self._setPlayerReady(prb_ctx.SetPlayerStateCtx(True, waitingID='prebattle/player_ready'), self.__onPlayerReady)
            self._cooldown.process(REQUEST_TYPE.CHANGE_USER_STATUS)
            return

    def changeArenaVoip(self, ctx, callback = None):
        setting = self._settings[PREBATTLE_SETTING_NAME.ARENA_VOIP_CHANNELS]
        if ctx.getChannels() == setting:
            if callback is not None:
                callback(True)
            return
        elif self._cooldown.validate(REQUEST_TYPE.CHANGE_ARENA_VOIP):
            if callback is not None:
                callback(False)
            return
        else:
            pPermissions = self.getPermissions()
            if pPermissions.canChangeArenaVOIP():
                ctx.startProcessing(callback=callback)
                BigWorld.player().prb_changeArenaVoip(ctx.getChannels(), ctx.onResponseReceived)
                self._cooldown.process(REQUEST_TYPE.CHANGE_ARENA_VOIP)
            else:
                LOG_ERROR('Player can not change arena VOIP', pPermissions)
                if callback is not None:
                    callback(False)
            return

    def prb_onPlayerStateChanged(self, pID, roster):
        if pID == account_helpers.getPlayerID():
            playerInfo = self.getPlayerInfo(pID=pID)
            self.storage.isObserver = playerInfo.isVehicleSpecified() and playerInfo.getVehicle().isObserver
        super(TrainingFunctional, self).prb_onPlayerStateChanged(pID, roster)

    def __enterTrainingRoom(self):
        if self.storage.isObserver:
            self.changeUserObserverStatus(prb_ctx.SetPlayerObserverStateCtx(True, True, waitingID='prebattle/change_user_status'), self.__onPlayerReady)
        else:
            self.setPlayerState(prb_ctx.SetPlayerStateCtx(True, waitingID='prebattle/player_ready'), self.__onPlayerReady)

    @staticmethod
    def __onPlayerReady(result):
        if result:
            g_eventDispatcher.loadTrainingRoom()
        else:
            g_eventDispatcher.loadHangar()
            g_eventDispatcher.removeTrainingFromCarousel()
            g_eventDispatcher.addTrainingToCarousel(False)

    def __onSettingChanged(self, code, record = '', callback = None):
        if code < 0:
            LOG_ERROR('Server return error for training change', code, record)
            if callback is not None:
                callback(False)
            return
        else:
            if record in self.__settingRecords:
                self.__settingRecords.remove(record)
            if not self.__settingRecords and callback is not None:
                callback(True)
            return

    def __handleViewLoad(self, _):
        self.setPlayerState(prb_ctx.SetPlayerStateCtx(False, waitingID='prebattle/player_not_ready'))
