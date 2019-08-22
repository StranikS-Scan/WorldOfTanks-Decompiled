# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/hangar_bottom_panel_cmp.py
from collections import namedtuple
from adisp import process
from frameworks.wulf import ViewFlags
from account_helpers.AccountSettings import AccountSettings, BATTLE_ROYALE_HANGAR_BOTTOM_PANEL_VIEWED
from CurrentVehicle import g_currentVehicle
from gui import SystemMessages, DialogsInterface, makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.battle_control.controllers.consumables.br_equipment_ctrl import createEquipmentByName
from gui.battle_royale.constants import VEHICLE_EQUIPMENTS, AVATAR_EQUIPMENTS, EQUIPMENT_ORDER
from gui.battle_royale.constants import AmmoTypes
from gui.impl import backport
from gui.impl.backport.backport_system_locale import getIntegralFormat
from gui.impl.backport.backport_tooltip import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle_royale.hangar_bottom_panel_view_model import HangarBottomPanelViewModel
from gui.impl.gen.view_models.views.battle_royale.equipment_panel_cmp_tooltips import EquipmentPanelCmpTooltips
from gui.impl.gen.view_models.views.battle_royale.br_consum_model import BrConsumModel
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.Scaleform.daapi.view.common.battle_royale_helpers import isIncorrectVehicle
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.shared import event_dispatcher
from gui.shared.formatters.tankmen import getItemPricesViewModel
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.processors.vehicle import VehicleRepairer
from gui.shared.items_parameters.params import ShellParams
from gui.shared.money import Money, Currency
from gui.shared.utils import decorators
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.shared import IItemsCache
_PREFIX = 'no_'
_DEFAULT_SLOT_VALUE = 1
_ArtefactData = namedtuple('_ArtefactData', ('intCD', 'count', 'icon', 'tooltip'))

class HangarBottomPanelComponent(InjectComponentAdaptor):

    def _makeInjectView(self):
        return HangarBottomPanelView()


