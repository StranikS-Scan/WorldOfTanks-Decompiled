# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/research_page.py
import nations
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.techtree import dumpers
from gui.Scaleform.daapi.view.lobby.techtree.data import ResearchItemsData
from gui.Scaleform.daapi.view.lobby.techtree.settings import SelectedNation
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import getBtnCompareData
from gui.Scaleform.daapi.view.meta.ResearchMeta import ResearchMeta
from gui.Scaleform.genConsts.RESEARCH_ALIASES import RESEARCH_ALIASES
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
    IGR = 'researchIgr'


class Research(ResearchMeta):
    __sound_env__ = LobbySubViewEnv

    def __init__(self, ctx=None, skipConfirm=False):
        super(Research, self).__init__(ResearchItemsData(dumpers.ResearchItemsObjDumper()))
        self._resolveLoadCtx(ctx=ctx)
        self._skipConfirm = skipConfirm

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
        ItemsActionsFactory.doAction(ItemsActionsFactory.UNLOCK_ITEM, int(itemCD), int(parentID), int(unlockIdx), int(xpCost), skipConfirm=self._skipConfirm)

    def request4Buy(self, itemCD):
        itemCD = int(itemCD)
        if getTypeOfCompactDescr(itemCD) == GUI_ITEM_TYPE.VEHICLE:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, itemCD, skipConfirm=self._skipConfirm)
        else:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_ITEM, itemCD, self._data.getRootCD(), skipConfirm=self._skipConfirm)

    def request4Restore(self, itemCD):
        itemCD = int(itemCD)
        if getTypeOfCompactDescr(itemCD) == GUI_ITEM_TYPE.VEHICLE:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, itemCD, skipConfirm=self._skipConfirm)

    def goToTechTree(self, nation):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_TECHTREE, ctx={'nation': nation}), scope=EVENT_BUS_SCOPE.LOBBY)

    def exitFromResearch(self):
        if self._canBeClosed:
            self.fireEvent(events.LoadEvent(events.LoadEvent.EXIT_FROM_RESEARCH), scope=EVENT_BUS_SCOPE.LOBBY)

    def invalidateVehCompare(self):
        super(Research, self).invalidateVehCompare()
        self.as_setRootNodeVehCompareDataS(getBtnCompareData(self.itemsCache.items.getItemByCD(self._data.getRootCD())))

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
            if result:
                self.as_setInstalledItemsS(result)

    def invalidatePrbState(self):
        self.redraw()
        super(Research, self).invalidatePrbState()

    def invalidateFreeXP(self):
        self.as_setFreeXPS(self.itemsCache.items.stats.actualFreeXP)
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

    def invalidateRestore(self, vehicles):
        if self._data.getRootCD() in vehicles:
            self.redraw()

    def compareVehicle(self, itemCD):
        self.cmpBasket.addVehicle(int(itemCD))

    def _populate(self):
        super(Research, self)._populate()
        self.as_setXpInfoLinkageS(self._getExperienceInfoLinkage())
        self.as_setWalletStatusS(self.wallet.componentsStatuses)
        self.setupContextHints(self.__getContextHintsID())

    def _resolveLoadCtx(self, ctx=None):
        rootCD = ctx['rootCD'] if ctx is not None and 'rootCD' in ctx else None
        if rootCD is None:
            if g_currentVehicle.isPresent():
                self._data.setRootCD(g_currentVehicle.item.intCD)
        else:
            self._data.setRootCD(rootCD)
        SelectedNation.select(self._data.getNationID())
        return

    def _getExperienceInfoLinkage(self):
        return RESEARCH_ALIASES.EXPERIENCE_INFO

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
        else:
            return RESEARCH_HINT_ID.PREMIUM if vehicle is not None and vehicle.isPremium else RESEARCH_HINT_ID.IGR
