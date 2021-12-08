# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/state_machine/__init__.py
from gui.shared.lock_overlays import lockNotificationManager as doLock
_LOCK_SOURCE_NAME = 'BATTLE_PASS_REWARD_LOGIC'

def lockNotificationManager(lock, notificationManager=None):
    doLock(lock, source=_LOCK_SOURCE_NAME, notificationManager=notificationManager)
