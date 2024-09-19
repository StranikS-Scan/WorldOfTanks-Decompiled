# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/battle_result_view.py
from logging import getLogger
import typing
import BigWorld
import SoundGroups
from constants import DEATH_REASON_ALIVE
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.battle_results.br_constants import PlayerTeamResult
from gui.clans.clan_cache import g_clanCache
from gui.impl import backport
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl
from gui.server_events.awards_formatters import AwardsPacker, getDefaultFormattersMap, AWARDS_SIZES
from helpers import dependency
from ids_generators import SequenceIDGenerator
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.lobby_context import ILobbyContext
from story_mode.gui.impl.gen.view_models.views.lobby.battle_result_stat_tooltip_model import StatEnum
from story_mode.gui.impl.gen.view_models.views.lobby.battle_result_view_model import BattleResultViewModel, RewardModel
from story_mode.gui.impl.gen.view_models.views.lobby.progress_level_model import ProgressLevelModel
from story_mode.gui.impl.lobby.battle_result_stat_tooltip import BattleResultStatTooltip
from story_mode.gui.impl.mixins import DestroyWindowOnDisconnectMixin
from story_mode.gui.shared.bonuses_formatters import StoryModeBonusesAwardsComposer, getImgName
from story_mode.gui.shared.event_dispatcher import showCongratulationsWindow
from story_mode.gui.shared.utils import getTasksCount
from story_mode.gui.story_mode_gui_constants import POST_BATTLE_MUSIC_WIN, POST_BATTLE_MUSIC_LOSE
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.skeletons.story_mode_fading_controller import IStoryModeFadingController
from story_mode.uilogging.story_mode.consts import LogButtons
from story_mode.uilogging.story_mode.loggers import PostBattleWindowLogger
from story_mode_common.story_mode_constants import LOGGER_NAME, MissionsDifficulty
from wg_async import wg_async
_logger = getLogger(LOGGER_NAME)

