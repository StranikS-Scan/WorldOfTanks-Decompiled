# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/event_battle_mode_selector_item.py
import typing
from gui.battle_pass.battle_pass_helpers import getFormattedTimeLeft
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_performance_model import PerformanceRiskEnum
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from gui.impl.lobby.mode_selector.tooltips.event_battle_calendar_tooltip import EventBattleCalendarTooltip
from gui.impl.pub import ToolTipWindow
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.utils import SelectorBattleTypesUtils
from gui.shared.utils.performance_analyzer import PerformanceGroup
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEventBattlesController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel
PERFORMANCE_MAP = {PerformanceGroup.LOW_RISK: PerformanceRiskEnum.LOWRISK,
 PerformanceGroup.MEDIUM_RISK: PerformanceRiskEnum.MEDIUMRISK,
 PerformanceGroup.HIGH_RISK: PerformanceRiskEnum.HIGHRISK}

class EventBattleModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    __eventBattleCtrl = dependency.descriptor(IEventBattlesController)

    @property
    def hasExtendedCalendarTooltip(self):
        return True

    def getExtendedCalendarTooltip(self, parentWindow, event=None):
        window = ToolTipWindow(event, EventBattleCalendarTooltip(), parentWindow)
        window.load()
        window.move(event.mouse.positionX, event.mouse.positionY)
        return window

    def _onInitializing(self):
        super(EventBattleModeSelectorItem, self)._onInitializing()
        self.__eventBattleCtrl.onPrimeTimeStatusUpdated += self.__onPrimeTimeStatusUpdate
        self.__eventBattleCtrl.onCompleteActivePhase += self.__onCompleteActivePhase
        self.__fillViewModel()

    def _onDisposing(self):
        self.__eventBattleCtrl.onPrimeTimeStatusUpdated -= self.__onPrimeTimeStatusUpdate
        self.__eventBattleCtrl.onCompleteActivePhase -= self.__onCompleteActivePhase
        super(EventBattleModeSelectorItem, self)._onDisposing()

    def __onCompleteActivePhase(self):
        self.onCardChange()

    def __onPrimeTimeStatusUpdate(self, *_):
        if self.__eventBattleCtrl.isAvailable():
            self.__fillViewModel()
        else:
            self.onCardChange()

    def __getSeasonTimeLeft(self):
        progressCtrl = self.__eventBattleCtrl.getHWProgressCtrl()
        if progressCtrl:
            phases = progressCtrl.phasesHalloween
            regularPhases = phases.getPhasesByType(phaseType=1)
            regularPhasesCount = len(regularPhases)
            lastRugularPhase = regularPhases[-1] if regularPhasesCount > 0 else None
            return getFormattedTimeLeft(max(0, lastRugularPhase.getFinishTime() - time_utils.getServerUTCTime()))
        else:
            return ''

    def __fillViewModel(self):
        if self.viewModel is None:
            return
        else:
            self._addReward(ModeSelectorRewardID.HW22_CREW)
            self._addReward(ModeSelectorRewardID.STYLE2D)
            with self.viewModel.transaction() as vm:
                vm.setTimeLeft(self.__getSeasonTimeLeft())
                vm.performance.setShowPerfRisk(True)
                vm.performance.setPerformanceRisk(PERFORMANCE_MAP.get(self.__eventBattleCtrl.getPerformanceGroup(), PerformanceRiskEnum.LOWRISK))
                vm.setIsNew(not SelectorBattleTypesUtils.isKnownBattleType(PREBATTLE_ACTION_NAME.EVENT_BATTLE))
            return

    def __getCurrentSeasonDate(self):
        currentSeason = self.__eventBattleCtrl.getCurrentSeason()
        if currentSeason is not None:
            currentSeason.getCycleEndDate()
            return self.__getDate(currentSeason.getEndDate())
        else:
            return ''

    def __getDate(self, date):
        timeStamp = time_utils.makeLocalServerTime(date)
        return backport.getShortDateFormat(timeStamp)
