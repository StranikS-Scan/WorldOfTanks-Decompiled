# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/epic_battle_training/entity.py
from functools import partial
import BigWorld
import account_helpers
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.prb_control import prb_getters
from gui.prb_control.entities.base import cooldown
from gui.prb_control.entities.base.legacy.ctx import SetPlayerStateCtx
from gui.prb_control.entities.base.legacy.entity import LegacyEntryPoint, LegacyIntroEntryPoint, LegacyIntroEntity, LegacyEntity
from gui.prb_control.entities.epic_battle_training.limits import EpicBattleTrainingLimits
from gui.prb_control.entities.epic_battle_training.actions_validator import TrainingActionsValidator, TrainingIntroActionsValidator
from gui.prb_control.entities.epic_battle_training.ctx import EpicTrainingSettingsCtx, SetPlayerObserverStateCtx
from gui.prb_control.entities.epic_battle_training.permissions import EpicBattleTrainingPermissions, EpicBattleTrainingIntroPermissions
from gui.prb_control.entities.epic_battle_training.requester import EpicBattleTrainingListRequester
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import prb_items, SelectResult, ValidationResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, PREBATTLE_RESTRICTION
from gui.prb_control.settings import PREBATTLE_ROSTER, REQUEST_TYPE
from gui.prb_control.settings import PREBATTLE_SETTING_NAME
from gui.prb_control.storages import legacy_storage_getter
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ViewEventType
from prebattle_shared import decodeRoster

class EpicBattleTrainingEntryPoint(LegacyEntryPoint):

    def __init__(self):
        super(EpicBattleTrainingEntryPoint, self).__init__(FUNCTIONAL_FLAG.EPIC_TRAINING)

    def create(self, ctx, callback=None):
        if not isinstance(ctx, EpicTrainingSettingsCtx):
            LOG_ERROR('Invalid context to create training', ctx)
            if callback is not None:
                callback(False)
        elif not self.canCreate():
            if callback is not None:
                callback(False)
        elif prb_getters.isParentControlActivated():
            g_eventDispatcher.showParentControlNotification()
            if callback:
                callback(False)
        elif prb_getters.getClientPrebattle() is None or ctx.isForced():
            ctx.startProcessing(callback=callback)
            BigWorld.player().prb_createEpicTrainingBattle(ctx.getArenaTypeID(), ctx.getRoundLen(), ctx.isOpened(), ctx.getComment())
            cooldown.setPrbCreationCooldown()
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle', prb_getters.getPrebattleType())
            if callback is not None:
                callback(False)
        return

    def canCreate(self):
        return not cooldown.validatePrbCreationCooldown()


class EpicBattleTrainingIntroEntryPoint(LegacyIntroEntryPoint):

    def __init__(self):
        super(EpicBattleTrainingIntroEntryPoint, self).__init__(FUNCTIONAL_FLAG.EPIC_TRAINING | FUNCTIONAL_FLAG.LOAD_PAGE, PREBATTLE_TYPE.EPIC_TRAINING)


class EpicBattleTrainingIntroEntity(LegacyIntroEntity):

    def __init__(self):
        super(EpicBattleTrainingIntroEntity, self).__init__(FUNCTIONAL_FLAG.EPIC_TRAINING, PREBATTLE_TYPE.EPIC_TRAINING, EpicBattleTrainingListRequester())

    def init(self, clientPrb=None, ctx=None):
        result = super(EpicBattleTrainingIntroEntity, self).init()
        g_eventDispatcher.loadEpicTrainingList()
        result = FUNCTIONAL_FLAG.addIfNot(result, FUNCTIONAL_FLAG.LOAD_PAGE)
        return result

    def fini(self, clientPrb=None, ctx=None, woEvents=False):
        result = super(EpicBattleTrainingIntroEntity, self).fini()
        if not woEvents:
            g_eventDispatcher.removeEpicTrainingFromCarousel()
        else:
            g_eventDispatcher.removeEpicTrainingFromCarousel(closeWindow=False)
        return result

    def doAction(self, action=None):
        g_eventDispatcher.loadEpicTrainingList()
        return True

    def doSelectAction(self, action):
        if action.actionName == PREBATTLE_ACTION_NAME.EPIC_TRAINING_LIST:
            g_eventDispatcher.loadEpicTrainingList()
            return SelectResult(True)
        return super(EpicBattleTrainingIntroEntity, self).doSelectAction(action)

    def getPermissions(self, pID=None):
        return EpicBattleTrainingIntroPermissions()

    def _createActionsValidator(self):
        return TrainingIntroActionsValidator(self)


