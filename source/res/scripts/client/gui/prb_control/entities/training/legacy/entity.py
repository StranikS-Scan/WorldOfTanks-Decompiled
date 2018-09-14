# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/training/legacy/entity.py
from functools import partial
import BigWorld
import account_helpers
from adisp import process
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.prb_control import prb_getters
from gui.prb_control.entities.training.legacy.actions_validator import TrainingActionsValidator, TrainingIntroActionsValidator
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base import cooldown
from gui.prb_control.entities.base.legacy.ctx import SetPlayerStateCtx
from gui.prb_control.entities.base.legacy.entity import LegacyEntryPoint, LegacyIntroEntryPoint, LegacyIntroEntity, LegacyEntity
from gui.prb_control.entities.training.legacy.ctx import TrainingSettingsCtx, SetPlayerObserverStateCtx
from gui.prb_control.entities.training.legacy.limits import TrainingLimits
from gui.prb_control.entities.training.legacy.permissions import TrainingPermissions
from gui.prb_control.entities.training.legacy.requester import TrainingListRequester
from gui.prb_control.items import prb_items, SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.settings import PREBATTLE_ROSTER, REQUEST_TYPE
from gui.prb_control.settings import PREBATTLE_SETTING_NAME
from gui.prb_control.storages import legacy_storage_getter
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.utils.functions import checkAmmoLevel
from prebattle_shared import decodeRoster

class TrainingEntryPoint(LegacyEntryPoint):
    """
    Training entry point
    """

    def __init__(self):
        super(TrainingEntryPoint, self).__init__(FUNCTIONAL_FLAG.TRAINING)

    def create(self, ctx, callback=None):
        if not isinstance(ctx, TrainingSettingsCtx):
            LOG_ERROR('Invalid context to create training', ctx)
            if callback is not None:
                callback(False)
        elif not self.canCreate():
            if callback is not None:
                callback(False)
        elif prb_getters.getClientPrebattle() is None or ctx.isForced():
            ctx.startProcessing(callback=callback)
            BigWorld.player().prb_createTraining(ctx.getArenaTypeID(), ctx.getRoundLen(), ctx.isOpened(), ctx.getComment())
            cooldown.setPrbCreationCooldown()
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle', prb_getters.getPrebattleType())
            if callback is not None:
                callback(False)
        return

    def canCreate(self):
        return not cooldown.validatePrbCreationCooldown()


class TrainingIntroEntryPoint(LegacyIntroEntryPoint):
    """
    Trainings intro entry point class
    """

    def __init__(self):
        super(TrainingIntroEntryPoint, self).__init__(FUNCTIONAL_FLAG.TRAINING, PREBATTLE_TYPE.TRAINING)


class TrainingIntroEntity(LegacyIntroEntity):
    """
    Trainings intro entity class
    """

    def __init__(self):
        super(TrainingIntroEntity, self).__init__(FUNCTIONAL_FLAG.TRAINING, PREBATTLE_TYPE.TRAINING, TrainingListRequester())

    def init(self, clientPrb=None, ctx=None):
        result = super(TrainingIntroEntity, self).init(clientPrb=clientPrb, ctx=ctx)
        g_eventDispatcher.loadTrainingList()
        result = FUNCTIONAL_FLAG.addIfNot(result, FUNCTIONAL_FLAG.LOAD_PAGE)
        return result

    def fini(self, clientPrb=None, ctx=None, woEvents=False):
        result = super(TrainingIntroEntity, self).fini(clientPrb=clientPrb, ctx=ctx, woEvents=woEvents)
        if not woEvents:
            if not self.canSwitch(ctx):
                g_eventDispatcher.loadHangar()
            g_eventDispatcher.removeTrainingFromCarousel()
        else:
            g_eventDispatcher.removeTrainingFromCarousel(closeWindow=False)
        return result

    def doAction(self, action=None):
        g_eventDispatcher.loadTrainingList()
        return True

    def doSelectAction(self, action):
        if action.actionName == PREBATTLE_ACTION_NAME.TRAININGS_LIST:
            g_eventDispatcher.loadTrainingList()
            return SelectResult(True)
        return super(TrainingIntroEntity, self).doSelectAction(action)

    def _createActionsValidator(self):
        return TrainingIntroActionsValidator(self)


