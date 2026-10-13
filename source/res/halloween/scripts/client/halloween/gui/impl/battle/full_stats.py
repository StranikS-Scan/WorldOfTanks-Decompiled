# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/battle/full_stats.py
from __future__ import absolute_import
from HWArenaInfoBossHealthBarComponent import getArenaInfoBossHealthBarComponent
from HWArenaPhasesComponent import HWArenaPhasesComponent
from HWTeamInfoStatsComponent import HWTeamInfoStatsComponent
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.battle_control import avatar_getter
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from halloween.gui.game_control.halloween_anomalies_controller import AnomalyData
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from halloween.gui.impl.gen.view_models.views.battle.full_stats_view_model import FullStatsViewModel
from halloween.gui.impl.gen.view_models.views.common.anomaly_model import AnomalyModel, AnomalyType
from halloween.gui.impl.lobby.widgets.event_stats import TeamStats
from halloween.skeletons.halloween_anomalies_controller import IHalloweenAnomaliesController
from halloween_common.halloween_constants import ARENA_BONUS_TYPE_TO_LEVEL
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class TabScreen(ViewImpl):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _hwAnomaliesCtrl = dependency.descriptor(IHalloweenAnomaliesController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.halloween.mono.battle.tab_screen(), model=FullStatsViewModel())
        super(TabScreen, self).__init__(settings)
        self.setChildView(resourceID=R.aliases.halloween.shared.TeamStats(), view=TeamStats())
        self._currentGoal = self.battleGUICtrl.currentGoal if self.battleGUICtrl else ''

    def _onLoading(self, *args, **kwargs):
        super(TabScreen, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            self.__updateHeader(model=tx)
            self.__updateBuffs(model=tx)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(TabScreen, self).createToolTipContent(event, contentID)

    @property
    def vehicleStats(self):
        return HWTeamInfoStatsComponent.getInstance()

    @property
    def arenaPhases(self):
        return HWArenaPhasesComponent.getInstance()

    @property
    def battleGUICtrl(self):
        return self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    @property
    def viewModel(self):
        return super(TabScreen, self).getViewModel()

    def _subscribe(self):
        super(TabScreen, self)._subscribe()
        if self.vehicleStats:
            self.vehicleStats.onTeamBuffsUpdated += self.__updateBuffs
        hwBattleGuiCtrl = self.battleGUICtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onPhaseChanged += self.__onPhaseChanged
            hwBattleGuiCtrl.onBattleGoalChanged += self.__onBattleGoalChanged
            hwBattleGuiCtrl.onBossVulnerableChanged += self.__onBossVulnerableChanged
            hwBattleGuiCtrl.onBossHPBarVisibilityChanged += self.__onBossHPBarVisibilityChanged

    def _unsubscribe(self):
        super(TabScreen, self)._unsubscribe()
        if self.vehicleStats:
            self.vehicleStats.onTeamBuffsUpdated -= self.__updateBuffs
        hwBattleGuiCtrl = self.battleGUICtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onPhaseChanged -= self.__onPhaseChanged
            hwBattleGuiCtrl.onBattleGoalChanged -= self.__onBattleGoalChanged
            hwBattleGuiCtrl.onBossVulnerableChanged -= self.__onBossVulnerableChanged
            hwBattleGuiCtrl.onBossHPBarVisibilityChanged -= self.__onBossHPBarVisibilityChanged

    @replaceNoneKwargsModel
    def __updateHeader(self, model=None):
        arena = avatar_getter.getArena()
        if arena:
            model.setDifficultyLevel(ARENA_BONUS_TYPE_TO_LEVEL.get(arena.bonusType, 1))
        phaseNum = self.arenaPhases.activePhase if self.arenaPhases else 1
        healthBarComponent = getArenaInfoBossHealthBarComponent()
        model.setMissionTitle(backport.text(R.strings.halloween_battle.eventStats.activePhase(), num=phaseNum))
        if self.arenaPhases and self.arenaPhases.phasesCount > 0 and self.arenaPhases.phasesCount == self.arenaPhases.activePhase and healthBarComponent and healthBarComponent.isVisible:
            if self.arenaPhases.isBossVulnerable:
                model.setMissionTask(backport.text(R.strings.halloween_battle.battleHint.bossfight_phase_1()))
            else:
                model.setMissionTask(backport.text(R.strings.halloween_battle.battleHint.destroyTheMinions()))
        elif self._currentGoal:
            model.setMissionTask(backport.text(R.strings.halloween_battle.battleHint.dyn(self.__prepareGoal(self._currentGoal))()))
        else:
            model.setMissionTask('')

    @replaceNoneKwargsModel
    def __updateBuffs(self, model=None):
        arenaDP = self._sessionProvider.getArenaDP()
        if not arenaDP:
            return
        anomaliesIDs = self.vehicleStats.getVehicleBuffs(arenaDP.getPlayerVehicleID())
        playerAnomaliesList = model.getPlayerAnomaliesList()
        playerAnomaliesList.clear()
        for anomalyID in anomaliesIDs:
            anomalyData = self._hwAnomaliesCtrl.getAnomalyByID(anomalyID)
            anomalyModel = AnomalyModel()
            anomalyModel.setId(anomalyID)
            anomalyModel.setType(AnomalyType(anomalyData.type))
            playerAnomaliesList.addViewModel(anomalyModel)

        playerAnomaliesList.invalidate()

    def __onPhaseChanged(self):
        self.__updateHeader()

    def __onBattleGoalChanged(self, goalName):
        self._currentGoal = goalName
        self.__updateHeader()

    def __prepareGoal(self, goalName):
        return str(goalName.split('.')[1]) if '.' in goalName else goalName

    def __onBossVulnerableChanged(self, isBossVulnerable):
        self.__updateHeader()

    def __onBossHPBarVisibilityChanged(self, isBossHPBarVisible):
        self.__updateHeader()


class FullEventStatsWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(FullEventStatsWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW | WindowFlags.WINDOW_MODALITY_MASK, content=TabScreen(), layer=WindowLayer.OVERLAY, parent=parent)