class HangarBottomPanelView(ViewImpl, IGlobalListener):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(HangarBottomPanelView, self).__init__(R.views.lobby.battleRoyale.hangar_bottom_panel_cmp.HangarBottomPanelCmp(), ViewFlags.COMPONENT, HangarBottomPanelViewModel, *args, **kwargs)
        self.__isModuleViewed = False

    @property
    def viewModel(self):
        return super(HangarBottomPanelView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(HangarBottomPanelView, self).createToolTip(event)

    def onPrbEntitySwitched(self):
        self.__updateVehicleStatus()

    def _initialize(self, *args, **kwargs):
        super(HangarBottomPanelView, self)._initialize(*args, **kwargs)
        self.__setRepairPrice()
        self.__addListeners()
        self.__updateModel()

    def _finalize(self):
        self.__removeListeners()
        super(HangarBottomPanelView, self)._finalize()

    @decorators.process('updateMyVehicles')
    def __repair(self):
        vehicle = g_currentVehicle.item
        result = yield VehicleRepairer(vehicle).request()
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __addListeners(self):
        self.viewModel.onModuleBtnClicked += self.__onModuleBtnClicked
        self.viewModel.onRepairBtnClicked += self.__onRepairBtnClicked
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        g_clientUpdateManager.addMoneyCallback(self.__moneyUpdateCallback)
        self.__battleRoyaleController.onUpdated += self.__updateModel
        self.startGlobalListening()

    def __removeListeners(self):
        self.viewModel.onModuleBtnClicked -= self.__onModuleBtnClicked
        self.viewModel.onModuleBtnClicked -= self.__onRepairBtnClicked
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__battleRoyaleController.onUpdated -= self.__updateModel
        self.stopGlobalListening()

    def __onModuleBtnClicked(self):
        event_dispatcher.showHangarVehicleConfigurator(not self.__isModuleViewed)

    @process
    def __onRepairBtnClicked(self):
        msg = backport.text(R.strings.dialogs.technicalMaintenanceConfirm.msg_repair())
        isConfirmed = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('technicalMaintenanceConfirm', messageCtx={'content': msg}))
        if isConfirmed and g_currentVehicle.item.isBroken:
            self.__repair()

    def __onCurrentVehicleChanged(self):
        self.__updateModel()

    def __moneyUpdateCallback(self, *_):
        self.__updateRepairPrice()

    def __updateModel(self):
        vehicle = g_currentVehicle.item
        if isIncorrectVehicle(vehicle):
            return
        self.__setAmmo(vehicle)
        self.__setPersonalConsumables()
        self.__setGlobalConsumables()
        self.__setRepairPrice()
        self.__updateRepairPrice()
        self.__updateVehicleStatus()
        self.__updateModuleButtonBubble()

    def __setAmmo(self, vehicle):
        items = self.viewModel.ammunition.getItems()
        self.__fillArtefactGroup(items, vehicle.shells, vehicle)

    def __setPersonalConsumables(self):
        items = self.viewModel.personalConsumables.getItems()
        self.__fillArtefactGroup(items, [ item for item in EQUIPMENT_ORDER if item in VEHICLE_EQUIPMENTS ])

    def __setGlobalConsumables(self):
        items = self.viewModel.globalConsumables.getItems()
        self.__fillArtefactGroup(items, [ item for item in EQUIPMENT_ORDER if item in AVATAR_EQUIPMENTS ])

    def __setRepairPrice(self):
        vehicle = g_currentVehicle.item
        if isIncorrectVehicle(vehicle):
            return
        items = self.viewModel.repairPrice.getItems()
        items.clear()
        repairCost = vehicle.repairCost
        itemPrice = ItemPrice(price=Money(credits=repairCost), defPrice=Money(credits=repairCost))
        actionPriceModels = getItemPricesViewModel(self.__itemsCache.items.stats.money, itemPrice)[0]
        for model in actionPriceModels:
            items.addViewModel(model)

        items.invalidate()

    def __updateRepairPrice(self):
        vehicle = g_currentVehicle.item
        if isIncorrectVehicle(vehicle):
            return
        repairCost = vehicle.repairCost
        isDissabled = False
        if repairCost <= 0:
            self.viewModel.setIsRepairBtnVisible(False)
            return
        self.viewModel.setIsRepairBtnVisible(True)
        with self.viewModel.transaction() as vm:
            repairPrice = vm.repairPrice.getItems()
            for model in repairPrice:
                statsMoney = self.__itemsCache.items.stats.money
                currencyType = model.getType()
                currencyValue = repairCost if currencyType == Currency.CREDITS else 0
                model.setPrice(getIntegralFormat(currencyValue))
                isEnough = currencyValue <= statsMoney.get(currencyType)
                model.setIsEnough(isEnough)
                if not isEnough:
                    isDissabled = True

        self.viewModel.setIsRepairBtnDisabled(isDissabled)

    def __updateVehicleStatus(self):
        if g_currentVehicle.isPresent():
            state, msgLvl = g_currentVehicle.item.getState()
            if state == Vehicle.VEHICLE_STATE.LOCKED:
                return
            message = R.strings.menu.currentVehicleStatus.dyn(state)()
            msgString = makeHtmlString('html_templates:vehicleStatus', msgLvl, {'message': backport.text(message)})
            if self.viewModel.getVehStatus() == msgString:
                return
            self.viewModel.setVehStatus(msgString)

    def __updateModuleButtonBubble(self):
        self.__isModuleViewed = AccountSettings.getSettings(BATTLE_ROYALE_HANGAR_BOTTOM_PANEL_VIEWED)
        self.viewModel.setIsModuleFirstEnter(not self.__isModuleViewed)

    def __fillArtefactGroup(self, items, artefactGroup, vehicle=None):
        if items is None:
            return
        else:
            items.clear()
            for artefact in artefactGroup:
                data = self.__getArtefactData(artefact, vehicle)
                itemModel = BrConsumModel()
                itemModel.setIconSource(data.icon)
                itemModel.setConsumValue(int(data.count))
                itemModel.setIntCD(data.intCD)
                itemModel.setTooltipType(data.tooltip)
                items.addViewModel(itemModel)

            items.invalidate()
            return

    def __getArtefactData(self, artefact, vehicle):
        return self.__getEquipmentData(artefact) if artefact in VEHICLE_EQUIPMENTS or artefact in AVATAR_EQUIPMENTS else self.__getAmmoData(artefact, vehicle)

    def __getAmmoData(self, shell, vehicle):
        isBasic = ShellParams(shell.descriptor, vehicle.descriptor).isBasic
        ammoType = AmmoTypes.BASIC_SHELL if isBasic else AmmoTypes.PREMIUM_SHELL
        count = self.__getEquipmentCount(ammoType) * vehicle.gun.maxAmmo
        return _ArtefactData(intCD=shell.intCD, count=count, icon=self.__getIconPath(shell.type.lower(), count), tooltip=EquipmentPanelCmpTooltips.TOOLTIP_SHELL)

    def __getEquipmentData(self, equipmentName):
        equipment = createEquipmentByName(equipmentName)
        intCD = equipment.id[1]
        count = self.__getEquipmentCount(AmmoTypes.ITEM, intCD)
        return _ArtefactData(intCD=intCD, count=count, icon=self.__getIconPath(equipment.iconName, count), tooltip=EquipmentPanelCmpTooltips.TOOLTIP_EQUIPMENT)

    def __getEquipmentCount(self, typeKey, intCD=None):
        return self.__battleRoyaleController.getDefaultAmmoCount(typeKey, intCD)

    @staticmethod
    def __getTooltipData(event):
        tooltipType = event.getArgument('tooltipType')
        intCD = event.getArgument('intCD')
        return None if not tooltipType or not intCD else createTooltipData(isSpecial=True, specialAlias=tooltipType, specialArgs=(intCD, _DEFAULT_SLOT_VALUE))

    @staticmethod
    def __getIconPath(itemName, count):
        if count <= 0:
            itemName = ''.join((_PREFIX, itemName))
        return R.images.gui.maps.icons.battleRoyale.artefact.dyn(itemName)()
