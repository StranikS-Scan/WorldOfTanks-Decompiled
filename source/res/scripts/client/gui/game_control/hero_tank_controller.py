# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/hero_tank_controller.py
import logging
import random
from collections import namedtuple
import ResMgr
import Event
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.game_control.calendar_controller import CalendarOfferType
from helpers import dependency
from skeletons.gui.game_control import IHeroTankController, IBootcampController, ICalendarController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from items import vehicles, tankmen
from shared_utils import first
_logger = logging.getLogger(__name__)
_HERO_VEHICLES = 'hero_vehicles'
_ADD_HERO_STEP_NAME = 'add_HeroVehicle'
_CALENDAR_ACTION_CHANGED = events.AdventCalendarEvent.HERO_ADVENT_ACTION_STATE_CHANGED
_HeroTankInfo = namedtuple('_HeroTankInfo', ('url', 'styleID', 'crew', 'name', 'shopUrl', 'action'))
_HeroTankInfo.__new__.__defaults__ = ('', None, None, '', '', '')

class HeroTankController(IHeroTankController):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    bootcampController = dependency.descriptor(IBootcampController)
    calendarController = dependency.descriptor(ICalendarController)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self.__data = {}
        self.__invVehiclesIntCD = tuple()
        self.__isEnabled = False
        self.__currentTankCD = None
        self.__actionInfo = None
        self.onUpdated = Event.Event()
        self.onInteractive = Event.Event()
        self.onHeroTankChanged = Event.Event()
        self.onHeroTankBought = Event.Event()
        return

    def init(self):
        self.itemsCache.onSyncCompleted += self.__updateInventoryVehiclesData
        g_eventBus.addListener(_CALENDAR_ACTION_CHANGED, self.__updateActionInfo, EVENT_BUS_SCOPE.LOBBY)

    def fini(self):
        g_eventBus.removeListener(_CALENDAR_ACTION_CHANGED, self.__updateActionInfo, EVENT_BUS_SCOPE.LOBBY)
        self.itemsCache.onSyncCompleted -= self.__updateInventoryVehiclesData

    def onDisconnected(self):
        super(HeroTankController, self).onDisconnected()
        self.__currentTankCD = None
        return

    def __onEventsCacheSyncCompleted(self, *_):
        self.__updateSettings()

    def onLobbyStarted(self, ctx):
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self._eventsCache.onSyncCompleted += self.__onEventsCacheSyncCompleted
        self.__fullUpdate()
        self.__updateSettings()
        self.onUpdated()

    def onAvatarBecomePlayer(self):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self._eventsCache.onSyncCompleted -= self.__onEventsCacheSyncCompleted
        self.__currentTankCD = None
        return

    def isEnabled(self):
        return self.__isEnabled and not self.bootcampController.isInBootcamp()

    def hasAdventHero(self):
        return self.__actionInfo is not None and self.__actionInfo.isEnabled

    def isAdventHero(self):
        return self.hasAdventHero() and self.__currentTankCD == self.__actionInfo.vehicleCD

    def getRandomTankCD(self):
        prevTankCD = self.__currentTankCD
        adventTankCD, _ = self._getAdventHeroTankData()
        if adventTankCD:
            self.__currentTankCD = adventTankCD
        else:
            self.__currentTankCD = random.choice(self.__data.keys() or [None]) if self.isEnabled() else None
        if prevTankCD != self.__currentTankCD:
            self.onHeroTankChanged()
        return self.__currentTankCD

    def getCurrentTankCD(self):
        return self.__currentTankCD

    def getCurrentTankStyleId(self):
        _, adventTankStyleId = self._getAdventHeroTankData()
        if adventTankStyleId:
            return adventTankStyleId
        else:
            return self.__data[self.__currentTankCD].styleID if self.isEnabled() and self.__currentTankCD in self.__data else None

    def getCurrentRelatedURL(self):
        return self.__data[self.__currentTankCD].url if self.isEnabled() and self.__currentTankCD in self.__data else ''

    def getCurrentShopUrl(self):
        return self.__data[self.__currentTankCD].shopUrl if self.isEnabled() and self.__currentTankCD in self.__data else ''

    def getCurrentTankCrew(self):
        return self.__data[self.__currentTankCD].crew if self.isEnabled() and self.__currentTankCD in self.__data else None

    def getCurrentVehicleName(self):
        return self.__data[self.__currentTankCD].name if self.isEnabled() and self.__currentTankCD in self.__data else ''

    def getCurrentVehicleAction(self):
        return self.__data[self.__currentTankCD].action if self.isEnabled() and self.__currentTankCD in self.__data else ''

    def setInteractive(self, interactive):
        self.onInteractive(interactive)

    def _getAdventHeroTankData(self):
        if not self.hasAdventHero():
            return (None, None)
        else:
            vehicleCD = self.__actionInfo.vehicleCD or None
            if not vehicleCD:
                return (None, None)
            styleId = self.__actionInfo.styleId or None
            styleAvailable = styleId and not self.__containsStyle(styleId)
            vehicleAvailable = not self.__containsVehicle(vehicleCD)
            offerType = self.__actionInfo.offerType
            return (vehicleCD, styleId) if offerType == CalendarOfferType.VEHICLE and vehicleAvailable or offerType == CalendarOfferType.STYLE and styleAvailable or offerType == CalendarOfferType.STYLE_BUNDLE and (styleAvailable or vehicleAvailable) else (None, None)

    def __fullUpdate(self):
        items = self.itemsCache.items
        getItem = items.getItemByCD
        self.__invVehiclesIntCD = tuple({intCD for intCD, rData in items.recycleBin.vehiclesBuffer.iteritems() if rData and getItem(intCD).isRestorePossible()}.union(items.inventory.getIventoryVehiclesCDs()))

    def __updateInventoryVehiclesData(self, reason, diff):
        if reason != CACHE_SYNC_REASON.CLIENT_UPDATE:
            return
        else:
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
                vehDiff = diff[GUI_ITEM_TYPE.VEHICLE]
                if self.__currentTankCD not in vehDiff:
                    return
                self.__fullUpdate()
                self.__updateSettings()
                for vehIntCD in vehDiff:
                    if vehIntCD == self.__currentTankCD:
                        self.onUpdated()

            return

    def __updateActionInfo(self, *_):
        self.__actionInfo = self.calendarController.getHeroAdventActionInfo()
        self.onUpdated()

    def __onServerSettingsChanged(self, diff):
        if _HERO_VEHICLES in diff:
            self.__updateSettings()
            self.onUpdated()

    def __updateSettings(self):
        self.__data = {}
        heroVehiclesDict = self.lobbyContext.getServerSettings().getHeroVehicles()
        self.__isEnabled = heroVehiclesDict.get('isEnabled', False)
        if 'vehicles' in heroVehiclesDict:
            heroVehicles = heroVehiclesDict['vehicles']
            for vCompDescr, vData in heroVehicles.iteritems():
                if vCompDescr in self.__invVehiclesIntCD:
                    continue
                self.__data[vCompDescr] = _HeroTankInfo(name=vData.get('name'), url=vData.get('url'), shopUrl=vData.get('shopUrl'), styleID=vData.get('styleID'), action=vData.get('action'), crew=self.__createCrew(vData.get('crew'), vCompDescr))

        self.__applyActions()
        self.__isEnabled = bool(self.__data)
        self.onUpdated()

    def __applyActions(self):
        actions = self._eventsCache.getActions()
        for action in actions.itervalues():
            steps = action.getData().get('steps', [])
            if not steps:
                continue
            for step in steps:
                if step.get('name') != _ADD_HERO_STEP_NAME:
                    continue
                self.__addActionVehicle(step['params'])

    def __addActionVehicle(self, params):
        vName = params.get('name')
        vCompDescr = vehicles.makeVehicleTypeCompDescrByName(vName)
        if not vCompDescr:
            _logger.error('Could not apply action, vehicle name = %s', vName)
            return
        elif vCompDescr in self.__invVehiclesIntCD:
            return
        else:
            styleStr = params.get('styleID')
            styleId = int(styleStr) if styleStr else None
            self.__data[vCompDescr] = _HeroTankInfo(name=vName, url=params.get('url'), shopUrl=params.get('shopUrl'), styleID=styleId, action=params.get('action'), crew=self.__createCrew(params.get('crew'), vCompDescr))
            return

    def __createCrew(self, crewXml, vCompDescr):
        crew = {}
        if not crewXml:
            return crew
        else:
            crewStr = '<root>{}</root>'.format(crewXml.encode('ascii'))
            crewSection = ResMgr.DataSection().createSectionFromString(crewStr)
            if crewSection is not None:
                crew['tankmen'] = []
                _, nationId, vehTypeId = vehicles.parseIntCompactDescr(vCompDescr)
                for tankmanSection in crewSection.values():
                    tmanDict = {}
                    tmanId = tankmanSection.readString('name')
                    if not tmanId:
                        continue
                    tData = None
                    tIdx = None
                    for idx, tMan in tankmen.getNationConfig(nationId).premiumGroups.iteritems():
                        if tMan.name == tmanId:
                            tData = tMan
                            tIdx = idx
                            break

                    if tData is None:
                        continue
                    tmanDict['isPremium'] = True
                    tmanDict['gId'] = tIdx
                    tmanDict['nationID'] = nationId
                    tmanDict['firstNameID'] = tankmanSection.readInt('firstNameID', first(tData.firstNames))
                    tmanDict['lastNameID'] = tankmanSection.readInt('lastNameID', first(tData.lastNames))
                    tmanDict['iconID'] = tankmanSection.readInt('iconID', first(tData.icons))
                    tmanDict['vehicleTypeID'] = vehTypeId
                    tmanDict['role'] = tankmanSection.readString('role')
                    for param in ('roleLevel', 'freeXP'):
                        tmanDict[param] = tankmanSection.readInt(param)

                    for param in ('skills', 'freeSkills'):
                        paramAsStr = tankmanSection.readString(param)
                        tmanDict[param] = paramAsStr.split(' ') if paramAsStr else []

                    crew['tankmen'].append(tmanDict)

            return crew

    def __containsVehicle(self, vehicleCD):

        def contains(i):
            return i.intCD == vehicleCD and (i.inventoryCount > 0 or i.isRestorePossible())

        return any(self.itemsCache.items.getVehicles(REQ_CRITERIA.CUSTOM(contains)))

    def __containsStyle(self, styleId):

        def contains(i):
            return i.id == styleId and (i.inventoryCount > 0 or i.isRestorePossible())

        return any(self.itemsCache.items.getStyles(REQ_CRITERIA.CUSTOM(contains)))
