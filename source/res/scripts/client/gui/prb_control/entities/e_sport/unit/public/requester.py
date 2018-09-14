# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/e_sport/unit/public/requester.py
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.Waiting import Waiting
from gui.prb_control import prb_getters
from gui.prb_control.entities.base.cooldown import PrbCooldownManager
from gui.prb_control.entities.base.requester import IPrbListRequester
from gui.prb_control.items.unit_seqs import UnitsListIterator, UnitsUpdateIterator
from gui.prb_control.settings import REQUEST_TYPE
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class UnitsListRequester(IPrbListRequester):
    """
    Class for units list requester. It has basic pagination functionality,
    and could store items found in local cache.
    """
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__selectedID = None
        self.__callback = None
        self.__callbackUpdate = None
        self.__isSubscribed = False
        self.__cooldown = PrbCooldownManager()
        self.__handlers = {}
        self.__cache = {}
        return

    def __del__(self):
        LOG_DEBUG('Units list requester deleted:', self)

    def start(self, callback):
        self.__cache.clear()
        if callback is not None and callable(callback):
            self.__callback = callback
        else:
            LOG_ERROR('Callback is None or is not callable')
            return
        if self.__cooldown.isInProcess(REQUEST_TYPE.UNITS_LIST):
            self.__cooldown.fireEvent(REQUEST_TYPE.UNITS_LIST)
        browser = prb_getters.getClientUnitBrowser()
        if browser:
            self.__unitBrowser_onUnitsListReceived(browser.results)
        return

    def stop(self):
        self.__cache.clear()
        self.__callback = None
        self.__callbackUpdate = None
        return

    def request(self, **kwargs):
        if self.__cooldown.validate(REQUEST_TYPE.UNITS_LIST):
            return
        LOG_DEBUG('Request list of units', kwargs)
        self.__cooldown.process(REQUEST_TYPE.UNITS_LIST)
        self.__cache.clear()
        browser = prb_getters.getClientUnitBrowser()
        if browser:
            if 'req' in kwargs:
                req = kwargs['req']
                if req in self.__handlers:
                    if self.__handlers[req](browser, **kwargs):
                        Waiting.show('prebattle/auto_search')
                else:
                    LOG_ERROR('Request is not supported', kwargs)
            else:
                LOG_ERROR('Request is not found', self.__handlers.keys(), kwargs)
        else:
            LOG_ERROR('Unit browser is not defined')

    def subscribe(self, unitTypeFlags):
        """
        Subscribes to client unit browser events
        Args:
            unitTypeFlags: flags of units visibility
        """
        if self.__isSubscribed:
            return
        self.__isSubscribed = True
        browser = prb_getters.getClientUnitBrowser()
        if browser:
            self.__cooldown.process(REQUEST_TYPE.UNITS_LIST)
            self.__handlers = {REQUEST_TYPE.UNITS_RECENTER: self.__recenter,
             REQUEST_TYPE.UNITS_REFRESH: self.__refresh,
             REQUEST_TYPE.UNITS_NAV_LEFT: self.__navLeft,
             REQUEST_TYPE.UNITS_NAV_RIGHT: self.__navRight}
            browser.subscribe(unitTypeFlags=unitTypeFlags)
            browser.onResultsReceived += self.__unitBrowser_onUnitsListReceived
            browser.onResultsUpdated += self.__unitBrowser_onUnitsListUpdated
        else:
            LOG_ERROR('Unit browser is not defined')

    def unsubscribe(self):
        """
        Unsubscribes to client unit browser events
        """
        self.__handlers.clear()
        browser = prb_getters.getClientUnitBrowser()
        if browser:
            if self.__isSubscribed:
                browser.unsubscribe()
            browser.onResultsReceived -= self.__unitBrowser_onUnitsListReceived
            browser.onResultsUpdated -= self.__unitBrowser_onUnitsListUpdated
        self.__isSubscribed = False
        self.__selectedID = None
        return

    def setSelectedID(self, selectedID):
        """
        Sets currently selected item ID
        Args:
            selectedID: selected unit ID
        """
        self.__selectedID = selectedID

    def addCacheItem(self, item):
        """
        Adds item to local cache.
        Args:
            item: unit item data
        """
        self.__cache[item.cfdUnitID] = item

    def getCacheItem(self, cfdUnitID):
        """
        Tries to get item from local cache.
        Args:
            cfdUnitID: unit index
        """
        try:
            item = self.__cache[cfdUnitID]
        except KeyError:
            LOG_ERROR('Item not found in cache', cfdUnitID)
            item = None

        return item

    def removeCacheItem(self, cfdUnitID):
        """
        Removes item from local cache.
        Args:
            cfdUnitID: unit index
        """
        self.__cache.pop(cfdUnitID, None)
        return

    def __navLeft(self, browser, **kwargs):
        """
        Loads next bunch of units
        Args:
            browser: unit browser instance
        """
        browser.left()
        return True

    def __navRight(self, browser, **kwargs):
        """
        Loads previous bunch of units
        Args:
            browser: unit browser instance
        """
        browser.right()
        return True

    def __recenter(self, browser, **kwargs):
        """
        Resets current page to default
        Args:
            browser: unit browser instance
        """
        result = False
        if 'unitTypeFlags' in kwargs:
            browser.recenter(self.itemsCache.items.stats.globalRating, unitTypeFlags=kwargs['unitTypeFlags'])
            result = True
        else:
            LOG_ERROR('Types of units are not defined', kwargs)
        return result

    def __refresh(self, browser, **kwargs):
        """
        Refreshes currently selected page
        Args:
            browser: unit browser instance
        """
        browser.refresh()
        return True

    def __unitBrowser_onUnitsListReceived(self, data):
        """
        Listener for list receive event
        Args:
            data: result with units data, like unit Idx -> unit data
        """
        Waiting.hide('prebattle/auto_search')
        if self.__callback:
            self.__callback(self.__selectedID, True, self.__cooldown.isInProcess(REQUEST_TYPE.UNITS_LIST), UnitsListIterator(self, data))

    def __unitBrowser_onUnitsListUpdated(self, data):
        """
        Listener for list update event
        Args:
            data: result with units data, like unit Idx -> unit data
        """
        if self.__callback:
            self.__callback(self.__selectedID, False, False, UnitsUpdateIterator(self, data))
