# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/hangar_bottom_panel_cmp.py
from collections import namedtuple
from battle_royale.gui.Scaleform.daapi.view.common.respawn_ability import RespawnAbility
from battle_royale.gui.constants import AmmoTypes
from CurrentVehicle import g_currentVehicle
from adisp import adisp_process
from battle_royale.gui.impl.lobby.tooltips.proxy_currency_tooltip_view import ProxyCurrencyTooltipView
from battle_royale.gui.impl.lobby.tooltips.rent_icon_tooltip_view import RentIconTooltipView
from battle_royale.gui.impl.lobby.tooltips.test_drive_info_tooltip_view import TestDriveInfoTooltipView
from battle_royale.gui.impl.lobby.tank_setup.dialogs.need_repair import NeedRepairBattleRoyale
from battle_royale.gui.impl.lobby.tank_setup.dialogs.need_repair import NeedRepairMainContentBattleRoyale
from frameworks.wulf import ViewFlags, ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import isIncorrectVehicle
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.backport.backport_tooltip import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle_royale.battle_royale_consumable_model import BattleRoyaleConsumableModel
from gui.impl.gen.view_models.views.battle_royale.equipment_panel_cmp_rent_states import EquipmentPanelCmpRentStates
from gui.impl.gen.view_models.views.battle_royale.equipment_panel_cmp_tooltips import EquipmentPanelCmpTooltips
from gui.impl.gen.view_models.views.battle_royale.hangar_bottom_panel_view_model import HangarBottomPanelViewModel
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.formatters.tankmen import getItemPricesViewModel
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.items_actions.actions import VehicleRepairAction
from gui.shared.gui_items.processors.vehicle import VehicleRepairer
from gui.shared.items_parameters.params import ShellParams
from gui.shared.utils import decorators
from helpers import dependency
from items import vehicles
from skeletons.gui.game_control import IBattleRoyaleController, IBattleRoyaleRentVehiclesController
from skeletons.gui.shared import IItemsCache
_DEFAULT_SLOT_VALUE = 1
_ArtefactData = namedtuple('_ArtefactData', ('intCD', 'quantity', 'icon', 'tooltip'))

def createEquipmentById(equipmentId):
    return vehicles.g_cache.equipments()[equipmentId]


class HangarBottomPanelComponent(InjectComponentAdaptor):

    def _makeInjectView(self):
        return HangarBottomPanelView(R.views.lobby.battleRoyale.hangar_bottom_panel_cmp.HangarBottomPanelCmp())


