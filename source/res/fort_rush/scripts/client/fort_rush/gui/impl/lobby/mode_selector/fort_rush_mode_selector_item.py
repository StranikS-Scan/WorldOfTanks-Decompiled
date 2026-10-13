# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/mode_selector/fort_rush_mode_selector_item.py
from __future__ import absolute_import
import typing
from fort_rush.gui.fort_rush_gui_constants import PREBATTLE_ACTION_NAME
from fort_rush.gui.game_control.perfomance_analyzer_controller import PerformanceGroup
from fort_rush.gui.impl.gen.view_models.views.lobby.mode_selector.fort_rush_mode_selector_model import FortRushModeSelectorModel
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from fort_rush.gui.shared.event_dispatcher import showFortRushInfoPage
from gui.shared.utils import SelectorBattleTypesUtils
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from gui.impl.gen.view_models.views.lobby.common.mode_performance_model import PerformanceRiskEnum
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from fort_rush.gui.impl.gen.view_models.views.lobby.mode_selector.fort_rush_mode_selector_model import FortRushModeSelectorWidgetModel
PERFORMANCE_MAP = {PerformanceGroup.LOW_RISK: PerformanceRiskEnum.LOWRISK,
 PerformanceGroup.MEDIUM_RISK: PerformanceRiskEnum.MEDIUMRISK,
 PerformanceGroup.HIGH_RISK: PerformanceRiskEnum.HIGHRISK}

class FortRushModeSelectorItem(ModeSelectorLegacyItem):
    __frCtrl = dependency.descriptor(IFortRushBattleController)
    __itemsCache = dependency.descriptor(IItemsCache)
    _VIEW_MODEL = FortRushModeSelectorModel

    @property
    def viewModel(self):
        return super(FortRushModeSelectorItem, self).viewModel

    @property
    def isSelectable(self):
        return self.__frCtrl.isAvailable()

    @property
    def isVisible(self):
        return self.__frCtrl.isAvailable()

    def _getPositionByModeName(self):
        config = self.__frCtrl.getConfig()
        return (config.modeSelectorCardColumn, config.modeSelectorCardPriority)

    def _onInitializing(self):
        super(FortRushModeSelectorItem, self)._onInitializing()
        self._addReward(ModeSelectorRewardID.OTHER)
        with self.viewModel.transaction() as vm:
            group = self.__frCtrl.getPerformanceGroup()
            vm.performance.setShowPerfRisk(group != PerformanceGroup.LOW_RISK)
            vm.performance.setPerformanceRisk(PERFORMANCE_MAP.get(group, PerformanceRiskEnum.LOWRISK))
            vm.setIsNew(not SelectorBattleTypesUtils.isKnownBattleType(PREBATTLE_ACTION_NAME.FORT_RUSH))
            vm.setIsSelected(self.__frCtrl.isEventPrbActive())
            self._fillProgressionWidget(vm)
        self.__itemsCache.onSyncCompleted += self.__onCacheSyncCompleted

    def _onDisposing(self):
        self.__itemsCache.onSyncCompleted -= self.__onCacheSyncCompleted
        super(FortRushModeSelectorItem, self)._onDisposing()

    def _fillProgressionWidget(self, vm):
        currentPoints, stageTotal = self.__frCtrl.getCurrentStagePoints()
        widget = vm.widget
        widget.setIsEnabled(self.__frCtrl.isWithinActiveTimeframe())
        widget.setCurrentProgress(currentPoints)
        widget.setTotalCount(stageTotal)

    def __onCacheSyncCompleted(self, reason, diff):
        if reason != CACHE_SYNC_REASON.CLIENT_UPDATE:
            return
        with self.viewModel.transaction() as vm:
            self._fillProgressionWidget(vm)

    def _isInfoIconVisible(self):
        return self.__frCtrl.isInfoPageEnabled()

    def handleInfoPageClick(self):
        showFortRushInfoPage()
