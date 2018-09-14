# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/Research.py
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
import nations
from CurrentVehicle import g_currentVehicle
from constants import IS_DEVELOPMENT
from debug_utils import LOG_DEBUG
from items import getTypeOfCompactDescr
from gui import game_control
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.ResearchMeta import ResearchMeta
from gui.shared import events, EVENT_BUS_SCOPE, g_itemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.Scaleform.daapi.view.lobby.techtree.settings import USE_XML_DUMPING
from gui.Scaleform.daapi.view.lobby.techtree.settings import SelectedNation
from gui.Scaleform.daapi.view.lobby.techtree.data import ResearchItemsData
from gui.Scaleform.daapi.view.lobby.techtree import dumpers

class RESEARCH_HINT_ID(object):
    PREMIUM = 'researchAlone'
    TOP = 'researchTop'
    ROOT = 'researchRoot'
    BASE = 'researchBase'
    IGR_OR_FALLOUT = 'researchIgrFallout'


class Research(ResearchMeta):

    def __init__(self, ctx = None):
        if USE_XML_DUMPING and IS_DEVELOPMENT:
            dumper = dumpers.ResearchItemsXMLDumper()
        else:
            dumper = dumpers.ResearchItemsObjDumper()
        super(Research, self).__init__(ResearchItemsData(dumper))
        self._resolveLoadCtx(ctx=ctx)

    def __del__(self):
        LOG_DEBUG('ResearchPage deleted')

    def requestNationData(self):
        if USE_XML_DUMPING and IS_DEVELOPMENT:
            self.as_useXMLDumpingS()
        self.redraw()
        return True

    def getResearchItemsData(self, vehCD, rootChanged):
        if rootChanged:
            self._data.setRootCD(vehCD)
        self._data.load()
        self.setupContextHints(self.__getContextHintsID())
        return self._data.dump()

    def redraw(self):
        self.as_drawResearchItemsS(nations.NAMES[self._data.getNationID()], self._data.getRootCD())

    def onResearchItemsDrawn(self):
        pass

    def request4Unlock(self, itemCD, parentID, unlockIdx, xpCost):
        ItemsActionsFactory.doAction(ItemsActionsFactory.UNLOCK_ITEM, int(itemCD), int(parentID), int(unlockIdx), int(xpCost))

    def request4Buy(self, itemCD):
        itemCD = int(itemCD)
        if getTypeOfCompactDescr(itemCD) == GUI_ITEM_TYPE.VEHICLE:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, itemCD)
        else:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_ITEM, itemCD, self._data.getRootCD())

    def goToTechTree(self, nation):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_TECHTREE, ctx={'nation': nation}), scope=EVENT_BUS_SCOPE.LOBBY)

    def exitFromResearch(self):
        if self._canBeClosed:
            self.fireEvent(events.LoadEvent(events.LoadEvent.EXIT_FROM_RESEARCH), scope=EVENT_BUS_SCOPE.LOBBY)

    def invalidateUnlocks(self, unlocks):
        if self._data.isRedrawNodes(unlocks):
            self.redraw()
        else:
            super(Research, self).invalidateUnlocks(unlocks)

    def invalidateInventory(self, data):
        if self._data.isRedrawNodes(data):
            self.redraw()
        else:
            super(Research, self).invalidateInventory(data)
            result = self._data.invalidateInstalled()
            if len(result):
                self.as_setInstalledItemsS(result)

    def invalidatePrbState(self):
        self.redraw()
        super(Research, self).invalidatePrbState()

    def invalidateFreeXP(self):
        self.as_setFreeXPS(g_itemsCache.items.stats.actualFreeXP)
        super(Research, self).invalidateFreeXP()

    def invalidateRent(self, vehicles):
        if self._data.getRootCD() in vehicles:
            self.redraw()

    def invalidateVehLocks(self, locks):
        if self._data.invalidateLocks(locks):
            self.redraw()

    def invalidateWalletStatus(self, status):
        self.invalidateFreeXP()
        self.as_setWalletStatusS(status)

    def _populate(self):
        super(Research, self)._populate()
        self.as_setWalletStatusS(game_control.g_instance.wallet.componentsStatuses)
        self.setupContextHints(self.__getContextHintsID())

    def _dispose(self):
        super(Research, self)._dispose()

    def _resolveLoadCtx(self, ctx = None):
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
        vehicle = g_itemsCache.items.getItemByCD(rootCD)
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
