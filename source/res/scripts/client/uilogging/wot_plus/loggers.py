# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/wot_plus/loggers.py
from enum import Enum
import logging
from typing import TYPE_CHECKING
from constants import WoTPlusBonusType, PREMIUM_TYPE
from helpers import dependency
from renewable_subscription_common.settings_constants import WotPlusState
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.shared import IItemsCache
from uilogging.base.logger import MetricsLogger
from uilogging.wot_plus.logging_constants import FEATURE, WotPlusLogActions, MIN_VIEW_TIME, RewardScreenTooltips, WotPlusKeys, WotPlusStateStr, HeaderAdditionalData, NotificationAdditionalData, AccountDashboardFeature, PremiumAccountStateStr, SubscriptionStateMixinKeys
from wotdecorators import noexcept
if TYPE_CHECKING:
    from typing import Optional
    from uilogging.types import ParentScreenType, ItemType
    from uilogging.wot_plus.logging_constants import WotPlusInfoPageSource, InfoPageInfo, SubscriptionPageKeys, ReservesKeys
_logger = logging.getLogger(__name__)
BONUS_NAME_TO_ITEM_MAP = {WoTPlusBonusType.EXCLUDED_MAP: RewardScreenTooltips.EXCLUDED_MAP,
 WoTPlusBonusType.EXCLUSIVE_VEHICLE: RewardScreenTooltips.EXCLUSIVE_VEHICLE,
 WoTPlusBonusType.FREE_EQUIPMENT_DEMOUNTING: RewardScreenTooltips.FREE_EQUIPMENT_MOVEMENT,
 WoTPlusBonusType.GOLD_BANK: RewardScreenTooltips.GOLD_RESERVE,
 WoTPlusBonusType.IDLE_CREW_XP: RewardScreenTooltips.PASSIVE_CREW_XP,
 WoTPlusBonusType.ATTENDANCE_REWARD: RewardScreenTooltips.ATTENDANCE_REWARD,
 WoTPlusBonusType.TEAM_CREDITS_BONUS: RewardScreenTooltips.TEAM_CREDITS_BONUS,
 WoTPlusBonusType.DAILY_QUESTS_REWARDS: RewardScreenTooltips.DAILY_QUESTS_REWARDS}
WOT_PLUS_STATE_TO_LOG_STATE_MAP = {WotPlusState.ACTIVE: WotPlusStateStr.ACTIVE,
 WotPlusState.INACTIVE: WotPlusStateStr.INACTIVE,
 WotPlusState.TRIAL: WotPlusStateStr.TRIAL,
 WotPlusState.CANCELLED: WotPlusStateStr.SUSPENDED,
 WotPlusState.ERROR: WotPlusStateStr.ERROR}

class SubscriptionsStateMixin(object):
    __slots__ = ()
    _itemsCache = dependency.descriptor(IItemsCache)
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)

    @staticmethod
    def _formatState(key, value):
        return '{}:{}'.format(key, value)

    def _getWotPlusStateSerialized(self):
        state = self._wotPlusCtrl.getState()
        return self._formatState(SubscriptionStateMixinKeys.WOT_PLUS.value, WOT_PLUS_STATE_TO_LOG_STATE_MAP[state].value)

    def _getPremiumAccountStateSerialized(self):
        hasPremium = self._itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
        premiumStr = PremiumAccountStateStr.ACTIVE.value if hasPremium else PremiumAccountStateStr.INACTIVE.value
        return self._formatState(SubscriptionStateMixinKeys.PREMIUM.value, premiumStr)

    def getSubscriptionsStatesSerialized(self):
        wotPlusStr = self._getWotPlusStateSerialized()
        paStr = self._getPremiumAccountStateSerialized()
        return ';'.join([wotPlusStr, paStr])


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


class WotPlusViewCloseLogger(WotPlusViewLogger):

    def logCloseEvent(self):
        self.log(action=WotPlusLogActions.CLOSE, item=WotPlusKeys.CLOSE_BUTTON, parentScreen=self._item)


class WotPlusInfoPageLogger(MetricsLogger, SubscriptionsStateMixin):

    def __init__(self):
        super(WotPlusInfoPageLogger, self).__init__(FEATURE)

    @noexcept
    def logInfoPage(self, source, includeSubscriptionInfo=False):
        info = source.value
        self.log(action=WotPlusLogActions.CLICK, item=info.item, parentScreen=info.parent_screen, info=self.getSubscriptionsStatesSerialized() if includeSubscriptionInfo else None)
        return


class WotPlusRewardScreenLogger(WotPlusViewCloseLogger):

    def __init__(self):
        super(WotPlusRewardScreenLogger, self).__init__(WotPlusKeys.HANGAR, WotPlusKeys.REWARD_SCREEN)


