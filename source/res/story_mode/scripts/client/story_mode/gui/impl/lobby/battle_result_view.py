# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/battle_result_view.py
import typing
from logging import getLogger
import BigWorld
import SoundGroups
from constants import DEATH_REASON_ALIVE
from frameworks.wulf import ViewSettings, WindowFlags
from gui.battle_results.settings import PLAYER_TEAM_RESULT
from gui.clans.clan_cache import g_clanCache
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.lobby_context import ILobbyContext
from story_mode.gui.impl.gen.view_models.views.lobby.battle_result_view_model import BattleResultViewModel
from story_mode.gui.impl.gen.view_models.views.lobby.progress_level_model import ProgressLevelModel
from story_mode.gui.impl.mixins import DestroyWindowOnDisconnectMixin
from story_mode.gui.shared.event_dispatcher import showCongratulationsWindow
from story_mode.gui.story_mode_gui_constants import POST_BATTLE_MUSIC
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode_common.story_mode_constants import LOGGER_NAME
from story_mode.uilogging.story_mode.consts import LogButtons
from story_mode.uilogging.story_mode.loggers import PostBattleWindowLogger
_logger = getLogger(LOGGER_NAME)

class BattleResultView(ViewImpl):
    __slots__ = ('_uiLogger', '__arenaUniqueId')
    _MAX_OBJECTIVES_COUNT = 1
    _ICON_OBJECTIVES = 'icon_battle_condition_win'
    _ICON_KILLS = 'icon_battle_condition_kill_vehicles'
    _ICON_DAMAGE = 'icon_battle_condition_damage'
    _ICON_ASSIST = 'icon_battle_condition_assist'
    _ICON_DAMAGE_BLOCKED = 'icon_battle_condition_damage_block'
    _battleResultsService = dependency.descriptor(IBattleResultsService)
    _storyModeCtrl = dependency.descriptor(IStoryModeController)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, arenaUniqueId):
        super(BattleResultView, self).__init__(settings=ViewSettings(layoutID=R.views.story_mode.lobby.BattleResultView(), model=BattleResultViewModel()))
        self.__arenaUniqueId = arenaUniqueId
        self._uiLogger = PostBattleWindowLogger()

    def _getEvents(self):
        viewModel = self.getViewModel()
        return ((viewModel.onQuit, self.__onClose), (viewModel.onContinue, self.__onClose))

    def _onLoading(self, *args, **kwargs):
        super(BattleResultView, self)._onLoading(*args, **kwargs)
        if self._battleResultsService.areResultsPosted(self.__arenaUniqueId):
            self.__fillViewModel()
        else:
            _logger.error('Battle results missing for arena[uniqueId=%s]', self.__arenaUniqueId)

    def _onLoaded(self, *args, **kwargs):
        super(BattleResultView, self)._onLoaded(*args, **kwargs)
        SoundGroups.g_instance.playSound2D(POST_BATTLE_MUSIC)
        viewModel = self.getViewModel()
        self._uiLogger.logOpen(missionId=viewModel.getMissionId() if viewModel else None, win=viewModel.getIsVictory() if viewModel else False)
        return

    def _finalize(self):
        self._uiLogger.logClose()
        super(BattleResultView, self)._finalize()

    def __fillViewModel(self):
        battleResults = self._battleResultsService.getResultsVO(self.__arenaUniqueId)
        with self.getViewModel().transaction() as model:
            rBattleResult = R.strings.sm_lobby.battleResult
            missionId = battleResults['missionId']
            finishResult = battleResults['finishResult']
            model.setMissionId(missionId)
            model.setIsVictory(finishResult == PLAYER_TEAM_RESULT.WIN)
            model.setTitle(rBattleResult.dyn(PLAYER_TEAM_RESULT.DEFEAT if finishResult == PLAYER_TEAM_RESULT.DRAW else finishResult).title())
            model.setSubTitle(battleResults['finishReason'])
            model.setInfoName(backport.text(rBattleResult.missionName.num(missionId)()))
            model.setInfoDescription(backport.text(rBattleResult.battleDuration(), date=battleResults['arenaDateTime'], duration=battleResults['arenaDuration']))
            model.setVehicleName(backport.text(rBattleResult.vehicleName(), playerName=self._lobbyContext.getPlayerFullName(BigWorld.player().name, clanInfo=g_clanCache.clanInfo), vehicleName=battleResults['vehicleName']))
            model.setPlayerStatus(backport.text(rBattleResult.vehicleState.alive() if battleResults['vehicle']['deathReason'] == DEATH_REASON_ALIVE else rBattleResult.vehicleState.dead()))
            self.__fillProgressLevels(model.missionProgress, model.getProgressLevels(), battleResults)

    def __fillProgressLevels(self, missionProgressModel, progressLevelsModels, battleResults):
        text = R.strings.sm_lobby.battleResult
        missionProgressModel.setValue(self._MAX_OBJECTIVES_COUNT if battleResults['finishResult'] == PLAYER_TEAM_RESULT.WIN else 0)
        missionProgressModel.setIcon(self._ICON_OBJECTIVES)
        missionProgressModel.setName(text.operationsCompleted())
        missionProgressModel.setTotal(self._MAX_OBJECTIVES_COUNT)
        with progressLevelsModels.transaction() as model:
            vehicle = battleResults['vehicle']
            model.addViewModel(self.__createProgressModel(vehicle['kills'], self._ICON_KILLS, text.kills()))
            model.addViewModel(self.__createProgressModel(vehicle['damageDealt'], self._ICON_DAMAGE, text.damageDealt()))
            model.addViewModel(self.__createProgressModel(vehicle['damageAssisted'], self._ICON_ASSIST, text.damageAssisted()))
            model.addViewModel(self.__createProgressModel(vehicle['damageBlockedByArmor'], self._ICON_DAMAGE_BLOCKED, text.damageBlockedByArmor()))

    def __createProgressModel(self, value, icon, name):
        progress = ProgressLevelModel()
        progress.setValue(value)
        progress.setIcon(icon)
        progress.setName(name)
        return progress

    def __onClose(self):
        self._uiLogger.logClick(LogButtons.CONTINUE)
        if self._storyModeCtrl.needToShowAward:
            showCongratulationsWindow(isCloseVisible=True)
        self.destroyWindow()


class BattleResultWindow(DestroyWindowOnDisconnectMixin, WindowImpl):
    __slots__ = ()

    def __init__(self, arenaUniqueId):
        super(BattleResultWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BattleResultView(arenaUniqueId))
