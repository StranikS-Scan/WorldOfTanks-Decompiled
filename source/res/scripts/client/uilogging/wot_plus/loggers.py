# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/wot_plus/loggers.py
from enum import Enum
import logging
from typing import TYPE_CHECKING
from constants import WoTPlusBonusType
from renewable_subscription_common.settings_constants import WotPlusState
from uilogging.base.logger import MetricsLogger
from uilogging.wot_plus.logging_constants import FEATURE, WotPlusLogActions, MIN_VIEW_TIME, RewardScreenTooltips, WotPlusKeys, HeaderItemState
from wotdecorators import noexcept
if TYPE_CHECKING:
    from typing import Optional
    from uilogging.types import ParentScreenType, ItemType
    from uilogging.wot_plus.logging_constants import WotPlusInfoPageSource, InfoPageInfo
_logger = logging.getLogger(__name__)
BONUS_NAME_TO_ITEM_MAP = {WoTPlusBonusType.EXCLUDED_MAP: RewardScreenTooltips.EXCLUDED_MAP,
 WoTPlusBonusType.EXCLUSIVE_VEHICLE: RewardScreenTooltips.EXCLUSIVE_VEHICLE,
 WoTPlusBonusType.FREE_EQUIPMENT_DEMOUNTING: RewardScreenTooltips.FREE_EQUIPMENT_MOVEMENT,
 WoTPlusBonusType.GOLD_BANK: RewardScreenTooltips.GOLD_RESERVE,
 WoTPlusBonusType.IDLE_CREW_XP: RewardScreenTooltips.PASSIVE_CREW_XP}
WOT_PLUS_STATE_TO_LOG_STATE_MAP = {WotPlusState.ACTIVE: HeaderItemState.ACTIVE,
 WotPlusState.INACTIVE: HeaderItemState.INACTIVE,
 WotPlusState.CANCELLED: HeaderItemState.SUSPENDED}

class WotPlusViewLogger(MetricsLogger):
    __slots__ = ('_viewParent', '_item')

    def __init__(self, parent, item):
        super(WotPlusViewLogger, self).__init__(FEATURE)
        self._item = item
        self._viewParent = parent

    def onViewInitialize(self):
        self.startAction(action=WotPlusLogActions.VIEWED)

    @noexcept
    def onViewFinalize(self, itemState=None):
        self.stopAction(action=WotPlusLogActions.VIEWED, item=self._item, parentScreen=self._viewParent, timeLimit=MIN_VIEW_TIME, itemState=itemState)


class WotPlusEventLogger(MetricsLogger):
    __slots__ = ('_eventParent',)

    def __init__(self, parent):
        super(WotPlusEventLogger, self).__init__(FEATURE)
        self._eventParent = parent

    def logCloseEvent(self):
        self.log(action=WotPlusLogActions.CLOSE, item=WotPlusKeys.CLOSE_BUTTON, parentScreen=self._eventParent)

    def logClickEvent(self, item):
        self.log(action=WotPlusLogActions.CLICK, item=item, parentScreen=self._eventParent)


class WotPlusInfoPageLogger(MetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(WotPlusInfoPageLogger, self).__init__(FEATURE)

    @noexcept
    def logInfoPage(self, source):
        info = source.value
        self.log(action=WotPlusLogActions.CLICK, item=info.item, parentScreen=info.parent_screen)


class WotPlusRewardScreenLogger(WotPlusViewLogger):
    __slots__ = ()

    def __init__(self):
        super(WotPlusRewardScreenLogger, self).__init__(WotPlusKeys.HANGAR, WotPlusKeys.REWARD_SCREEN)

    def logCloseEvent(self):
        self.log(action=WotPlusLogActions.CLOSE, item=WotPlusKeys.CLOSE_BUTTON, parentScreen=self._item)


class WotPlusRewardTooltipLogger(WotPlusViewLogger):

    def __init__(self, parent, bonusName):
        item = BONUS_NAME_TO_ITEM_MAP.get(bonusName)
        super(WotPlusRewardTooltipLogger, self).__init__(parent, item)


class WotPlusHeaderLogger(MetricsLogger):

    def __init__(self):
        super(WotPlusHeaderLogger, self).__init__(FEATURE)

    @noexcept
    def logClickEvent(self, state):
        self.log(action=WotPlusLogActions.CLICK, item=WotPlusKeys.HEADER_TOOLTIP, parentScreen=WotPlusKeys.HANGAR, itemState=WOT_PLUS_STATE_TO_LOG_STATE_MAP[state])


class WotPlusHeaderTooltipLogger(WotPlusViewLogger):

    def __init__(self):
        super(WotPlusHeaderTooltipLogger, self).__init__(WotPlusKeys.HANGAR, WotPlusKeys.HEADER_TOOLTIP)

    @noexcept
    def onViewFinalize(self, itemState):
        return super(WotPlusHeaderTooltipLogger, self).onViewFinalize(WOT_PLUS_STATE_TO_LOG_STATE_MAP[itemState])
