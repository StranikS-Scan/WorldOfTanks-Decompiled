# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/e_sport/unit/entity.py
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR, LOG_WARNING
from gui.prb_control import settings, prb_getters
from gui.prb_control.entities.e_sport.unit.requester import UnitAutoSearchHandler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.unit.entity import UnitIntroEntity, UnitBrowserEntity, UnitEntity, UnitIntroEntryPoint, UnitBrowserEntryPoint, UnitEntryPoint
from gui.prb_control.entities.base.unit.listener import IUnitIntroListener
from gui.prb_control.entities.e_sport.unit.actions_handler import ESportActionsHandler
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from gui.shared.utils.requesters import REQ_CRITERIA

class ESportIntroEntry(UnitIntroEntryPoint):
    """
    ESport intro entry point
    """

    def __init__(self):
        super(ESportIntroEntry, self).__init__(FUNCTIONAL_FLAG.E_SPORT, PREBATTLE_TYPE.E_SPORT_COMMON)


class ESportBrowserEntryPoint(UnitBrowserEntryPoint):
    """
    Base ESport browser entry point
    """

    def __init__(self, prbType):
        super(ESportBrowserEntryPoint, self).__init__(FUNCTIONAL_FLAG.E_SPORT, prbType)


class ESportEntryPoint(UnitEntryPoint):
    """
    Base ESport entry point
    """

    def __init__(self, accountsToInvite=None):
        super(ESportEntryPoint, self).__init__(FUNCTIONAL_FLAG.E_SPORT, accountsToInvite)


class ESportIntroEntity(UnitIntroEntity):
    """
    ESport intro entity
    """

    def __init__(self):
        RQ_TYPE = settings.REQUEST_TYPE
        handlers = {RQ_TYPE.AUTO_SEARCH: self.doAutoSearch,
         RQ_TYPE.ACCEPT_SEARCH: self.acceptSearch,
         RQ_TYPE.DECLINE_SEARCH: self.declineSearch}
        super(ESportIntroEntity, self).__init__(FUNCTIONAL_FLAG.E_SPORT, handlers, IUnitIntroListener, PREBATTLE_TYPE.E_SPORT_COMMON)

    def init(self, ctx=None):
        self._searchHandler = UnitAutoSearchHandler(self)
        self._searchHandler.init()
        selectedVehs = self.getSelectedVehicles('selectedIntroVehicles')
        if not selectedVehs and g_currentVehicle.isPresent():
            selectedVehs = [g_currentVehicle.item.intCD]
        self.setSelectedVehicles('selectedIntroVehicles', selectedVehs)
        return super(ESportIntroEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if self._searchHandler is not None:
            self._searchHandler.fini()
            self._searchHandler = None
        return super(ESportIntroEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def initEvents(self, listener):
        if listener in self.getListenersIterator():
            if self._searchHandler:
                self._searchHandler.initEvents(listener)
        else:
            LOG_ERROR('Listener not found', listener)

    def resetPlayerState(self):
        if self._searchHandler and self._searchHandler.isInSearch():
            self._searchHandler.stop()

    def doSelectAction(self, action):
        actionName = action.actionName
        if actionName == PREBATTLE_ACTION_NAME.E_SPORT:
            g_eventDispatcher.showUnitWindow(self._prbType)
            return SelectResult(True)
        return super(ESportIntroEntity, self).doSelectAction(action)

    def hasLockedState(self):
        return self._searchHandler and self._searchHandler.isInSearch()

    def getSelectedVehicles(self, section, useAll=True):
        """
        Returns list of intCD's of selected vehicles.
        Args:
            section: section in AccountSettings to store
            useAll: should we use all vehicles
        
        Returns:
            selected vehicles list
        """
        accSettings = dict(AccountSettings.getSettings('unitWindow'))
        vehicles = accSettings.get(section, [])
        items = self.itemsCache.items
        if vehicles or not useAll:
            selectedVehicles = []
            for vehCD in vehicles:
                vehCD = int(vehCD)
                if items.doesVehicleExist(vehCD):
                    vehicle = self.itemsCache.items.getItemByCD(vehCD)
                    if vehicle.isInInventory:
                        selectedVehicles.append(vehCD)
                LOG_WARNING('There is invalid vehicle compact descriptor in the stored unit seelected vehicles data', vehCD)

        else:
            criteria = REQ_CRITERIA.INVENTORY
            selectedVehicles = [ k for k, v in self.itemsCache.items.getVehicles(criteria).iteritems() if v.level in self._rosterSettings.getLevelsRange() ]
        return selectedVehicles

    def setSelectedVehicles(self, section, vehicles):
        """
        Sets the list of selected vehicles
        Args:
            section: section to store
            vehicles: vehicles intCDs
        """
        settings = dict(AccountSettings.getSettings('unitWindow'))
        settings[section] = vehicles
        AccountSettings.setSettings('unitWindow', settings)

    def doAutoSearch(self, ctx, callback=None):
        """
        Starts player's auto search
        Args:
            ctx: auto search request context
            callback: operation callback
        """
        if ctx.isRequestToStart():
            if self.isParentControlActivated(callback=callback):
                return
            result = self._searchHandler.start(ctx.getVehTypes())
        else:
            result = self._searchHandler.stop()
        if callback:
            callback(result)

    def acceptSearch(self, ctx, callback=None):
        """
        Accepts player's auto search
        Args:
            ctx: accept auto search request context
            callback: operation callback
        """
        result = self._searchHandler.accept()
        if callback:
            callback(result)

    def declineSearch(self, ctx, callback=None):
        """
        Declines player's auto search
        Args:
            ctx: decline auto search request context
            callback: operation callback
        """
        result = self._searchHandler.decline()
        if callback:
            callback(result)

    def _loadUnit(self):
        g_eventDispatcher.loadUnit(self._prbType)

    def _unloadUnit(self):
        g_eventDispatcher.removeUnitFromCarousel(self._prbType)

    def _showWindow(self):
        g_eventDispatcher.showUnitWindow(self._prbType)


class ESportBrowserEntity(UnitBrowserEntity):
    """
    Base ESport broweser entity
    """

    def __init__(self, prbType):
        super(ESportBrowserEntity, self).__init__(FUNCTIONAL_FLAG.E_SPORT, prbType)

    def getIntroType(self):
        return PREBATTLE_TYPE.E_SPORT_COMMON

    def _getUnit(self, unitIdx=None):
        unitBrowser = prb_getters.getClientUnitBrowser()
        if unitBrowser:
            results = unitBrowser.results
        else:
            results = {}
        if unitIdx in results:
            unit = results[unitIdx]['unit']
        else:
            unit = None
        return (unitIdx, unit)

    def _loadUnit(self):
        g_eventDispatcher.loadUnit(self._prbType)

    def _unloadUnit(self):
        g_eventDispatcher.removeUnitFromCarousel(self._prbType)

    def _showWindow(self):
        g_eventDispatcher.showUnitWindow(self._prbType)


class ESportEntity(UnitEntity):
    """
    Base ESport entity
    """

    def __init__(self, prbType):
        super(ESportEntity, self).__init__(FUNCTIONAL_FLAG.E_SPORT, prbType)

    def _createActionsHandler(self):
        return ESportActionsHandler(self)
