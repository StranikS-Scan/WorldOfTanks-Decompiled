# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/Research.py
import nations
from CurrentVehicle import g_currentVehicle
from constants import IS_DEVELOPMENT
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.techtree import dumpers
from gui.Scaleform.daapi.view.lobby.techtree.data import ResearchItemsData
from gui.Scaleform.daapi.view.lobby.techtree.settings import SelectedNation
from gui.Scaleform.daapi.view.lobby.techtree.settings import USE_XML_DUMPING
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import getBtnCompareData
from gui.Scaleform.daapi.view.meta.ResearchMeta import ResearchMeta
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.sounds.ambients import LobbySubViewEnv
from items import getTypeOfCompactDescr

class RESEARCH_HINT_ID(object):
    PREMIUM = 'researchAlone'
    TOP = 'researchTop'
    ROOT = 'researchRoot'
    BASE = 'researchBase'
    IGR_OR_FALLOUT = 'researchIgrFallout'


class Research(ResearchMeta):
    """
    UI Interface for 'Research modules' page.
    """
    __sound_env__ = LobbySubViewEnv

    def __init__(self, ctx=None):
        if USE_XML_DUMPING and IS_DEVELOPMENT:
            dumper = dumpers.ResearchItemsXMLDumper()
        else:
            dumper = dumpers.ResearchItemsObjDumper()
        super(Research, self).__init__(ResearchItemsData(dumper))
        self._resolveLoadCtx(ctx=ctx)

    def __del__(self):
        LOG_DEBUG('ResearchPage deleted')

    def goToVehicleView(self, itemCD):
        vehicle = self.itemsCache.items.getItemByCD(int(itemCD))
        if vehicle:
            if vehicle.isPreviewAllowed():
                shared_events.showVehiclePreview(int(itemCD), self.alias)
            elif vehicle.isInInventory:
                shared_events.selectVehicleInHangar(itemCD)

    def requestNationData(self):
        """
        Game communication.
        Overridden method of the class _Py_ScriptHandler.requestNationData.
        """
        if USE_XML_DUMPING and IS_DEVELOPMENT:
            self.as_useXMLDumpingS()
        self.redraw()
        return True

    def getResearchItemsData(self, vehCD, rootChanged):
        """
        Overridden method of the class _Py_ScriptHandler.getResearchItemsData.
        """
        if rootChanged:
            self._data.setRootCD(vehCD)
        self._data.load()
        self.setupContextHints(self.__getContextHintsID())
        return self._data.dump()

    def redraw(self):
        """
        Redraws items for selected vehicle.
        """
        self.as_drawResearchItemsS(nations.NAMES[self._data.getNationID()], self._data.getRootCD())

    def onResearchItemsDrawn(self):
        """
        Overridden method of the class _Py_ScriptHandler.onResearchItemsDrawn.
        """
        pass

    def request4Unlock(self, itemCD, parentID, unlockIdx, xpCost):
        """
        Overridden method of the class ResearchViewMeta.request4Unlock.
        """
        ItemsActionsFactory.doAction(ItemsActionsFactory.UNLOCK_ITEM, int(itemCD), int(parentID), int(unlockIdx), int(xpCost))

    def request4Buy(self, itemCD):
        """
        Overridden method of the class ResearchViewMeta.request4Buy.
        """
        itemCD = int(itemCD)
        if getTypeOfCompactDescr(itemCD) == GUI_ITEM_TYPE.VEHICLE:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, itemCD)
        else:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_ITEM, itemCD, self._data.getRootCD())

    def request4Restore(self, itemCD):
        itemCD = int(itemCD)
        if getTypeOfCompactDescr(itemCD) == GUI_ITEM_TYPE.VEHICLE:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, itemCD)

    def goToTechTree(self, nation):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_TECHTREE, ctx={'nation': nation}), scope=EVENT_BUS_SCOPE.LOBBY)

    def exitFromResearch(self):
        if self._canBeClosed:
            self.fireEvent(events.LoadEvent(events.LoadEvent.EXIT_FROM_RESEARCH), scope=EVENT_BUS_SCOPE.LOBBY)

    def invalidateVehCompare(self):
        """
        Updates compare add icon status of nodes if change status of comparison basket fullness.
        """
        super(Research, self).invalidateVehCompare()
        self.as_setRootNodeVehCompareDataS(getBtnCompareData(self.itemsCache.items.getItemByCD(self._data.getRootCD())))

    def invalidateUnlocks(self, unlocks):
        """
        Set of unlocks items updated. If root has been unlocked than redraws all
        nodes, otherwise - updates nodes that have been unlocked, next to unlock.
        :param unlocks: set([<int:compactDescr>, ...])
        """
        if self._data.isRedrawNodes(unlocks):
            self.redraw()
        else:
            super(Research, self).invalidateUnlocks(unlocks)

    def invalidateInventory(self, data):
        """
        Inventory items are updated. If root has been changed than redraws all
        nodes, otherwise - updates nodes that have been purchased.
        :param data: set of int-type compact descriptors for  modified items (vehicles/modules).
        """
        if self._data.isRedrawNodes(data):
            self.redraw()
        else:
            super(Research, self).invalidateInventory(data)
            result = self._data.invalidateInstalled()
            if len(result):
                self.as_setInstalledItemsS(result)

    def invalidatePrbState(self):
        """
        Player's PRB state was changed in prb, unit or prequeue entity.
        """
        self.redraw()
        super(Research, self).invalidatePrbState()

    def invalidateFreeXP(self):
        """
        Overridden method of the class ResearchView.invalidateFreeXP.
        """
        self.as_setFreeXPS(self.itemsCache.items.stats.actualFreeXP)
        super(Research, self).invalidateFreeXP()

    def invalidateRent(self, vehicles):
        """
        Overridden method of the class ResearchView.invalidateRent.
        """
        if self._data.getRootCD() in vehicles:
            self.redraw()

    def invalidateVehLocks(self, locks):
        """
        Overridden method of the class ResearchView.invalidateVehLocks.
        """
        if self._data.invalidateLocks(locks):
            self.redraw()

    def invalidateWalletStatus(self, status):
        """
        Overridden method of the class ResearchView.invalidateWalletStatus.
        """
        self.invalidateFreeXP()
        self.as_setWalletStatusS(status)

    def invalidateRestore(self, vehicles):
        if self._data.getRootCD() in vehicles:
            self.redraw()

    def compareVehicle(self, itemCD):
        self.cmpBasket.addVehicle(int(itemCD))

    def _populate(self):
        super(Research, self)._populate()
        self.as_setWalletStatusS(self.wallet.componentsStatuses)
        self.setupContextHints(self.__getContextHintsID())

    def _dispose(self):
        super(Research, self)._dispose()

    def _resolveLoadCtx(self, ctx=None):
        rootCD = ctx['rootCD'] if ctx is not None and 'rootCD' in ctx else None
        if rootCD is None:
            if g_currentVehicle.isPresent():
                self._data.setRootCD(g_currentVehicle.item.intCD)
        else:
            self._data.setRootCD(rootCD)
        SelectedNation.select(self._data.getNationID())
        return

    def __getContextHintsID(self):
        rootCD = self._data.getRootCD()
        hasParents = len(g_techTreeDP.getTopLevel(rootCD))
        hasChildren = len(g_techTreeDP.getNextLevel(rootCD))
        vehicle = self.itemsCache.items.getItemByCD(rootCD)
        if hasParents and hasChildren:
            return RESEARCH_HINT_ID.BASE
        elif hasParents:
            return RESEARCH_HINT_ID.TOP
        elif hasChildren:
            return RESEARCH_HINT_ID.ROOT
        elif vehicle is not None and vehicle.isPremium:
            return RESEARCH_HINT_ID.PREMIUM
        else:
            return RESEARCH_HINT_ID.IGR_OR_FALLOUT
            return