class WotPlusRewardTooltipLogger(WotPlusViewLogger):

    def __init__(self, parent, bonusName):
        item = BONUS_NAME_TO_ITEM_MAP.get(bonusName)
        super(WotPlusRewardTooltipLogger, self).__init__(parent, item)


class WotPlusHeaderLogger(MetricsLogger):

    def __init__(self):
        super(WotPlusHeaderLogger, self).__init__(FEATURE)

    @noexcept
    def logClickEvent(self, state, isNewAttendanceReward=False):
        self.log(action=WotPlusLogActions.CLICK, item=WotPlusKeys.HEADER_TOOLTIP, parentScreen=WotPlusKeys.HANGAR, itemState=WOT_PLUS_STATE_TO_LOG_STATE_MAP[state], info=HeaderAdditionalData.NEW_ATTENDANCE_REWARD if isNewAttendanceReward else None)
        return


class WotPlusHeaderTooltipLogger(WotPlusViewLogger):

    def __init__(self):
        super(WotPlusHeaderTooltipLogger, self).__init__(WotPlusKeys.HANGAR, WotPlusKeys.HEADER_TOOLTIP)

    @noexcept
    def onViewFinalize(self, itemState):
        return super(WotPlusHeaderTooltipLogger, self).onViewFinalize(WOT_PLUS_STATE_TO_LOG_STATE_MAP[itemState])


class WotPlusNotificationLogger(MetricsLogger):

    def __init__(self):
        super(WotPlusNotificationLogger, self).__init__(FEATURE)

    @noexcept
    def logDetailsButtonClickEvent(self, notificationType):
        self.log(action=WotPlusLogActions.CLICK, item=WotPlusKeys.DETAILS_BUTTON, parentScreen=WotPlusKeys.NOTIFICATION_CENTER, info=notificationType)


class WotPlusAttendanceRewardScreenLogger(WotPlusViewCloseLogger):

    def __init__(self):
        super(WotPlusAttendanceRewardScreenLogger, self).__init__(WotPlusKeys.HANGAR, WotPlusKeys.ATTENDANCE_REWARD_SCREEN)


class WotPlusAccountDashboardLogger(WotPlusViewCloseLogger, SubscriptionsStateMixin):

    def __init__(self):
        super(WotPlusAccountDashboardLogger, self).__init__(WotPlusKeys.HANGAR, WotPlusKeys.ACCOUNT_DASHBOARD)

    def onViewFinalize(self, itemState=None):
        self.stopAction(action=WotPlusLogActions.VIEWED, item=self._item, parentScreen=self._viewParent, timeLimit=MIN_VIEW_TIME, itemState=itemState, info=self.getSubscriptionsStatesSerialized())


class WotPlusAccountDashboardWidgetLogger(MetricsLogger, SubscriptionsStateMixin):
    __slots__ = ()

    def __init__(self):
        super(WotPlusAccountDashboardWidgetLogger, self).__init__(FEATURE)

    @noexcept
    def logWidgetClickEvent(self, widget):
        self.log(action=WotPlusLogActions.CLICK, item=widget, parentScreen=WotPlusKeys.ACCOUNT_DASHBOARD, info=self.getSubscriptionsStatesSerialized())


class WotPlusReservesLogger(WotPlusViewCloseLogger, SubscriptionsStateMixin):

    def __init__(self):
        super(WotPlusReservesLogger, self).__init__(WotPlusKeys.ACCOUNT_DASHBOARD, WotPlusKeys.RESERVE_VIEW)

    def onViewFinalize(self, itemState=None):
        self.stopAction(action=WotPlusLogActions.VIEWED, item=self._item, parentScreen=self._viewParent, timeLimit=MIN_VIEW_TIME, itemState=itemState, info=self.getSubscriptionsStatesSerialized())

    def logClickEvent(self, item):
        self.log(action=WotPlusLogActions.CLICK, item=item, parentScreen=self._item, info=self.getSubscriptionsStatesSerialized())


class WotPlusSubscriptionViewLogger(WotPlusViewCloseLogger, SubscriptionsStateMixin):

    def __init__(self):
        super(WotPlusSubscriptionViewLogger, self).__init__(WotPlusKeys.ACCOUNT_DASHBOARD, WotPlusKeys.SUBSCRIPTION_PAGE)

    def onViewFinalize(self, itemState=None):
        self.stopAction(action=WotPlusLogActions.VIEWED, item=self._item, parentScreen=self._viewParent, timeLimit=MIN_VIEW_TIME, itemState=itemState, info=self.getSubscriptionsStatesSerialized())

    def logClickEvent(self, item):
        self.log(action=WotPlusLogActions.CLICK, item=item, parentScreen=self._item, info=self.getSubscriptionsStatesSerialized())
