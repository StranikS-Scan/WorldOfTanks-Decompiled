# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/Research.py
from adisp import process
from CurrentVehicle import g_currentVehicle
from constants import IS_DEVELOPMENT
from debug_utils import LOG_DEBUG
from gui import SystemMessages, DialogsInterface, game_control
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import LocalSellModuleMeta
from gui.Scaleform.daapi.view.meta.ResearchMeta import ResearchMeta
from gui.Scaleform.daapi.view.lobby.techtree.ResearchView import ResearchView
from gui.shared import events, EVENT_BUS_SCOPE, g_itemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.module import ModuleBuyer, getInstallerProcessor
from gui.shared.gui_items.processors.vehicle import tryToLoadDefaultShellsLayout
from items import vehicles, getTypeOfCompactDescr
from gui.Scaleform.daapi.view.lobby.techtree import USE_XML_DUMPING, SelectedNation, RequestState
from gui.Scaleform.daapi.view.lobby.techtree.data import ResearchItemsData
from gui.Scaleform.daapi.view.lobby.techtree import dumpers
import nations

class Research(ResearchView, ResearchMeta):

    def __init__(self, ctx = None):
        if USE_XML_DUMPING and IS_DEVELOPMENT:
            dumper = dumpers.ResearchItemsXMLDumper()
        else:
            dumper = dumpers.ResearchItemsObjDumper()
        super(Research, self).__init__(ResearchItemsData(dumper))
        self._resolveLoadCtx(ctx=ctx)

    def __del__(self):
        LOG_DEBUG('ResearchPage deleted')

    def _resolveLoadCtx(self, ctx = None):
        rootCD = ctx['rootCD'] if ctx is not None and 'rootCD' in ctx else None
        if rootCD is None:
            if g_currentVehicle.isPresent():
                self._data.setRootCD(g_currentVehicle.item.intCD)
        else:
            self._data.setRootCD(rootCD)
        SelectedNation.select(self._data.getNationID())
        return

    def _populate(self):
        super(Research, self)._populate()
        self.as_setWalletStatusS(game_control.g_instance.wallet.componentsStatuses)

    def _dispose(self):
        super(Research, self)._dispose()

    def requestNationData(self):
        if USE_XML_DUMPING and IS_DEVELOPMENT:
            self.as_useXMLDumpingS()
        self.redraw()
        return True

    def getResearchItemsData(self, vehCD, rootChanged):
        if rootChanged:
            self._data.setRootCD(vehCD)
        self._data.load()
        return self._data.dump()

    def redraw(self):
        self.as_drawResearchItemsS(nations.NAMES[self._data.getNationID()], self._data.getRootCD())

    def onResearchItemsDrawn(self):
        pass

    def request4Unlock(self, itemCD, parentID, unlockIdx, xpCost):
        self.unlockItem(int(itemCD), int(parentID), int(unlockIdx), int(xpCost))

    def request4Buy(self, itemCD):
        itemCD = int(itemCD)
        if getTypeOfCompactDescr(itemCD) == GUI_ITEM_TYPE.VEHICLE:
            self.buyVehicle(itemCD)
        else:
            if RequestState.inProcess('buyAndInstall'):
                SystemMessages.pushI18nMessage('#system_messages:shop/item/buy_and_equip_in_processing', type=SystemMessages.SM_TYPE.Warning)
            self.buyAndInstallItem(itemCD, 'buyAndInstall')

    def request4Sell(self, itemCD):
        itemCD = int(itemCD)
        if getTypeOfCompactDescr(itemCD) == GUI_ITEM_TYPE.VEHICLE:
            self.sellVehicle(itemCD)
        else:
            self.sellItem(itemCD)

    def request4SelectInHangar(self, itemCD):
        self.selectVehicleInHangar(itemCD)
        self.fireEvent(events.LoadEvent(events.LoadEvent.LOAD_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def request4ShowVehicleStatistics(self, itemCD):
        self.showVehicleStatistics(itemCD)

    def request4Install(self, itemCD):
        if RequestState.inProcess('install'):
            SystemMessages.pushI18nMessage('#system_messages:inventory/item/equip_in_processing', type=SystemMessages.SM_TYPE.Warning)
        itemCD = int(itemCD)
        self.buyAndInstallItem(itemCD, 'install', inInventory=True)

    def requestModuleInfo(self, pickleDump):
        self.showModuleInfo(pickleDump)

    def requestVehicleInfo(self, pickleDump):
        self.showVehicleInfo(pickleDump)

    def goToTechTree(self, nation):
        self.fireEvent(events.LoadEvent(events.LoadEvent.LOAD_TECHTREE, ctx={'nation': nation}), scope=EVENT_BUS_SCOPE.LOBBY)

    def exitFromResearch(self):
        if self._canBeClosed:
            self.fireEvent(events.LoadEvent(events.LoadEvent.EXIT_FROM_RESEARCH), scope=EVENT_BUS_SCOPE.LOBBY)

    @process
    def buyAndInstallItem(self, itemCD, state, inInventory = False):
        itemTypeID, nationID, itemID = vehicles.parseIntCompactDescr(itemCD)
        raise itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES or AssertionError
        vehicle = self._data.getRootItem()
        if not vehicle.isInInventory:
            raise AssertionError('Vehicle must be in inventory')
            item = self._data.getItem(itemCD)
            conflictedEqs = item.getConflictedEquipments(vehicle)
            if not inInventory:
                Waiting.show('buyItem')
                buyResult = yield ModuleBuyer(item, count=1, buyForCredits=True, conflictedEqs=conflictedEqs, install=True).request()
                Waiting.hide('buyItem')
                if len(buyResult.userMsg):
                    SystemMessages.g_instance.pushI18nMessage(buyResult.userMsg, type=buyResult.sysMsgType)
                if buyResult.success:
                    item = self._data.getItem(itemCD)
                else:
                    return
            else:
                RequestState.sent(state)
            if item.isInInventory:
                Waiting.show('applyModule')
                result = yield getInstallerProcessor(vehicle, item, conflictedEqs=conflictedEqs).request()
                if result and result.auxData:
                    for m in result.auxData:
                        SystemMessages.g_instance.pushI18nMessage(m.userMsg, type=m.sysMsgType)

                if result and len(result.userMsg):
                    SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
                vehicle = result.success and item.itemTypeID in (GUI_ITEM_TYPE.TURRET, GUI_ITEM_TYPE.GUN) and g_itemsCache.items.getItemByCD(vehicle.intCD)
                yield tryToLoadDefaultShellsLayout(vehicle)
            Waiting.hide('applyModule')
        RequestState.received(state)

    @process
    def sellItem(self, itemTypeCD):
        item = self._data.getItem(itemTypeCD)
        if item.isInInventory:
            yield DialogsInterface.showDialog(LocalSellModuleMeta(itemTypeCD))
        else:
            self._showMessage(self.MSG_SCOPE.Inventory, 'not_found', itemTypeCD)
            yield lambda callback = None: callback
        return

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

    def invalidateVehLocks(self, locks):
        if self._data.invalidateLocks(locks):
            self.redraw()

    def invalidateWalletStatus(self, status):
        self.invalidateFreeXP()
        self.as_setWalletStatusS(status)
