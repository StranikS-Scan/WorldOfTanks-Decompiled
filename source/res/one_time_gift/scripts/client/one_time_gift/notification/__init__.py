# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/notification/__init__.py
from gui.shared.system_factory import registerNotificationsListeners
from one_time_gift.notification.listeners import RewardAvailableListener

def registerOTGNotificationsListeners():
    registerNotificationsListeners((RewardAvailableListener,))
