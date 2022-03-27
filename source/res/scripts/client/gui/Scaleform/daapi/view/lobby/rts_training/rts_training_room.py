# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rts_training/rts_training_room.py
import ArenaType
from adisp import process
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.trainings import formatters
from gui.Scaleform.daapi.view.lobby.trainings.TrainingRoomBase import TrainingRoomBase
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.BATTLE_TYPES import BATTLE_TYPES
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.legacy.ctx import SetPlayerStateCtx
from gui.prb_control.entities.rts_battles_training.ctx import RtsTrainingSettingsCtx, SetPlayerCommanderStateCtx
from gui.prb_control.settings import PREBATTLE_ROSTER, REQUEST_TYPE, PREBATTLE_SETTING_NAME
from constants import PREBATTLE_ERRORS, PREBATTLE_TYPE, PREBATTLE_MAX_OBSERVERS_IN_TEAM, OBSERVERS_BONUS_TYPES
from gui.shared import events, EVENT_BUS_SCOPE
from gui.impl.gen import R
BATTLE_TYPES_ICONS = {PREBATTLE_TYPE.RTS_TRAINING: BATTLE_TYPES.TRAINING}

class RtsTrainingRoom(TrainingRoomBase):

    def __init__(self, _=None):
        super(RtsTrainingRoom, self).__init__()
        self.__currentPlayerIsOut = False

    @process
    def selectObserver(self, isCommander):
        if not isCommander:
            playersCount = 0
            roster = self.prbEntity.getRosterKey()
            if roster != PREBATTLE_ROSTER.UNKNOWN and roster & PREBATTLE_ROSTER.UNASSIGNED == 0:
                accounts = self.prbEntity.getRosters()[roster]
                for account in accounts:
                    if account.isVehicleSpecified():
                        vehicle = account.getVehicle()
                        if not vehicle.isObserver:
                            playersCount += 1

            playersMaxCount = self.__getPlayersMaxCount()
            if playersCount >= playersMaxCount:
                event = events.CoolDownEvent()
                self.as_startCoolDownObserverS(event.coolDown)
                self.as_setObserverS(True)
                self._showActionErrorMessage(PREBATTLE_ERRORS.PLAYERS_LIMIT)
                return
        result = yield self.prbDispatcher.sendPrbRequest(SetPlayerCommanderStateCtx(isCommander, True, waitingID='prebattle/change_user_status'))
        if not result:
            self.as_setObserverS(False)
            self._showActionErrorMessage()

    def _populate(self):
        if self.prbDispatcher:
            funcState = self.prbDispatcher.getFunctionalState()
            if not funcState.isInLegacy(PREBATTLE_TYPE.RTS_TRAINING):
                g_eventDispatcher.removeTrainingFromCarousel(False)
                return
        super(RtsTrainingRoom, self)._populate()

    def _addListeners(self):
        super(RtsTrainingRoom, self)._addListeners()
        self.addListener(events.TrainingSettingsEvent.UPDATE_RTS_TRAINING_SETTINGS, self._updateRtsTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        super(RtsTrainingRoom, self)._removeListeners()
        self.removeListener(events.TrainingSettingsEvent.UPDATE_RTS_TRAINING_SETTINGS, self._updateRtsTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)

    def onSettingUpdated(self, entity, settingName, settingValue):
        if settingName in (PREBATTLE_SETTING_NAME.ARENA_TYPE_ID, PREBATTLE_SETTING_NAME.LIMITS):
            settings = entity.getSettings()
            if settingName == PREBATTLE_SETTING_NAME.ARENA_TYPE_ID:
                arenaTypeID = settingValue
            else:
                arenaTypeID = settings[PREBATTLE_SETTING_NAME.ARENA_TYPE_ID]
            arenaType = ArenaType.g_cache.get(arenaTypeID)
            self.as_updateMapS(arenaTypeID, arenaType.maxPlayersInTeam * 2, arenaType.name, formatters.getTrainingRoomTitle(arenaType), formatters.getArenaSubTypeString(arenaTypeID), arenaType.description, self.__battleTypeIcon(settings[PREBATTLE_SETTING_NAME.BATTLE_TYPE]))
        elif settingName == PREBATTLE_SETTING_NAME.ROUND_LENGTH:
            self.as_updateTimeoutS(formatters.getRoundLenString(settingValue))
        elif settingName == PREBATTLE_SETTING_NAME.COMMENT:
            self.as_updateCommentS(settingValue)
        elif settingName == PREBATTLE_SETTING_NAME.ARENA_VOIP_CHANNELS:
            self.as_setArenaVoipChannelsS(settingValue)
        self._updateStartButton(entity)

    def showTrainingSettings(self):
        settings = RtsTrainingSettingsCtx()
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(PREBATTLE_ALIASES.RTS_TRAINING_SETTINGS_WINDOW_PY), ctx={'isCreateRequest': False,
         'settings': settings}), scope=EVENT_BUS_SCOPE.LOBBY)

    def onRostersChanged(self, entity, rosters, full):
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 in rosters:
            self.as_setTeam1S(self._makeAccountsData(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1], R.strings.menu.training.info.team1Label()))
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2 in rosters:
            self.as_setTeam2S(self._makeAccountsData(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2], R.strings.menu.training.info.team2Label()))
        if PREBATTLE_ROSTER.UNASSIGNED in rosters:
            self.as_setOtherS(self._makeAccountsData(rosters[PREBATTLE_ROSTER.UNASSIGNED], R.strings.menu.training.info.otherLabel()))
        super(RtsTrainingRoom, self).onRostersChanged(entity, rosters, full)

    def onFocusIn(self, alias):
        LobbySubView.onFocusIn(self, alias)
        self.__currentPlayerEntered()

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        if not self.__currentPlayerIsOut and accountInfo.isCurrentPlayer() and not accountInfo.isReady():
            self.__currentPlayerIsOut = True
        super(RtsTrainingRoom, self).onPlayerStateChanged(entity, roster, accountInfo)

    def _handleSetPrebattleCoolDown(self, event):
        super(RtsTrainingRoom, self)._handleSetPrebattleCoolDown(event)
        if event.requestID is REQUEST_TYPE.SWAP_TEAMS:
            self.as_startCoolDownSwapButtonS(event.coolDown)

    def _closeWindows(self):
        self._closeWindow(PREBATTLE_ALIASES.RTS_TRAINING_SETTINGS_WINDOW_PY)
        self._closeWindow(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY)

    def _showRosters(self, entity, rosters):
        accounts = rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1]
        self.as_setTeam1S(self._makeAccountsData(accounts, R.strings.menu.training.info.team1Label()))
        accounts = rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2]
        self.as_setTeam2S(self._makeAccountsData(accounts, R.strings.menu.training.info.team2Label()))
        accounts = rosters[PREBATTLE_ROSTER.UNASSIGNED]
        self.as_setOtherS(self._makeAccountsData(accounts, R.strings.menu.training.info.otherLabel()))
        super(RtsTrainingRoom, self)._showRosters(entity, rosters)

    def _updateRtsTrainingRoom(self, event):
        self._closeWindow(PREBATTLE_ALIASES.RTS_TRAINING_SETTINGS_WINDOW_PY)
        self.__changeRtsTrainingRoomSettings(event.ctx.get('settings', None))
        return

    @process
    def __changeRtsTrainingRoomSettings(self, settings):
        if settings and settings.areSettingsChanged(self.prbEntity.getSettings()):
            settings.setWaitingID('prebattle/change_settings')
            result = yield self.prbDispatcher.sendPrbRequest(settings)
            if not result:
                self._showActionErrorMessage()

    def __battleTypeIcon(self, prebattleType):
        return BATTLE_TYPES_ICONS.get(prebattleType, BATTLE_TYPES.TRAINING)

    def __getPlayersMaxCount(self):
        playersMaxCount = self.prbEntity.getTeamLimits()['maxCount'][0]
        if self.prbEntity.getSettings()['bonusType'] in OBSERVERS_BONUS_TYPES:
            playersMaxCount -= PREBATTLE_MAX_OBSERVERS_IN_TEAM
        return playersMaxCount

    @process
    def __currentPlayerEntered(self):
        if self.__currentPlayerIsOut:
            if self.prbEntity.storage.isObserver:
                yield self.prbDispatcher.sendPrbRequest(SetPlayerCommanderStateCtx(isCommander=True, isReadyState=True, waitingID='prebattle/change_user_status'))
            else:
                yield self.prbDispatcher.sendPrbRequest(SetPlayerStateCtx(True, waitingID='prebattle/player_ready'))
            self.as_setObserverS(self.prbEntity.storage.isObserver)
            self.__currentPlayerIsOut = False
