# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/hero_tank_controller.py
import random
import Event
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IHeroTankController, IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_HERO_VEHICLES = 'hero_vehicles'

class HeroTankController(IHeroTankController):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        self.__data = {}
        self.__invVehsIntCD = []
        self.__isEnabled = False
        self.__currentTankOnScene = ''
        self.onUpdated = Event.Event()

    def init(self):
        self.itemsCache.onSyncCompleted += self.__updateInventoryVehsData

    def fini(self):
        self.itemsCache.onSyncCompleted -= self.__updateInventoryVehsData

    def onLobbyStarted(self, ctx):
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__fullUpdate()

    def onAvatarBecomePlayer(self):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged

    def isEnabled(self):
        return self.__isEnabled and not self.bootcampController.isInBootcamp()

    def getRandomTank(self):
        return self.__getNameFromCD(self.__randomChoice()) if self.isEnabled() else ''

    def getLinkByTankName(self, tankName=''):
        if self.isEnabled():
            searchTankName = tankName or self.__currentTankOnScene
            return self.__data.get(searchTankName, '')

    def getCurrentTankOnScene(self):
        return self.__currentTankOnScene

    def __fullUpdate(self):
        self.__invVehsIntCD = []
        invVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
        for invVeh in invVehicles:
            self.__invVehsIntCD.append(invVeh.intCD)

        self.__updateSettings()

    def __updateInventoryVehsData(self, reason, diff):
        if reason != CACHE_SYNC_REASON.CLIENT_UPDATE:
            return
        else:
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
                vehDiff = diff[GUI_ITEM_TYPE.VEHICLE]
                for vehIntCD in vehDiff:
                    if vehIntCD == self.__currentTankOnScene:
                        self.__fullUpdate()

            return

    def __onServerSettingsChanged(self, diff):
        if _HERO_VEHICLES in diff:
            self.__updateSettings()

    def __updateSettings(self):
        self.__data = {}
        heroVehsDict = self.lobbyContext.getServerSettings().getHeroVehicles()
        self.__isEnabled = heroVehsDict.get('isEnabled', False)
        if 'vehicles' in heroVehsDict:
            self.__data = {k:v for k, v in heroVehsDict['vehicles'].iteritems() if k not in self.__invVehsIntCD}
            self.onUpdated()

    def __randomChoice(self):
        items = self.__data.keys()
        if items:
            self.__currentTankOnScene = random.choice(self.__data.keys())
            return self.__currentTankOnScene

    def __getNameFromCD(self, cd):
        if cd:
            veh = self.itemsCache.items.getItemByCD(cd)
            return veh.name
