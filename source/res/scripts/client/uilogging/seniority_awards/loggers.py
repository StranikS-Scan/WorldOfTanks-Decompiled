# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/seniority_awards/loggers.py
import logging
from typing import TYPE_CHECKING
from uilogging.base.logger import MetricsLogger
from uilogging.constants import LogLevels
from uilogging.seniority_awards.constants import SeniorityAwardsLogActions, SeniorityAwardsLogKeys, SeniorityAwardsLogButtons, SeniorityAwardsLogSpaces, SeniorityAwardsFeatures
from wotdecorators import noexcept
if TYPE_CHECKING:
    from uilogging.types import ParentScreenType
_logger = logging.getLogger(__name__)

class SeniorityAwardsMetricsLogger(MetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(SeniorityAwardsMetricsLogger, self).__init__(SeniorityAwardsFeatures.FEATURE)


class VehicleSelectionErrorNotificationsLogger(MetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(VehicleSelectionErrorNotificationsLogger, self).__init__(SeniorityAwardsFeatures.VEHICLE_SELECTION_FEATURE)

    @noexcept
    def handleTimeoutError(self):
        self.log(action=SeniorityAwardsLogActions.DISPLAYED, item=SeniorityAwardsLogKeys.TIMEOUT_NOTIFICATION_ERROR, parentScreen=SeniorityAwardsLogSpaces.HANGAR, loglevel=LogLevels.WARNING)

    @noexcept
    def handleMultipleTokensError(self):
        self.log(action=SeniorityAwardsLogActions.DISPLAYED, item=SeniorityAwardsLogKeys.MULTIPLE_TOKENS_NOTIFICATION_ERROR, parentScreen=SeniorityAwardsLogSpaces.HANGAR, loglevel=LogLevels.WARNING)


class VehicleSelectionNotificationLogger(SeniorityAwardsMetricsLogger):
    __slots__ = ()

    @noexcept
    def handleClickAction(self):
        self.log(action=SeniorityAwardsLogActions.CLICK, item=SeniorityAwardsLogButtons.SELECT_BUTTON, parentScreen=SeniorityAwardsLogKeys.VEHICLE_SELECTION_NOTIFICATION, info=SeniorityAwardsLogSpaces.NOTIFICATION_CENTER)

    @noexcept
    def handleDisplayedAction(self):
        self.log(action=SeniorityAwardsLogActions.DISPLAYED, item=SeniorityAwardsLogKeys.VEHICLE_SELECTION_NOTIFICATION, parentScreen=SeniorityAwardsLogSpaces.NOTIFICATION_CENTER)


class RewardNotificationLogger(SeniorityAwardsMetricsLogger):
    __slots__ = ()

    @noexcept
    def handleClickAction(self, displaySpace):
        self.log(action=SeniorityAwardsLogActions.CLICK, item=SeniorityAwardsLogButtons.CLAIM_BUTTON, parentScreen=SeniorityAwardsLogKeys.REWARD_NOTIFICATION, info=displaySpace)

    @noexcept
    def handleDisplayedAction(self, parentScreen, limitedUICompleted, isNeedBullet):
        additionalInfo = ''
        if not limitedUICompleted:
            additionalInfo += 'limited_ui'
        if isNeedBullet:
            additionalInfo += ';bullet' if additionalInfo else 'bullet'
        self.log(action=SeniorityAwardsLogActions.DISPLAYED, item=SeniorityAwardsLogKeys.REWARD_NOTIFICATION, parentScreen=parentScreen, info=additionalInfo or None)
        return


class CoinsNotificationLogger(SeniorityAwardsMetricsLogger):
    __slots__ = ()

    @noexcept
    def handleClickAction(self, displaySpace):
        self.log(action=SeniorityAwardsLogActions.CLICK, item=SeniorityAwardsLogButtons.SHOP_BUTTON, parentScreen=SeniorityAwardsLogKeys.COINS_NOTIFICATION, info=displaySpace)

    @noexcept
    def handleDisplayedAction(self, parentScreen):
        self.log(action=SeniorityAwardsLogActions.DISPLAYED, item=SeniorityAwardsLogKeys.COINS_NOTIFICATION, parentScreen=parentScreen)
