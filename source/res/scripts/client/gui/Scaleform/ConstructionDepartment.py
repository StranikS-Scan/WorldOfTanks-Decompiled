# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/ConstructionDepartment.py
# Compiled at: 2018-11-29 14:33:44
from AccountCommands import RES_SUCCESS
from account_helpers.Inventory import _VEHICLE
from adisp import process
import BigWorld, Keys
from CurrentVehicle import g_currentVehicle
from constants import IS_DEVELOPMENT
from debug_utils import LOG_DEBUG, LOG_ERROR
from items import getTypeOfCompactDescr, ITEM_TYPE_INDICES, ITEM_TYPE_NAMES, vehicles
from gui.Scaleform.graphs import custom_items, INVENTORY_ITEM_VCDESC_IDX, CLIENT_DATA_DIFF_STAT_IDX, CLIENT_DATA_DIFF_INVENTORY_IDX
from gui import SystemMessages, SystemMessages, GUI_NATIONS
from gui.Scaleform.graphs.dumpers import VehiclesGraphXMLDumper
from gui.Scaleform.graphs.data import VehiclesGraph
from gui.Scaleform.graphs.trees_display_info import g_treeDisplayInfo
from gui.Scaleform.graphs.MessagesInterface import MessagesInterface
from gui.Scaleform.graphs.ResearchInterface import ResearchInterface
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.utils import gui_items
from gui.Scaleform.utils.requesters import StatsRequester
from functools import partial
import nations
from PlayerEvents import g_playerEvents

class SelectedNationHolder(object):
    __nationName = None

    def initNation(self):
        if self.__nationName is None:
            nationIdx = g_currentVehicle.vehicle.nation if g_currentVehicle.isPresent() else 0
            self.__nationName = GUI_NATIONS[nationIdx]
        return

    def getName(self):
        return self.__nationName

    def setName(self, name):
        if name in GUI_NATIONS:
            if name in nations.AVAILABLE_NAMES:
                self.__nationName = name


g_selectedNation = SelectedNationHolder()