class BattleResultView(ViewImpl):
    __slots__ = ('_uiLogger', '__arenaUniqueId', '__idGen', '__bonusCache')
    _MAX_OBJECTIVES_COUNT = 1
    _MAX_BONUSES_IN_VIEW = 7
    _ICON_OBJECTIVES = 'icon_battle_condition_win'
    _ICON_KILLS = 'icon_battle_condition_kill_vehicles'
    _ICON_DAMAGE = 'icon_battle_condition_damage'
    _ICON_ASSIST = 'icon_battle_condition_assist'
    _ICON_DAMAGE_BLOCKED = 'icon_battle_condition_damage_block'
    _battleResultsService = dependency.descriptor(IBattleResultsService)
    _storyModeCtrl = dependency.descriptor(IStoryModeController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _fadeManager = dependency.descriptor(IStoryModeFadingController)
    _battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self, arenaUniqueId):
        super(BattleResultView, self).__init__(settings=ViewSettings(layoutID=R.views.story_mode.lobby.BattleResultView(), model=BattleResultViewModel()))
        self.__arenaUniqueId = arenaUniqueId
        self.__idGen = SequenceIDGenerator()
        self._uiLogger = PostBattleWindowLogger()
        self.__bonusCache = {}

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
        viewModel = self.getViewModel()
        if viewModel.getIsVictory():
            SoundGroups.g_instance.playSound2D(POST_BATTLE_MUSIC_WIN)
        else:
            SoundGroups.g_instance.playSound2D(POST_BATTLE_MUSIC_LOSE)
        self._uiLogger.logOpen(missionId=viewModel.getMissionId() if viewModel else None, win=viewModel.getIsVictory() if viewModel else False)
        return

    def _finalize(self):
        self._uiLogger.logClose()
        super(BattleResultView, self)._finalize()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs), self.getParentWindow())
                window.load()
                return window
        return super(BattleResultView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.story_mode.lobby.BattleResultStatTooltip():
            stat = event.getArgument('stat', '')
            enumStat = StatEnum(stat)
            return BattleResultStatTooltip(enumStat, self.__getDetailedStatsForStatTooltip(enumStat))
        return super(BattleResultView, self).createToolTipContent(event, contentID)

    def __getDetailedStatsForStatTooltip(self, stat):
        battleResults = self._battleResultsService.getResultsVO(self.__arenaUniqueId)
        if battleResults:
            vehicle = battleResults['vehicle']
            battleResultStat = R.strings.sm_lobby.tooltips.battleResultStat
            if stat == StatEnum.ASSIST:
                return [(vehicle['damageAssisted'], backport.text(battleResultStat.assist.total()))]
            if stat == StatEnum.DAMAGE:
                return [(vehicle['damageDealt'], backport.text(battleResultStat.damage.total()))]
            if stat == StatEnum.ARMOR_USE:
                return [(vehicle['damageBlockedByArmor'], backport.text(battleResultStat.armorUse.blocked()))]
        return []

    def __fillViewModel(self):
        battleResults = self._battleResultsService.getResultsVO(self.__arenaUniqueId)
        with self.getViewModel().transaction() as model:
            rBattleResult = R.strings.sm_lobby.battleResult
            missionId = battleResults['missionId']
            finishResult = battleResults['finishResult']
            model.setMissionId(missionId)
            mission = self._storyModeCtrl.missions.getMission(missionId)
            if mission is None:
                _logger.error('Mission ID=%s not exists', missionId)
                return
            model.setIsDifficult(mission.difficulty == MissionsDifficulty.HARD)
            model.setIsVictory(finishResult == PlayerTeamResult.WIN)
            model.setIsEvent(mission.isEvent)
            model.setTitle(rBattleResult.dyn(PlayerTeamResult.DEFEAT if finishResult == PlayerTeamResult.DRAW else finishResult).title())
            model.setSubTitle(battleResults['finishReason'])
            model.setInfoName(backport.text(rBattleResult.missionName.num(missionId)()))
            model.setInfoDescription(backport.text(rBattleResult.battleDuration(), date=battleResults['arenaDateTime'], duration=battleResults['arenaDuration']))
            model.setVehicleName(backport.text(rBattleResult.vehicleName(), playerName=self._lobbyContext.getPlayerFullName(BigWorld.player().name, clanInfo=g_clanCache.clanInfo), vehicleName=battleResults['vehicleName']))
            model.setPlayerStatus(backport.text(rBattleResult.vehicleState.alive() if battleResults['vehicle']['deathReason'] == DEATH_REASON_ALIVE else rBattleResult.vehicleState.dead()))
            self.__fillProgressLevels(model.missionProgress, model.getProgressLevels(), battleResults)
            self.__fillRewards(model.getRewards())
        return

    def __fillProgressLevels(self, missionProgressModel, progressLevelsModels, battleResults):
        text = R.strings.sm_lobby.battleResult
        progressionInfo = battleResults.get('progressionInfo', {})
        completedTasksCount, tasksToCompleteCount = getTasksCount(progressionInfo)
        missionProgressModel.setTotal(tasksToCompleteCount)
        missionProgressModel.setValue(completedTasksCount)
        missionProgressModel.setIcon(self._ICON_OBJECTIVES)
        missionProgressModel.setName(text.tasksCompleted() if tasksToCompleteCount else text.noTasksToComplete())
        with progressLevelsModels.transaction() as model:
            vehicle = battleResults['vehicle']
            model.addViewModel(self.__createProgressModel(vehicle['kills'], self._ICON_KILLS, text.kills(), StatEnum.KILLS))
            model.addViewModel(self.__createProgressModel(vehicle['damageDealt'], self._ICON_DAMAGE, text.damageDealt(), StatEnum.DAMAGE))
            model.addViewModel(self.__createProgressModel(vehicle['damageAssisted'], self._ICON_ASSIST, text.damageAssisted(), StatEnum.ASSIST))
            model.addViewModel(self.__createProgressModel(vehicle['damageBlockedByArmor'], self._ICON_DAMAGE_BLOCKED, text.damageBlockedByArmor(), StatEnum.ARMOR_USE))

    def __createProgressModel(self, value, icon, name, stat):
        progress = ProgressLevelModel()
        progress.setValue(value)
        progress.setIcon(icon)
        progress.setName(name)
        progress.setStat(stat)
        return progress

    def __fillRewards(self, rewardsModel):
        battleResults = self._battleResultsService.getResultsVO(self.__arenaUniqueId)
        with rewardsModel.transaction() as model:
            formatter = StoryModeBonusesAwardsComposer(self._MAX_BONUSES_IN_VIEW, AwardsPacker(getDefaultFormattersMap()))
            bonusRewards = formatter.getFormattedBonuses(battleResults['rewards'], AWARDS_SIZES.BIG)
            for bonus in bonusRewards:
                tooltipId = '{}'.format(self.__idGen.next())
                self.__bonusCache[tooltipId] = bonus
                rewardItem = RewardModel()
                rewardItem.setName(bonus.bonusName)
                rewardItem.setValue(str(bonus.label))
                rewardItem.setIcon(getImgName(bonus.getImage(AWARDS_SIZES.BIG)))
                rewardItem.setTooltipId(tooltipId)
                if isinstance(bonus.tooltip, int):
                    rewardItem.setTooltipContentId(str(bonus.tooltip))
                model.addViewModel(rewardItem)

    @wg_async
    def __onClose(self):
        yield self._fadeManager.show(WindowLayer.OVERLAY)
        self._uiLogger.logClick(LogButtons.CONTINUE)
        if self._storyModeCtrl.needToShowAward:
            showCongratulationsWindow(isCloseVisible=True, awardData=self._storyModeCtrl.popWaitingToBeShownAwardData())
        self.destroyWindow()
        if not self._storyModeCtrl.needToShowAward:
            yield self._fadeManager.hide(WindowLayer.OVERLAY)


class BattleResultWindow(DestroyWindowOnDisconnectMixin, WindowImpl):
    __slots__ = ()

    def __init__(self, arenaUniqueId):
        super(BattleResultWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW, content=BattleResultView(arenaUniqueId))
