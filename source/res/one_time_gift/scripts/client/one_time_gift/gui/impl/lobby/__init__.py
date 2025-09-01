# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/__init__.py
from gui.impl.gen import R
from gui.shared.system_factory import registerGamefaceNotifications
from one_time_gift.gui.impl.lobby.reward_available_notification_view import RewardAvailableNotificationView

def getViewSettings():
    pass


def getBusinessHandlers():
    pass


def getContextMenuHandlers():
    pass


OTG_REWARD_AVAILABLE_NOTIFICATION = 'OTGRewardAvailableNotification'
registerGamefaceNotifications({OTG_REWARD_AVAILABLE_NOTIFICATION: (R.views.one_time_gift.mono.lobby.reward_available_notification_view(), RewardAvailableNotificationView)})
