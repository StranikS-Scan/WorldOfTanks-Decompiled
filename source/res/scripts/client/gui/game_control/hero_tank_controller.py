# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/hero_tank_controller.py
import datetime
import random
import time
from collections import namedtuple
import BigWorld
import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import LAST_HEROTANK_SHOW_TIMESTAMP, LAST_HEROTANK_SHOW_ID
from adisp import process
from gui import GUI_SETTINGS, _logger
from gui.server_events.modifiers import HeroTankModifier
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.wgcg.hero_tank.contexts import GetHeroTankRequestCtx
from helpers import dependency, time_utils
from helpers.time_utils import ONE_HOUR
from skeletons.gui.game_control import IHeroTankController, IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
_HERO_VEHICLES = 'hero_vehicles'
_HeroTankInfo = namedtuple('_HeroTankInfo', ('url', 'styleID'))
_HeroTankInfo.__new__.__defaults__ = ('', None)

class HeroTankController(IHeroTankController):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    bootcampController = dependency.descriptor(IBootcampController)
    eventsCache = dependency.descriptor(IEventsCache)
    webCtrl = dependency.descriptor(IWebController)

    def __init__(self):
        self.__data = {}
        self.__invVehsIntCD = []
        self.__isEnabled = False
        self.__currentTankCD = None
        self.__reloadCallbackId = None
        self.onUpdated = Event.Event()
        self.onInteractive = Event.Event()
        self.onHeroTankChanged = Event.Event()
        self.onHeroTankBought = Event.Event()
        return

    def init(self):
        self.itemsCache.onSyncCompleted += self.__updateInventoryVehsData

    def fini(self):
        self.__cancelCallback()
        self.itemsCache.onSyncCompleted -= self.__updateInventoryVehsData

    def onLobbyInited(self, event):
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.__fullUpdate()
        self.__updateSettings()
        self.onUpdated()

    def onAvatarBecomePlayer(self):
        self.__cancelCallback()
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.eventsCache.onSyncCompleted -= self.__onSyncCompleted

    def isEnabled(self):
        return self.__isEnabled and not self.bootcampController.isInBootcamp()

    def isOverloaded(self):
        return len(self.eventsCache.getActions(_herotankOverridedActionFilter)) > 0

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

    def mustShow(self):
        result = False
        lastShowTstamp, lastHerotankID = self.__getEffectPlayedTimestamp()
        if not lastShowTstamp or lastShowTstamp < 0:
            return True
        elif not lastHerotankID or lastHerotankID != self.__currentTankCD:
            return True
        else:
            now = time_utils.getServerRegionalTime()
            if lastShowTstamp > now:
                return True
            actions = self.eventsCache.getActions(_herotankOverridedActionFilter).values()
            for action in actions:
                if action.getFinishTime() < now:
                    continue
                stepDuration = None
                for modifier in action.getModifiers():
                    duration = modifier.getDuration() if modifier else None
                    if duration:
                        stepDuration = min(stepDuration, duration) if stepDuration else duration

                stepDuration = (stepDuration or GUI_SETTINGS.adventCalendar['popupIntervalInHours']) * ONE_HOUR
                offerChangedTime = now - int(now - action.getStartTime()) % stepDuration
                wasntVisibleAtAll = not lastShowTstamp or lastShowTstamp > now
                wasntVisibleCurrentOffer = not wasntVisibleAtAll and lastShowTstamp < offerChangedTime
                result = wasntVisibleAtAll or wasntVisibleCurrentOffer

            return result

    def setEffectPlayedTime(self):
        AccountSettings.setSettings(LAST_HEROTANK_SHOW_TIMESTAMP, str(time_utils.getServerRegionalTime()))
        AccountSettings.setSettings(LAST_HEROTANK_SHOW_ID, str(self.__currentTankCD))

    def __getEffectPlayedTimestamp(self):
        tstampStr = AccountSettings.getSettings(LAST_HEROTANK_SHOW_TIMESTAMP)
        herotankIdStr = AccountSettings.getSettings(LAST_HEROTANK_SHOW_ID)
        timestamp = None
        herotankId = ''
        if tstampStr:
            try:
                timestamp = float(tstampStr)
            except (TypeError, ValueError):
                _logger.warning('Invalid herotank show timestamp')

        if herotankIdStr:
            try:
                herotankId = int(herotankIdStr)
            except (TypeError, ValueError):
                _logger.warning('Invalid herotank id')

        return (timestamp, herotankId)

    def __onSyncCompleted(self, *_):
        self.__updateSettings()

    def __fullUpdate(self):
        if not self.isOverloaded():
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
                herotankInInventory = bool(self.itemsCache.items.getVehicles(REQ_CRITERIA.CUSTOM(lambda item: item.inventoryCount > 0 and item.intCD == self.__currentTankCD)).values())
                for vehIntCD in vehDiff:
                    if vehIntCD == self.__currentTankCD and herotankInInventory:
                        self.onUpdated()
                        self.onHeroTankBought()

            return

    def __onServerSettingsChanged(self, diff):
        if _HERO_VEHICLES in diff or self.isOverloaded():
            self.__updateSettings()
            self.onUpdated()

    @process
    def __updateSettings(self):
        self.__reloadCallbackId = None
        heroVehsDict = {'isEnabled': False,
         'vehicles': {}}
        if self.isOverloaded():
            answer = yield self.webCtrl.sendRequest(ctx=GetHeroTankRequestCtx())
            if answer.isSuccess():
                data = answer.data.get(u'data', {})
                finishDate = data.get(u'finish_date', None)
                reloadTime = finishDate - int(time.mktime(datetime.datetime.now().timetuple())) if finishDate else 0
                self.__cancelCallback()
                if reloadTime and reloadTime > 0:
                    self.__reloadCallbackId = BigWorld.callback(reloadTime, self.__updateSettings)
                heroTankCD = data.get(u'vehicle_cd', None)
                heroVehsDict['isEnabled'] = heroTankCD is not None
                if heroTankCD is not None:
                    heroVehsDict['vehicles'][heroTankCD] = {'url': GUI_SETTINGS.adventCalendar['baseURL'],
                     'styleID': 0}
        else:
            heroVehsDict = self.lobbyContext.getServerSettings().getHeroVehicles()
        self.__updateHeroTanks(heroVehsDict)
        self.onUpdated()
        if self.isOverloaded() and heroVehsDict['isEnabled']:
            self.onHeroTankChanged()
        return

    def __updateHeroTanks(self, heroVehsDict):
        self.__isEnabled = heroVehsDict.get('isEnabled', False)
        heroVehicles = heroVehsDict.get('vehicles', {}) if self.__isEnabled else {}
        self.__data = {k:_HeroTankInfo(**v) for k, v in heroVehicles.iteritems() if k not in self.__invVehsIntCD}

    def __cancelCallback(self):
        if self.__reloadCallbackId is not None:
            BigWorld.cancelCallback(self.__reloadCallbackId)
            self.__reloadCallbackId = None
        return


def _herotankOverridedActionFilter(act):
    return any((isinstance(mod, HeroTankModifier) for mod in act.getModifiers()))