class EpicBattleTrainingEntity(LegacyEntity):
    __loadEvents = (VIEW_ALIAS.LOBBY_HANGAR,
     VIEW_ALIAS.LOBBY_STORE,
     VIEW_ALIAS.LOBBY_STORAGE,
     VIEW_ALIAS.LOBBY_TECHTREE,
     VIEW_ALIAS.LOBBY_BARRACKS,
     VIEW_ALIAS.LOBBY_PROFILE,
     VIEW_ALIAS.VEHICLE_COMPARE)

    def __init__(self, settings):
        requests = {REQUEST_TYPE.ASSIGN: self.assign,
         REQUEST_TYPE.SET_TEAM_STATE: self.setTeamState,
         REQUEST_TYPE.SET_PLAYER_STATE: self.setPlayerState,
         REQUEST_TYPE.CHANGE_SETTINGS: self.changeSettings,
         REQUEST_TYPE.CHANGE_ARENA_VOIP: self.changeArenaVoip,
         REQUEST_TYPE.CHANGE_USER_STATUS: self.changeUserObserverStatus,
         REQUEST_TYPE.KICK: self.kickPlayer,
         REQUEST_TYPE.SEND_INVITE: self.sendInvites,
         REQUEST_TYPE.EPIC_SWAP_IN_TEAM: self.swapInTeam,
         REQUEST_TYPE.EPIC_SWAP_BETWEEN_TEAM: self.swapBetweenTeam}
        super(EpicBattleTrainingEntity, self).__init__(FUNCTIONAL_FLAG.EPIC_TRAINING, settings, permClass=EpicBattleTrainingPermissions, limits=EpicBattleTrainingLimits(self), requestHandlers=requests)
        self.__settingRecords = []
        self.storage = legacy_storage_getter(PREBATTLE_TYPE.EPIC_TRAINING)()

    def init(self, clientPrb=None, ctx=None):
        result = super(EpicBattleTrainingEntity, self).init(clientPrb=clientPrb)
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self.__handleViewLoad, scope=EVENT_BUS_SCOPE.LOBBY)
        if clientPrb is None:
            clientPrb = prb_getters.getClientPrebattle()
        if clientPrb is not None:
            clientPrb.onPlayerGroupChanged += self.__prb_onPlayerGroupChanged
        self.__enterTrainingRoom(True)
        g_eventDispatcher.addEpicTrainingToCarousel(False)
        result = FUNCTIONAL_FLAG.addIfNot(result, FUNCTIONAL_FLAG.LOAD_WINDOW)
        result = FUNCTIONAL_FLAG.addIfNot(result, FUNCTIONAL_FLAG.LOAD_PAGE)
        return result

    def fini(self, clientPrb=None, ctx=None, woEvents=False):
        super(EpicBattleTrainingEntity, self).fini(clientPrb=clientPrb, ctx=ctx, woEvents=woEvents)
        clientPrb = prb_getters.getClientPrebattle()
        if clientPrb is not None:
            clientPrb.onPlayerGroupChanged -= self.__prb_onPlayerGroupChanged
        g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self.__handleViewLoad, scope=EVENT_BUS_SCOPE.LOBBY)
        if not woEvents:
            aliasToLoad = [PREBATTLE_ALIASES.EPICBATTLE_LIST_VIEW_PY, PREBATTLE_ALIASES.EPIC_TRAINING_ROOM_VIEW_PY]
            if not self.canSwitch(ctx) and g_eventDispatcher.needToLoadHangar(ctx, self.getModeFlags(), aliasToLoad):
                g_eventDispatcher.loadHangar()
            g_eventDispatcher.removeEpicTrainingFromCarousel(False)
            self.storage.suspend()
        else:
            g_eventDispatcher.removeEpicTrainingFromCarousel(False, closeWindow=False)
        return FUNCTIONAL_FLAG.UNDEFINED

    def resetPlayerState(self):
        super(EpicBattleTrainingEntity, self).resetPlayerState()
        g_eventDispatcher.loadHangar()

    def getRosters(self, keys=None):
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
                result[key] = []

        hasTeam1 = PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 in result
        hasTeam2 = PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2 in result
        hasUnassigned = PREBATTLE_ROSTER.UNASSIGNED in result
        for key, roster in rosters.iteritems():
            accounts = map(lambda accInfo: prb_items.PlayerPrbInfo(accInfo[0], entity=self, roster=key, **accInfo[1]), roster.iteritems())
            team, assigned = decodeRoster(key)
            if assigned:
                if hasTeam1 and team == 1:
                    result[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1] = accounts
                elif hasTeam2 and team == 2:
                    result[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2] = accounts
            if hasUnassigned:
                result[PREBATTLE_ROSTER.UNASSIGNED].extend(accounts)

        return result

    def getTeamLimits(self):
        return prb_getters.getPrebattleSettings().getTeamLimits(self.getPlayerTeam())

    def doAction(self, action=None):
        self.__enterTrainingRoom()
        return True

    def doSelectAction(self, action):
        if action.actionName == PREBATTLE_ACTION_NAME.EPIC_TRAINING_LIST:
            self.__enterTrainingRoom()
            return SelectResult(True)
        return super(EpicBattleTrainingEntity, self).doSelectAction(action)

    def hasGUIPage(self):
        return True

    def showGUI(self, ctx=None):
        self.__enterTrainingRoom()

    def prb_onPlayerStateChanged(self, pID, roster):
        if pID == account_helpers.getPlayerID():
            playerInfo = self.getPlayerInfo(pID=pID)
            self.storage.isObserver = playerInfo.isVehicleSpecified() and playerInfo.getVehicle().isObserver
        super(EpicBattleTrainingEntity, self).prb_onPlayerStateChanged(pID, roster)

    def changeSettings(self, ctx, callback=None):
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
            elif not self.__settingRecords:
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
            if not self.__settingRecords:
                if callback is not None:
                    callback(False)
            else:
                self._cooldown.process(REQUEST_TYPE.CHANGE_SETTINGS)
            return

    def changeUserObserverStatus(self, ctx, callback=None):
        if self._cooldown.validate(REQUEST_TYPE.CHANGE_USER_STATUS):
            if callback is not None:
                callback(False)
            return
        else:
            if ctx.isObserver():
                self._setPlayerReady(ctx, callback=callback)
            else:
                self._setPlayerReady(SetPlayerStateCtx(ctx.isReadyState(), ctx.isInitial(), waitingID='prebattle/player_ready'), self.__onPlayerReady)
            self._cooldown.process(REQUEST_TYPE.CHANGE_USER_STATUS)
            return

    def changeArenaVoip(self, ctx, callback=None):
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

    def swapInTeam(self, ctx, callback=None):
        if self._cooldown.validate(REQUEST_TYPE.EPIC_SWAP_IN_TEAM):
            if callback:
                callback(False)
            return
        pPermissions = self.getPermissions()
        if pPermissions.canChangePlayerTeam():
            roster = ctx.getRoster()
            flane, tlane = ctx.getGroups()
            ctx.startProcessing(callback)
            BigWorld.player().prb_swapGroupsWithinTeam(roster, flane, tlane, ctx.onResponseReceived)
            self._cooldown.process(REQUEST_TYPE.EPIC_SWAP_IN_TEAM)
        else:
            LOG_ERROR('Player can not swap teams', pPermissions)
            if callback:
                callback(False)

    def swapBetweenTeam(self, ctx, callback=None):
        if self._cooldown.validate(REQUEST_TYPE.EPIC_SWAP_BETWEEN_TEAM):
            if callback:
                callback(False)
            return
        pPermissions = self.getPermissions()
        if pPermissions.canChangePlayerTeam():
            lane = ctx.getGroup()
            ctx.startProcessing(callback)
            BigWorld.player().prb_swapTeamsWithinGroup(lane, ctx.onResponseReceived)
            self._cooldown.process(REQUEST_TYPE.EPIC_SWAP_BETWEEN_TEAM)
        else:
            LOG_ERROR('Player can not swap teams', pPermissions)
            if callback:
                callback(False)

    def assign(self, ctx, callback=None):
        prevTeam, _ = decodeRoster(self.getRosterKey(pID=ctx.getPlayerID()))
        nextTeam, assigned = decodeRoster(ctx.getRoster())
        pPermissions = self.getPermissions()
        if prevTeam is nextTeam:
            if not pPermissions.canAssignToTeam(team=nextTeam):
                LOG_ERROR('Player can not change roster', nextTeam, assigned)
                if callback:
                    callback(False)
                return
        elif not pPermissions.canChangePlayerTeam():
            LOG_ERROR('Player can not change team', prevTeam, nextTeam)
            if callback:
                callback(False)
            return
        if prevTeam != nextTeam:
            result = self.getLimits().isMaxCountValid(nextTeam, assigned)
            if result is not None and not result.isValid:
                LOG_ERROR('Max count limit', nextTeam, assigned)
                if callback:
                    callback(False)
                return
        ctx.startProcessing(callback)
        BigWorld.player().prb_assignGroup(ctx.getPlayerID(), ctx.getRoster(), ctx.getGroup(), ctx.onResponseReceived)
        return

    def _createActionsValidator(self):
        return TrainingActionsValidator(self)

    def _setPlayerReady(self, ctx, callback=None):
        if g_currentVehicle.isObserver():
            if not self._processValidationResult(ctx, ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_NOT_SUPPORTED)):
                if callback:
                    callback(False)
                return
        super(EpicBattleTrainingEntity, self)._setPlayerReady(ctx, callback)

    def __enterTrainingRoom(self, isInitial=False):
        if self.storage.isObserver:
            self.changeUserObserverStatus(SetPlayerObserverStateCtx(True, True, isInitial=isInitial, waitingID='prebattle/change_user_status'), self.__onPlayerReady)
        else:
            self.setPlayerState(SetPlayerStateCtx(True, isInitial=isInitial, waitingID='prebattle/player_ready'), self.__onPlayerReady)

    def __onPlayerReady(self, result):
        if result:
            g_eventDispatcher.loadEpicTrainingRoom()
        else:
            g_eventDispatcher.loadHangar()

    def __onSettingChanged(self, code, record='', callback=None):
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

    def __handleViewLoad(self, event):
        if event.alias in self.__loadEvents:
            self.setPlayerState(SetPlayerStateCtx(False, waitingID='prebattle/player_not_ready'))

    def __prb_onPlayerGroupChanged(self, pID, prevRoster, roster, group, actorID):
        rosters = self.getRosters(keys=[prevRoster, roster])
        actorInfo = self.getPlayerInfo(pID=actorID)
        playerInfo = self.getPlayerInfo(pID=pID)
        for listener in self.getListenersIterator():
            if actorInfo and playerInfo:
                listener.onPlayerRosterChanged(self, actorInfo, playerInfo)
            listener.onRostersChanged(self, rosters, False)
