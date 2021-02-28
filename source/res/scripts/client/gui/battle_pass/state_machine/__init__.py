# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/state_machine/__init__.py
from helpers import dependency
from skeletons.gui.impl import INotificationWindowController
_LOCK_SOURCE_NAME = 'BATTLE_PASS_REWARD_LOGIC'

@dependency.replace_none_kwargs(notificationManager=INotificationWindowController)
def lockNotificationManager(lock, notificationManager=None):
    isLocked = notificationManager.hasLock(_LOCK_SOURCE_NAME)
    if lock and not isLocked:
        notificationManager.lock(_LOCK_SOURCE_NAME)
    elif not lock and isLocked:
        notificationManager.unlock(_LOCK_SOURCE_NAME)