class HangarBottomPanelView(ViewImpl, IGlobalListener):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __rentVehiclesController = dependency.descriptor(IBattleRoyaleRentVehiclesController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewKey, viewModelClazz=HangarBottomPanelViewModel):
        settings = ViewSettings(viewKey)
        settings.flags = ViewFlags.VIEW
        settings.model = viewModelClazz()
        super(HangarBottomPanelView, self).__init__(settings)
        self.__isModuleViewed = False

    @property
    def viewModel(self):
        return super(HangarBottomPanelView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.battle_royale.lobby.tooltips.RentIconTooltipView():
            return RentIconTooltipView()
        if contentID == R.views.battle_royale.lobby.tooltips.ProxyCurrencyTooltipView():
            return ProxyCurrencyTooltipView()
        return TestDriveInfoTooltipView() if contentID == R.views.battle_royale.lobby.tooltips.TestDriveInfoTooltipView() else super(HangarBottomPanelView, self).createToolTipContent(event, contentID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(HangarBottomPanelView, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(HangarBottomPanelView, self)._initialize(*args, **kwargs)
        self.__addListeners()
        self.__updateModel()

    def _finalize(self):
        self.__removeListeners()
        self.__removeListeners()
        super(HangarBottomPanelView, self)._finalize()

    @decorators.adisp_process('updateMyVehicles')
    def __repair(self):
        vehicle = g_currentVehicle.item
        result = yield VehicleRepairer(vehicle).request()
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __addListeners(self):
        self.viewModel.onRentBtnClicked += self.__onRentBtnClicked
        self.viewModel.onRepairBtnClicked += self.__onRepairBtnClicked
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        g_clientUpdateManager.addMoneyCallback(self.__moneyUpdateCallback)
        self.__battleRoyaleController.onUpdated += self.__updateModel
        self.__rentVehiclesController.onUpdated += self.__updateRent
        self.__rentVehiclesController.onRentInfoUpdated += self.__updateRentState
        self.__rentVehiclesController.onPriceInfoUpdated += self.__updateRentPrice
        self.__subscribeRentTimeUpdate()
        self.startGlobalListening()

    def __removeListeners(self):
        self.__rentVehiclesController.clearRentUpdateCurrentVehicleCallback(self.__rentLiveUpdate)
        self.viewModel.onRentBtnClicked -= self.__onRentBtnClicked
        self.viewModel.onRepairBtnClicked -= self.__onRepairBtnClicked
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__battleRoyaleController.onUpdated -= self.__updateModel
        self.__rentVehiclesController.onUpdated -= self.__updateRent
        self.__rentVehiclesController.onRentInfoUpdated -= self.__updateRentState
        self.__rentVehiclesController.onPriceInfoUpdated -= self.__updateRentPrice
        self.stopGlobalListening()

    def __rentLiveUpdate(self):
        self.__updateRentState()

    def __onRentBtnClicked(self):
        self.__rentVehiclesController.purchaseRent()

    @adisp_process
    def __onRepairBtnClicked(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            yield VehicleRepairAction(vehicle, NeedRepairBattleRoyale, NeedRepairMainContentBattleRoyale).doAction()

    def __onCurrentVehicleChanged(self):
        self.__updateModel()
        self.__subscribeRentTimeUpdate()

    def __moneyUpdateCallback(self, *_):
        self.__updateRentPrice()

    def __updateModel(self):
        vehicle = g_currentVehicle.item
        if isIncorrectVehicle(vehicle):
            return
        self.__setAmmo(vehicle)
        self.__setAbilities(vehicle)
        self.__setSpecialAbilities()
        self.__updateRentPrice()
        self.__updateRentState()
        self.__updateVehicleInfo()

    def __setAmmo(self, vehicle):
        items = self.viewModel.ammunition.getItems()
        self.__fillArtefactGroup(items, vehicle.shells.installed, False, vehicle)

    def __setAbilities(self, vehicle):
        vehicleEquipment = []
        vehicleEquipmentIds = self.__battleRoyaleController.getBrVehicleEquipmentIds(vehicle.name)
        if vehicleEquipmentIds is not None:
            vehicleEquipment = [ createEquipmentById(eqId) for eqId in vehicleEquipmentIds ]
        items = self.viewModel.abilities.getItems()
        self.__fillArtefactGroup(items, vehicleEquipment, True, vehicle)
        return

    def __setSpecialAbilities(self):
        items = self.viewModel.specialAbilities.getItems()
        items.clear()
        itemModel = BattleRoyaleConsumableModel()
        itemModel.setIconSource(RespawnAbility.icon)
        itemModel.setQuantity(0)
        itemModel.setIntCD(-1)
        itemModel.setTooltipType(RespawnAbility.tooltipType)
        items.addViewModel(itemModel)
        items.invalidate()

    def __updateRentPrice(self):
        vehicle = g_currentVehicle.item
        if isIncorrectVehicle(vehicle):
            return
        else:
            items = self.viewModel.rentPrice.getItems()
            items.clear()
            price = self.__rentVehiclesController.getRentPrice()
            itemPrice = ItemPrice(price=price, defPrice=price)
            actionPriceModels = getItemPricesViewModel(self.__itemsCache.items.stats.getDynamicMoney(), itemPrice)[0]
            isEnoughMoney = self.__rentVehiclesController.isEnoughMoneyToPurchase()
            if actionPriceModels is not None:
                for model in actionPriceModels:
                    items.addViewModel(model)

            items.invalidate()
            self.viewModel.setIsEnoughMoney(isEnoughMoney)
            return

    def __updateVehicleInfo(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            with self.viewModel.transaction() as vm:
                vm.setVehName(vehicle.userName)
                vm.setVehType(vehicle.type)
                vm.setIsVehicleInBattle(vehicle.isInBattle)

    def __updateRent(self):
        self.__updateRentState()
        self.__updateRentPrice()

    def __updateRentState(self):
        state = self.__rentVehiclesController.getRentState()
        self.viewModel.setRentState(state)
        if state in (EquipmentPanelCmpRentStates.STATE_RENT_AVAILABLE, EquipmentPanelCmpRentStates.STATE_TEST_DRIVE_AVAILABLE):
            self.viewModel.setRentDays(self.__rentVehiclesController.getPendingRentDays())
        else:
            self.viewModel.setRentTime(self.__rentVehiclesController.getFormatedRentTimeLeft())

    def __fillArtefactGroup(self, items, artefactGroup, isEquipment, vehicle):
        if items is None:
            return
        else:
            items.clear()
            for artefact in artefactGroup:
                data = self.__getArtefactData(artefact, vehicle, isEquipment)
                itemModel = BattleRoyaleConsumableModel()
                itemModel.setIconSource(data.icon)
                itemModel.setQuantity(data.quantity)
                itemModel.setIntCD(data.intCD)
                itemModel.setTooltipType(data.tooltip)
                items.addViewModel(itemModel)

            items.invalidate()
            return

    def __getArtefactData(self, artefact, vehicle, isEquipment):
        return self.__getEquipmentData(artefact, vehicle.name) if isEquipment else self.__getAmmoData(artefact, vehicle)

    def __getAmmoData(self, shell, vehicle):
        isBasic = ShellParams(shell.descriptor, vehicle.descriptor).isBasic
        ammoType = AmmoTypes.BASIC_SHELL if isBasic else AmmoTypes.PREMIUM_SHELL
        configCount = self.__getEquipmentCount(ammoType)
        count = max(configCount * vehicle.gun.maxAmmo if configCount < 1.0 else int(configCount), 0)
        return _ArtefactData(intCD=shell.intCD, quantity=count, icon=R.images.gui.maps.icons.shell.small.dyn(shell.descriptor.iconName)(), tooltip=EquipmentPanelCmpTooltips.TOOLTIP_SHELL)

    def __getEquipmentData(self, equipment, vehicleName):
        intCD = equipment.id[1]
        count = self.__getEquipmentCount(AmmoTypes.ITEM, intCD, vehicleName)
        return _ArtefactData(intCD=intCD, quantity=count, icon=R.images.gui.maps.icons.battleRoyale.artefact.dyn(equipment.iconName)(), tooltip=EquipmentPanelCmpTooltips.TOOLTIP_EQUIPMENT)

    def __getEquipmentCount(self, typeKey, intCD=None, vehicleName=None):
        return self.__battleRoyaleController.getDefaultAmmoCount(typeKey, intCD, vehicleName)

    @staticmethod
    def __getTooltipData(event):
        tooltipType = event.getArgument('tooltipType')
        intCD = event.getArgument('intCD')
        return None if not tooltipType or not intCD else createTooltipData(isSpecial=True, specialAlias=tooltipType, specialArgs=(intCD, _DEFAULT_SLOT_VALUE))

    def __subscribeRentTimeUpdate(self):
        vehicle = g_currentVehicle.item
        if not isIncorrectVehicle(vehicle):
            self.__rentVehiclesController.setRentUpdateCurrentVehicleCallback(self.__rentLiveUpdate)
