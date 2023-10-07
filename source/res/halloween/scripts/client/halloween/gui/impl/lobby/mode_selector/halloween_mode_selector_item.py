# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/mode_selector/halloween_mode_selector_item.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from enum import Enum
import typing
from gui.battle_pass.battle_pass_helpers import getFormattedTimeLeft
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_performance_model import PerformanceRiskEnum
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.tooltips.event_battle_calendar_tooltip import EventBattleCalendarTooltip
from gui.impl.pub import ToolTipWindow
from halloween.gui.halloween_gui_constants import PREBATTLE_ACTION_NAME
from gui.shared.utils import SelectorBattleTypesUtils
from gui.shared.utils.performance_analyzer import PerformanceGroup
from helpers import dependency, time_utils
from skeletons.gui.game_control import IHalloweenController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel
PERFORMANCE_MAP = {PerformanceGroup.LOW_RISK: PerformanceRiskEnum.LOWRISK,
 PerformanceGroup.MEDIUM_RISK: PerformanceRiskEnum.MEDIUMRISK,
 PerformanceGroup.HIGH_RISK: PerformanceRiskEnum.HIGHRISK}

class _ModeSelectorRewardID(Enum):
    CREW = 'halloweenCrew'
    STYLE2D = 'style2d'


class HalloweenModeSelectorItem(ModeSelectorLegacyItem):
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.HALLOWEEN
    _hwController = dependency.descriptor(IHalloweenController)

    @property
    def hasExtendedCalendarTooltip(self):
        return True

    def getExtendedCalendarTooltip(self, parentWindow, event=None):
        window = ToolTipWindow(event, EventBattleCalendarTooltip(), parentWindow)
        window.load()
        window.move(event.mouse.positionX, event.mouse.positionY)
        return window

    def _onInitializing(self):
        super(HalloweenModeSelectorItem, self)._onInitializing()
        self._hwController.onPrimeTimeStatusUpdated += self.__onPrimeTimeStatusUpdate
        self._hwController.onCompleteActivePhase += self.__onCompleteActivePhase
        if self._hwController.isAvailable():
            self.__fillViewModel()

    def _onDisposing(self):
        self._hwController.onPrimeTimeStatusUpdated -= self.__onPrimeTimeStatusUpdate
        self._hwController.onCompleteActivePhase -= self.__onCompleteActivePhase
        super(HalloweenModeSelectorItem, self)._onDisposing()

    def __onCompleteActivePhase(self):
        self.onCardChange()

    def __onPrimeTimeStatusUpdate(self, *_):
        if self._hwController.isAvailable():
            self.__fillViewModel()
        else:
            self.onCardChange()

    def __getSeasonTimeLeft(self):
        if self._hwController:
            phases = self._hwController.phases
            regularPhases = phases.getPhasesByType(phaseType=1)
            regularPhasesCount = len(regularPhases)
            lastRugularPhase = regularPhases[-1] if regularPhasesCount > 0 else None
            if lastRugularPhase is None:
                return ''
            return getFormattedTimeLeft(max(0, lastRugularPhase.getFinishTime() - time_utils.getServerUTCTime()))
        else:
            return ''

    def __fillViewModel(self):
        if self.viewModel is None:
            return
        else:
            self._addReward(_ModeSelectorRewardID.CREW)
            self._addReward(_ModeSelectorRewardID.STYLE2D)
            with self.viewModel.transaction() as vm:
                vm.setTimeLeft(self.__getSeasonTimeLeft())
                vm.performance.setShowPerfRisk(True)
                vm.performance.setPerformanceRisk(PERFORMANCE_MAP.get(self._hwController.getPerformanceGroup(), PerformanceRiskEnum.LOWRISK))
                vm.setIsNew(not SelectorBattleTypesUtils.isKnownBattleType(PREBATTLE_ACTION_NAME.HALLOWEEN_BATTLE))
            return

    def __getCurrentSeasonDate(self):
        currentSeason = self._hwController.getCurrentSeason()
        if currentSeason is not None:
            currentSeason.getCycleEndDate()
            return self.__getDate(currentSeason.getEndDate())
        else:
            return ''

    def __getDate(self, date):
        timeStamp = time_utils.makeLocalServerTime(date)
        return backport.getShortDateFormat(timeStamp)
