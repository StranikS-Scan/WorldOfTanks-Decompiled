# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/lobby/banner_entry_point/grinch_banner_entry_point.py
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from grinch.gui.grinch_gui_constants import PREBATTLE_ACTION_NAME
from grinch.gui.impl.gen.view_models.views.lobby.banner_entry_point.event_banner_tooltip import EventBannerTooltipView
from grinch.gui.impl.gen.view_models.views.lobby.banner_entry_point.grinch_banner_entry_point_model import GrinchBannerEntryPointModel, PerformanceRiskEnum, State
from grinch.gui.impl.lobby.mode_selector.grinch_mode_selector_item import PERFORMANCE_MAP
from grinch.gui.shared.utils.performance_analyzer import PerformanceAnalyzerMixin
from grinch.skeletons.battle_controller import IGrinchController
from grinch_progression.skeletons.game_controller import IGrinchProgressionController
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.periodic_battles.models import PeriodType
from gui.shared.utils import SelectorBattleTypesUtils
from helpers import dependency, time_utils
from shared_utils import nextTick
if typing.TYPE_CHECKING:
    from grinch.gui.game_control.grinch_controller import GrinchController
    from typing import Tuple
    from frameworks.wulf import View, ViewEvent
DISABLED_STATES = {PeriodType.UNDEFINED,
 PeriodType.NOT_AVAILABLE,
 PeriodType.ALL_NOT_AVAILABLE,
 PeriodType.STANDALONE_NOT_AVAILABLE,
 PeriodType.NOT_AVAILABLE_END,
 PeriodType.ALL_NOT_AVAILABLE_END,
 PeriodType.STANDALONE_NOT_AVAILABLE_END}

@dependency.replace_none_kwargs(grinchCtrl=IGrinchController)
def isGrinchBannerEntryPointAvailable(grinchCtrl=None):
    return grinchCtrl.isEnabled()


class GrinchBannerEntryPoint(ViewImpl, PerformanceAnalyzerMixin):
    __slots__ = ('__isSingle',)
    __END_NOTIFICATIONS_PERIOD_LENGTH = time_utils.ONE_DAY
    _grinchCtrl = dependency.descriptor(IGrinchController)
    _grinchProgressionCtrl = dependency.descriptor(IGrinchProgressionController)

    def __init__(self):
        settings = ViewSettings(R.views.grinch.lobby.banner_entry_point.GrinchBannerEntryPoint())
        settings.flags = ViewFlags.VIEW
        settings.model = GrinchBannerEntryPointModel()
        self.__isSingle = True
        super(GrinchBannerEntryPoint, self).__init__(settings)

    def setIsSingle(self, value):
        self.__isSingle = value

    @property
    def viewModel(self):
        return super(GrinchBannerEntryPoint, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onOpen, self.__onOpen), (self._grinchCtrl.onPrimeTimeStatusUpdated, self.__onStatusUpdated))

    def _onLoading(self, *args, **kwargs):
        super(GrinchBannerEntryPoint, self)._onLoading(*args, **kwargs)
        self.__updateState()

    def __updateState(self):
        if isGrinchBannerEntryPointAvailable():
            with self.viewModel.transaction() as tx:
                state, actualTime = self.__getPeriodStateAndActualTime()
                tx.setState(state)
                tx.setTimestamp(actualTime or 0)
                tx.setIsSingle(self.__isSingle)
                tx.setPerformanceRisk(PERFORMANCE_MAP.get(self.getPerformanceGroup(), PerformanceRiskEnum.LOWRISK))
                tx.setIsNew(state != State.STARTSOON and not SelectorBattleTypesUtils.isKnownBattleType(PREBATTLE_ACTION_NAME.GRINCH))
                if self._grinchCtrl.getNextSeason():
                    tx.setChapter(self._grinchProgressionCtrl.getNextChapterID())
                tx.setEndTimestamp(0)
                if state == State.ACTIVE:
                    tx.setEndTimestamp(self._grinchProgressionCtrl.getEndEventDate())
        else:
            nextTick(self.destroy)()

    def __getPeriodStateAndActualTime(self):
        periodInfo = self._grinchCtrl.getPeriodInfo()
        if periodInfo.periodType == PeriodType.BEFORE_SEASON:
            return (State.STARTSOON, int(self._grinchProgressionCtrl.getTimeTillSeasonStart()))
        if periodInfo.periodType == PeriodType.BETWEEN_SEASONS:
            nearestTimeCycle = self._grinchCtrl.getNextSeason().getNextByTimeCycle(periodInfo.now)
            return (State.PAUSE, nearestTimeCycle.startDate)
        if periodInfo.periodType == PeriodType.AFTER_SEASON:
            return (State.POSTMORTEM, self._grinchProgressionCtrl.getEndEventDate())
        if not self._grinchCtrl.isAvailable() or not self._grinchCtrl.getCurrentSeason() or periodInfo.periodType in DISABLED_STATES:
            return (State.DISABLED, 0)
        startsIn = periodInfo.cycleBorderRight.delta(periodInfo.now)
        return (State.ENDSOON, startsIn) if startsIn < self.__END_NOTIFICATIONS_PERIOD_LENGTH else (State.ACTIVE, startsIn)

    def __onStatusUpdated(self, *_):
        self.__updateState()

    def __onOpen(self):
        periodInfo = self._grinchCtrl.getPeriodInfo()
        if periodInfo.periodType == PeriodType.BEFORE_SEASON:
            return
        self._grinchCtrl.selectMode()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.grinch.lobby.tooltips.EventBannerTooltip():
            performance = PERFORMANCE_MAP.get(self.getPerformanceGroup(), PerformanceRiskEnum.LOWRISK)
            return EventBannerTooltipView(performanceRisk=performance)
        return super(GrinchBannerEntryPoint, self).createToolTipContent(event, contentID)