class ConstructionDepartment(UIInterface, MessagesInterface):
    __unlocks = set()
    __experiences = {}
    __eliteVehicles = set()
    __availableNations = g_treeDisplayInfo.getAvailableNations()

    def __init__(self):
        super(ConstructionDepartment, self).__init__()
        self.vehiclesData = VehiclesGraph()
        self.vehiclesData.setDumper(VehiclesGraphXMLDumper())
        self.researchInterface = ResearchInterface()
        g_selectedNation.initNation()

    def __del__(self):
        LOG_DEBUG('ConstructionDepartment deleted')

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.researchInterface.populateUI(proxy)
        g_playerEvents.onClientUpdated += self.__pe_onClientUpdated
        g_playerEvents.onShopResync += self.onShopResync
        self.uiHolder.addExternalCallbacks({'LevelingTreeOfVehicles.RequestAvailableNations': self.onRequestAvailableNations,
         'LevelingTreeOfVehicles.RequestSelectedNation': self.onRequestSelectedNation,
         'LevelingTreeOfVehicles.RequestData': self.onRequestData,
         'LevelingTreeOfVehicles.RequestForVehicleBuy': self.onVehicleBuy})
        if IS_DEVELOPMENT:
            self.uiHolder.bindExCallbackToKey(Keys.KEY_R, 'LevelingTreeOfVehicles.ReloadData', self.__handleReloadData)
        self.__startDataCollect()

    def dispossessUI(self):
        self.uiHolder.removeExternalCallbacks('LevelingTreeOfVehicles.RequestAvailableNations', 'LevelingTreeOfVehicles.RequestSelectedNation', 'LevelingTreeOfVehicles.RequestData', 'LevelingTreeOfVehicles.RequestForVehicleBuy')
        self.researchInterface.dispossessUI()
        g_playerEvents.onClientUpdated -= self.__pe_onClientUpdated
        g_playerEvents.onShopResync -= self.onShopResync
        if IS_DEVELOPMENT:
            self.uiHolder.clearExCallbackToKey(Keys.KEY_R, 'LevelingTreeOfVehicles.ReloadData')
        UIInterface.dispossessUI(self)

    def __pe_onClientUpdated(self, diff):
        stats = diff.get(CLIENT_DATA_DIFF_STAT_IDX, {})
        if 'unlocks' in stats:
            self.__unlocks |= stats['unlocks']
            self.__setUnlocks(stats['unlocks'])
        if 'vehTypeXP' in stats:
            self.__experiences.update(stats['vehTypeXP'])
            self.__setVehicleTypeXP(stats['vehTypeXP'])
        if 'eliteVehicles' in stats:
            self.__eliteVehicles |= stats['eliteVehicles']
            self.__setEliteVehicles(stats['eliteVehicles'])
        inventory = diff.get(CLIENT_DATA_DIFF_INVENTORY_IDX, {})
        invVehs = inventory.get(_VEHICLE)
        if invVehs is not None:
            self.__setInventoryData(invVehs)
            vehInvID = -1
            if g_currentVehicle.isPresent():
                vehInvID = g_currentVehicle.vehicle.inventoryId
            if invVehs.get(INVENTORY_ITEM_VCDESC_IDX, {}).get(vehInvID) is not None:
                g_currentVehicle.update()
                if inventory.get(ITEM_TYPE_INDICES['vehicleTurret']) is not None or inventory.get(ITEM_TYPE_INDICES['vehicleGun']):
                    from gui.Scaleform.utils.HangarSpace import g_hangarSpace
                    g_hangarSpace.refreshVehicle()
        return

    def onRequestAvailableNations(self, *args):
        parser = CommandArgsParser(self.onRequestAvailableNations.__name__)
        parser.parse(*args)
        parser.addArgs(self.__availableNations[:])
        self.uiHolder.respond(parser.args())

    def onRequestSelectedNation(self, *args):
        parser = CommandArgsParser(self.onRequestSelectedNation.__name__)
        parser.parse(*args)
        parser.addArg(g_selectedNation.getName())
        self.uiHolder.respond(parser.args())

    def onRequestData(self, *args):
        parser = CommandArgsParser(self.onRequestData.__name__, 1)
        nationName = parser.parse(*args)
        g_selectedNation.setName(nationName)
        nationId = nations.INDICES.get(nationName, None)
        self.vehiclesData.load(nationId, self.__unlocks, self.__eliteVehicles, self.__experiences)
        parser.addArg(self.vehiclesData.dump())
        self.uiHolder.respond(parser.args())
        return

    def onVehicleBuy(self, *args):
        parser = CommandArgsParser(self.onVehicleBuy.__name__, 1, [int])
        intCompDescr = parser.parse(*args)
        _, nationID, innationID = vehicles.parseIntCompactDescr(intCompDescr)
        if not self.vehiclesData.hasInvItem(intCompDescr):
            price = self.vehiclesData.getShopPrice(intCompDescr)
            if price is None:
                self._showMessageForVehicle('vehicle_not_found_in_shop', nationID, innationID)
                return
            self.__showVehicleBuyDialog(nationID, innationID, price)
        else:
            self._showMessageForVehicle('vehicle_has_in_inventory', nationID, innationID, type=SystemMessages.SM_TYPE.Warning)
        return

    def __refreshData(self):
        self.call('LevelingTreeOfVehicles.RefreshData')

    def __setInventoryData(self, data):
        vCompactDescrs = data.get(INVENTORY_ITEM_VCDESC_IDX, {})
        vehicleTypeName = ITEM_TYPE_NAMES[_VEHICLE]
        for invID, vCompactDescr in vCompactDescrs.iteritems():
            vType = vehicles.getVehicleType(vCompactDescr)
            intCompactDescr = vehicles.makeIntCompactDescrByID(vehicleTypeName, vType.id[0], vType.id[1])
            self.vehiclesData.setInvItem(intCompactDescr, custom_items._makeInventoryVehicle(invID, vCompactDescr, data))

        self.call('LevelingTreeOfVehicles.SetInventoryVehicles', self.vehiclesData.getInventoryItemsCDs())

    def __setUnlocks(self, unlocks):
        vUnlocks = filter(lambda unlock: getTypeOfCompactDescr(unlock) == ITEM_TYPE_INDICES['vehicle'], unlocks)
        if len(vUnlocks) > 0:
            self.call('LevelingTreeOfVehicles.SetVehicleUnlocks', list(vUnlocks))

    def __setVehicleTypeXP(self, vTypeXP):
        args = []
        for vCompactDescr, xp in vTypeXP.iteritems():
            args.append(vCompactDescr)
            args.append(xp)

        self.call('LevelingTreeOfVehicles.SetVehicleTypeXP', args)

    def __setEliteVehicles(self, eliteVehicles):
        self.call('LevelingTreeOfVehicles.SetEliteVehicles', list(eliteVehicles))

    @process
    def __startDataCollect(self):
        if not Waiting.isVisible():
            Waiting.show('loadPage')
        self.__experiences = yield StatsRequester().getVehicleTypeExperiences()
        self.__unlocks = yield StatsRequester().getUnlocks()
        self.__eliteVehicles = yield StatsRequester().getEliteVehicles()
        self.__requestVehiclesFromInv()

    def __requestVehiclesFromInv(self):
        BigWorld.player().inventory.getItems(_VEHICLE, self.__onGetVehiclesFromInventory)

    def __onGetVehiclesFromInventory(self, resultID, data):
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error inventory vehicle items request: responseCode=', resultID)
            data = {INVENTORY_ITEM_VCDESC_IDX: {}}
        self.__setInventoryData(data)
        self.__requestVehiclesFromShop(nations.INDICES.values())

    def __requestVehiclesFromShop(self, nationIDs):
        if len(nationIDs) > 0:
            next = nationIDs.pop()
            BigWorld.player().shop.getItems(_VEHICLE, next, partial(self.__onGetVehiclesFromShop, next, nationIDs))
        else:
            self.__stopDataCollect()

    def __onGetVehiclesFromShop(self, nationID, nationIDs, resultID, data, _):
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error shop vehicles request: responseCode=' % resultID)
            data = {}
        prices = data[0].iteritems() if len(data) else []
        for innationID, price in prices:
            intCompactDescr = vehicles.makeIntCompactDescrByID(ITEM_TYPE_NAMES[_VEHICLE], nationID, innationID)
            self.vehiclesData.setShopPrice(intCompactDescr, price)

        self.__requestVehiclesFromShop(nationIDs)

    def __stopDataCollect(self):
        self.call('LevelingTreeOfVehicles.DataInitialized')
        Waiting.hide('loadPage')

    @process
    def __showVehicleBuyDialog(self, nationIdx, innationIdx, buyPrice):
        credits = yield StatsRequester().getCredits()
        gold = yield StatsRequester().getGold()
        if (credits, gold) >= buyPrice:
            self.call('common.showVehicleBuyDialog', [gui_items.ShopItem('vehicle', innationIdx, nation=nationIdx, priceOrder=buyPrice).pack()])
        else:
            _credits = buyPrice[0] - credits if buyPrice[0] > 0 else 0
            _gold = buyPrice[1] - gold if buyPrice[1] > 0 else 0
            self._showMessageForVehicle('vehicle_not_enough_money', nationIdx, innationIdx, {'price': gui_items.formatPrice([_credits, _gold])})

    def __handleReloadData(self, _, isDown):
        if not isDown:
            g_treeDisplayInfo.load(reload=True)
            self.__refreshData()

    def onShopResync(self):
        self.__requestVehiclesFromShop(nations.INDICES.values())
        self.__refreshData()