class TrainingEntity(LegacyEntity):
    """
    Training entity class
    """
    __loadEvents = (VIEW_ALIAS.LOBBY_HANGAR,
     VIEW_ALIAS.LOBBY_INVENTORY,
     VIEW_ALIAS.LOBBY_STORE,
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
        super(TrainingEntity, self).__init__(FUNCTIONAL_FLAG.TRAINING, settings, permClass=TrainingPermissions, limits=TrainingLimits(self), requestHandlers=requests)
        self.__settingRecords = []

    @legacy_storage_getter(PREBATTLE_TYPE.TRAINING)
    def storage(self):
        """
        Trainings data storage getter property
        """
        return None

    def init(self, clientPrb=None, ctx=None):
        result = super(TrainingEntity, self).init(clientPrb=clientPrb, ctx=ctx)
        add = g_eventBus.addListener
        for event in self.__loadEvents:
            add(event, self.__handleViewLoad, scope=EVENT_BUS_SCOPE.LOBBY)

        self.__enterTrainingRoom(True)
        result = FUNCTIONAL_FLAG.addIfNot(result, FUNCTIONAL_FLAG.LOAD_WINDOW)
        result = FUNCTIONAL_FLAG.addIfNot(result, FUNCTIONAL_FLAG.LOAD_PAGE)
        return result

    def fini(self, clientPrb=None, ctx=None, woEvents=False):
        result = super(TrainingEntity, self).fini(clientPrb=clientPrb, ctx=ctx, woEvents=woEvents)
        remove = g_eventBus.removeListener
        for event in self.__loadEvents:
            remove(event, self.__handleViewLoad, scope=EVENT_BUS_SCOPE.LOBBY)

        if not woEvents:
            if not self.canSwitch(ctx):
                g_eventDispatcher.loadHangar()
            g_eventDispatcher.removeTrainingFromCarousel(False)
            self.storage.suspend()
        else:
            g_eventDispatcher.removeTrainingFromCarousel(False, closeWindow=False)
        return result

    def resetPlayerState(self):
        super(TrainingEntity, self).resetPlayerState()
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
                if hasTeam1 and team is 1:
                    result[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1] = accounts
                elif hasTeam2 and team is 2:
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
        if action.actionName == PREBATTLE_ACTION_NAME.TRAININGS_LIST:
            self.__enterTrainingRoom()
            return SelectResult(True)
        return super(TrainingEntity, self).doSelectAction(action)

    def hasGUIPage(self):
        return True

    def showGUI(self, ctx=None):
        self.__enterTrainingRoom()

    def prb_onPlayerStateChanged(self, pID, roster):
        if pID == account_helpers.getPlayerID():
            playerInfo = self.getPlayerInfo(pID=pID)
            if playerInfo.isVehicleSpecified():
                self.storage.isObserver = playerInfo.getVehicle().isObserver
        super(TrainingEntity, self).prb_onPlayerStateChanged(pID, roster)

    def changeSettings(self, ctx, callback=None):
        """
        Sets training settings
        Args:
            ctx: settings request context
            callback: operation callback
        """
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

    def changeUserObserverStatus(self, ctx, callback=None):
        """
        Sets player as observer/not observer
        Args:
            ctx: observer request context
            callback: operation callback
        """
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
        """
        Changes training VOIP settings
        Args:
            ctx: VOIP settings request context
            callback: operation callback
        """
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

    def _createActionsValidator(self):
        return TrainingActionsValidator(self)

    def __enterTrainingRoom(self, isInitial=False):
        """
        Routine must be invoked to enter training room as player
        """
        if self.storage.isObserver:
            self.changeUserObserverStatus(SetPlayerObserverStateCtx(True, True, isInitial=isInitial, waitingID='prebattle/change_user_status'), self.__onPlayerReady)
        else:
            self.setPlayerState(SetPlayerStateCtx(True, isInitial=isInitial, waitingID='prebattle/player_ready'), self.__onPlayerReady)

    def __onPlayerReady(self, result):
        """
        Callback for player set ready opertaion
        Args:
            result: was operation successful
        """
        if result:
            g_eventDispatcher.loadTrainingRoom()
        else:
            g_eventDispatcher.addTrainingToCarousel(False)
            g_eventDispatcher.loadHangar()

    def __onSettingChanged(self, code, record='', callback=None):
        """
        Listener for training settings update
        Args:
            code: result code
            record: record name that was changed
            callback: operation's callback
        """
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
        """
        Listener for view load event
        """
        self.setPlayerState(SetPlayerStateCtx(False, waitingID='prebattle/player_not_ready'))
