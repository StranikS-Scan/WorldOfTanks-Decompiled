# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/hero_tank_controller.py
import random
from collections import namedtuple
import Event
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IHeroTankController, IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_HERO_VEHICLES = 'hero_vehicles'
_HeroTankInfo = namedtuple('_HeroTankInfo', ('url', 'styleID'))
_HeroTankInfo.__new__.__defaults__ = ('', None)

class HeroTankController(IHeroTankController):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        self.__data = {}
        self.__invVehsIntCD = []
        self.__isEnabled = False
        self.__currentTankCD = None
        self.onUpdated = Event.Event()
        self.onInteractive = Event.Event()
        return

    def init(self):
        self.itemsCache.onSyncCompleted += self.__updateInventoryVehsData

    def fini(self):
        self.itemsCache.onSyncCompleted -= self.__updateInventoryVehsData

    def onLobbyStarted(self, ctx):
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__fullUpdate()
        self.__updateSettings()
        self.onUpdated()

    def onAvatarBecomePlayer(self):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged

    def isEnabled(self):
        return self.__isEnabled and not self.bootcampController.isInBootcamp()

    def getRandomTankCD(self):
        if self.isEnabled():
            items = self.__data.keys() or [None]
            self.__currentTankCD = random.choice(items)
        else:
            self.__currentTankCD = None
        return self.__currentTankCD

    def getCurrentTankCD(self):
        return self.__currentTankCD

    def getCurrentTankStyleId(self):
        return self.__data[self.__currentTankCD].styleID if self.__currentTankCD in self.__data else None

    def getCurrentRelatedURL(self):
        if self.isEnabled():
            vehicleCD = self.__currentTankCD
            if vehicleCD in self.__data:
                return self.__data[vehicleCD].url
            return ''

    def setInteractive(self, interactive):
        self.onInteractive(interactive)

    def __fullUpdate(self):
        self.__invVehsIntCD = []
        invVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.CUSTOM(lambda item: item.inventoryCount > 0 or item.isRestorePossible())).values()
        for invVeh in invVehicles:
            self.__invVehsIntCD.append(invVeh.intCD)

    def __updateInventoryVehsData(self, reason, diff):
        if reason != CACHE_SYNC_REASON.CLIENT_UPDATE:
            return
        else:
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
                vehDiff = diff[GUI_ITEM_TYPE.VEHICLE]
                self.__fullUpdate()
                self.__updateSettings()
                for vehIntCD in vehDiff:
                    if vehIntCD == self.__currentTankCD:
                        self.onUpdated()

            return

    def __onServerSettingsChanged(self, diff):
        if _HERO_VEHICLES in diff:
            self.__updateSettings()
            self.onUpdated()

    def __updateSettings(self):
        self.__data = {}
        heroVehsDict = self.lobbyContext.getServerSettings().getHeroVehicles()
        self.__isEnabled = heroVehsDict.get('isEnabled', False)
        if 'vehicles' in heroVehsDict:
            heroVehicles = heroVehsDict['vehicles']
            self.__data = {k:_HeroTankInfo(**v) for k, v in heroVehicles.iteritems() if k not in self.__invVehsIntCD}
