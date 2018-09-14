# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/clan_lock_controller.py
import Event
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.game_control.controllers import Controller
from gui.shared import g_itemsCache
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from gui.shared.gui_items import CLAN_LOCK
_UPDATE_LOCKS_PERIOD = 60

class ClanLockController(Controller, Notifiable):
    """ This controller handles occurrence of vehicle locks (global or by vehicle)
     and fires a special event each minute util these locks exist.
    """

    def __init__(self, proxy):
        super(ClanLockController, self).__init__(proxy)
        self.onClanLockUpdate = Event.Event()
        self.__lockedVehicles = []
        self.__isFullLock = False

    def init(self):
        self.addNotificators(PeriodicNotifier(lambda : _UPDATE_LOCKS_PERIOD, lambda : self.onClanLockUpdate(self.__lockedVehicles, self.__isFullLock)))

    def fini(self):
        self.__stop()
        self.clearNotification()

    def onLobbyStarted(self, ctx):
        g_clientUpdateManager.addCallbacks({'stats.vehTypeLocks': self.__updateVehicleLocks,
         'stats.globalVehicleLocks': self.__updateGlobalLocks})
        self.__updateVehicleLocks(g_itemsCache.items.stats.vehicleTypeLocks)
        self.__updateGlobalLocks(g_itemsCache.items.stats.globalVehicleLocks)

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__stop()

    def __stop(self):
        self.stopNotification()
        self.__isFullLock = False
        self.__lockedVehicles = []
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __updateVehicleLocks(self, locks):
        self.__lockedVehicles = [ key for key, value in locks.iteritems() if value.get(CLAN_LOCK, None) is not None ]
        self.__notificationStartStop()
        return

    def __updateGlobalLocks(self, locks):
        self.__isFullLock = locks.get(CLAN_LOCK, False)
        self.__notificationStartStop()

    def __notificationStartStop(self):
        if self.__isFullLock or self.__lockedVehicles:
            self.startNotification()
        else:
            self.stopNotification()
