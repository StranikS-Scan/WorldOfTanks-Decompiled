# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/mode_selector/items/historical_battles_mode_selector_item.py
from enum import Enum
from gui.impl.gen import R
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.shared.utils.performance_analyzer import PerformanceGroup
from helpers import dependency
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_hb_card_model import ModeSelectorHbCardModel, PerformanceRiskEnum
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.shared.formatters import time_formatters
from helpers import time_utils
PERFORMANCE_MAP = {PerformanceGroup.LOW_RISK: PerformanceRiskEnum.LOWRISK,
 PerformanceGroup.MEDIUM_RISK: PerformanceRiskEnum.MEDIUMRISK,
 PerformanceGroup.HIGH_RISK: PerformanceRiskEnum.HIGHRISK}

class HBModeSelectorRewardID(Enum):
    HB_OTHER = 'hb_other'
    HB_VEHICLE = 'hb_vehicle'


class HistoricalBattlesModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    __gameEventController = dependency.descriptor(IGameEventController)
    _VIEW_MODEL = ModeSelectorHbCardModel
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.HISTORICAL_BATTLES

    def _onInitializing(self):
        super(HistoricalBattlesModeSelectorItem, self)._onInitializing()
        performanceGroup = self.__gameEventController.getPerformanceGroup()
        self.viewModel.setPerformanceRisk(PERFORMANCE_MAP.get(performanceGroup, PerformanceRiskEnum.LOWRISK))
        self.viewModel.setTimeLeft(self.__getSeasonTimeLeft())
        self._addReward(HBModeSelectorRewardID.HB_VEHICLE)
        self._addReward(HBModeSelectorRewardID.HB_OTHER)

    def __getSeasonTimeLeft(self):
        return time_formatters.getTillTimeByResource(max(0, self.__gameEventController.getEventFinishTime() - time_utils.getServerUTCTime()), R.strings.menu.Time.timeLeftShort, removeLeadingZeros=True) if self.__gameEventController is not None else ''
