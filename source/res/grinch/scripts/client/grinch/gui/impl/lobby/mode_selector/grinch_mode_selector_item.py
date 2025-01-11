# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/lobby/mode_selector/grinch_mode_selector_item.py
from typing import TYPE_CHECKING
from grinch.gui.grinch_gui_constants import PREBATTLE_ACTION_NAME
from grinch.gui.shared.utils.performance_analyzer import PerformanceGroup, PerformanceAnalyzerMixin
from grinch.skeletons.battle_controller import IGrinchController
from grinch_common.grinch_constants import GrinchModeSelectorRewardID
from grinch_progression.gui.shared.event_dispatcher import showGameBoardProgressionInfoView
from grinch_progression.skeletons.game_controller import IGrinchProgressionController
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.date_time_formats import DateTimeFormatsEnum
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_performance_model import PerformanceRiskEnum
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.periodic_battles.models import PeriodType
from gui.shared.formatters.date_time import getRegionalDateTime
from gui.shared.utils import SelectorBattleTypesUtils
from helpers import dependency
if TYPE_CHECKING:
    from gui.periodic_battles.models import PeriodInfo
PERFORMANCE_MAP = {PerformanceGroup.LOW_RISK: PerformanceRiskEnum.LOWRISK,
 PerformanceGroup.MEDIUM_RISK: PerformanceRiskEnum.MEDIUMRISK,
 PerformanceGroup.HIGH_RISK: PerformanceRiskEnum.HIGHRISK}

class GrinchModeSelectorItem(ModeSelectorLegacyItem, PerformanceAnalyzerMixin):
    __slots__ = ()
    _grinchCtrl = dependency.descriptor(IGrinchController)
    _grinchProgressionCtrl = dependency.descriptor(IGrinchProgressionController)

    @property
    def viewModel(self):
        return self._viewModel

    @property
    def isSelectable(self):
        return self._grinchCtrl.isEnabled()

    @property
    def isVisible(self):
        periodInfo = self._grinchCtrl.getPeriodInfo()
        return self._grinchCtrl.isEnabled() and periodInfo.periodType not in (PeriodType.BEFORE_SEASON, PeriodType.UNDEFINED)

    def handleClick(self):
        self._grinchCtrl.selectMode()

    def handleInfoPageClick(self):
        showGameBoardProgressionInfoView()

    def _isInfoIconVisible(self):
        return True

    def _getIsDisabled(self):
        return self._grinchCtrl.isFrozen()

    def _setMoreDescription(self, model, periodInfo):
        dateFrom = None
        dateTo = None
        if periodInfo.periodType == PeriodType.BETWEEN_SEASONS:
            nearestTimeCycle = self._grinchCtrl.getNextSeason().getNextByTimeCycle(periodInfo.now)
            dateFrom = nearestTimeCycle.startDate
            dateTo = nearestTimeCycle.endDate
        elif periodInfo.periodType == PeriodType.AVAILABLE:
            dateFrom = periodInfo.seasonBorderLeft.timestamp
            dateTo = periodInfo.seasonBorderRight.timestamp
        model.setDescription('')
        if dateFrom and dateTo:
            model.setDescription(backport.text(R.strings.mode_selector.mode.grinch.description(), dateFrom=getRegionalDateTime(dateFrom, DateTimeFormatsEnum.DAYMONTHFULLTIME), dateTo=getRegionalDateTime(dateTo, DateTimeFormatsEnum.DAYMONTHFULLTIME)))
        return

    def _onInitializing(self):
        super(GrinchModeSelectorItem, self)._onInitializing()
        periodInfo = self._grinchCtrl.getPeriodInfo()
        with self.viewModel.transaction() as tx:
            tx.setName(backport.text(R.strings.mode_selector.mode.grinch.title()))
            if periodInfo.periodType == PeriodType.AFTER_SEASON:
                tx.setDescription(backport.text(R.strings.mode_selector.mode.grinch.postEventDescription()))
            else:
                curChapterID = self._grinchProgressionCtrl.getCurrentChapter()
                tx.setEventName(backport.text(R.strings.mode_selector.mode.grinch.chapter(), chapter=curChapterID))
                self._setMoreDescription(tx, periodInfo)
            tx.setIsNew(not SelectorBattleTypesUtils.isKnownBattleType(PREBATTLE_ACTION_NAME.GRINCH))
            tx.performance.setShowPerfRisk(True)
            tx.performance.setPerformanceRisk(PERFORMANCE_MAP.get(self.getPerformanceGroup(), PerformanceRiskEnum.LOWRISK))
            if self._grinchCtrl.isAvailable():
                self._addReward(GrinchModeSelectorRewardID.ATTACHMENT_3D)
