# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/shared/lock_overlays.py
from gui.impl.lobby.elite_window.elite_view import EliteWindow
from helpers import dependency
from skeletons.gui.game_control import IAchievements20EarningController, ISteamCompletionController
from skeletons.gui.impl import INotificationWindowController
from one_time_gift.gui.gui_constants import OTG_LOCK_SOURCE_NAME

def _oneTimeGiftBlockEliteWindowsPredicate(command):
    window = command.getWindow()
    if window is not None and isinstance(window, EliteWindow):
        window.destroy()
        return False
    else:
        return True


@dependency.replace_none_kwargs(notificationManager=INotificationWindowController)
def lockEliteWindows(lock, notificationManager=None):
    notificationManager.setFilterPredicate(_oneTimeGiftBlockEliteWindowsPredicate if lock else None)
    return


@dependency.replace_none_kwargs(achievementsEarningCtrl=IAchievements20EarningController)
def lockAchievementsEarning(lock, achievementsEarningCtrl=None):
    isLocked = achievementsEarningCtrl.hasLock(OTG_LOCK_SOURCE_NAME)
    if lock and not isLocked:
        achievementsEarningCtrl.lock(OTG_LOCK_SOURCE_NAME)
    elif not lock and isLocked:
        achievementsEarningCtrl.unlock(OTG_LOCK_SOURCE_NAME)


@dependency.replace_none_kwargs(steamCompletionCtrl=ISteamCompletionController)
def lockSteamShade(lock, steamCompletionCtrl=None):
    isLocked = steamCompletionCtrl.hasLock(OTG_LOCK_SOURCE_NAME)
    if lock and not isLocked:
        steamCompletionCtrl.lock(OTG_LOCK_SOURCE_NAME)
    elif not lock and isLocked:
        steamCompletionCtrl.unlock(OTG_LOCK_SOURCE_NAME)


@dependency.replace_none_kwargs(notificationManager=INotificationWindowController)
def areNotificationsLockedByOTG(notificationManager=None):
    return notificationManager.hasLock(OTG_LOCK_SOURCE_NAME)
