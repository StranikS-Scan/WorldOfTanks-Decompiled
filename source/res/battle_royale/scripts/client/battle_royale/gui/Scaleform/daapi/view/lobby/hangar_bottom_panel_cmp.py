# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/hangar_bottom_panel_cmp.py
from collections import namedtuple
from battle_royale.gui.Scaleform.daapi.view.common.respawn_ability import RespawnAbility
from battle_royale.gui.constants import AmmoTypes
from CurrentVehicle import g_currentVehicle
from adisp import adisp_process
from battle_royale.gui.impl.lobby.tooltips.br_coin_tooltip_view import BrCoinTooltipView
from battle_royale.gui.impl.lobby.tank_setup.dialogs.need_repair import NeedRepairBattleRoyale
from battle_royale.gui.impl.lobby.tank_setup.dialogs.need_repair import NeedRepairMainContentBattleRoyale
from frameworks.wulf import ViewFlags, ViewSettings
from gui import SystemMessages
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import isIncorrectVehicle
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.backport.backport_tooltip import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle_royale.battle_royale_consumable_model import BattleRoyaleConsumableModel
from gui.impl.gen.view_models.views.battle_royale.equipment_panel_cmp_tooltips import EquipmentPanelCmpTooltips
from gui.impl.gen.view_models.views.battle_royale.hangar_bottom_panel_view_model import HangarBottomPanelViewModel
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.gui_items.items_actions.actions import VehicleRepairAction
from gui.shared.gui_items.processors.vehicle import VehicleRepairer
from gui.shared.items_parameters.params import ShellParams
from gui.shared.utils import decorators
from helpers import dependency
from items import vehicles
from skeletons.gui.game_control import IBattleRoyaleController
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
        return BrCoinTooltipView() if contentID == R.views.battle_royale.lobby.tooltips.BrCoinTooltipView() else super(HangarBottomPanelView, self).createToolTipContent(event, contentID)

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
        self.viewModel.onRepairBtnClicked += self.__onRepairBtnClicked
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self.__battleRoyaleController.onUpdated += self.__updateModel
        self.startGlobalListening()

    def __removeListeners(self):
        self.viewModel.onRepairBtnClicked -= self.__onRepairBtnClicked
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        self.__battleRoyaleController.onUpdated -= self.__updateModel
        self.stopGlobalListening()

    @adisp_process
    def __onRepairBtnClicked(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            yield VehicleRepairAction(vehicle, NeedRepairBattleRoyale, NeedRepairMainContentBattleRoyale).doAction()

    def __onCurrentVehicleChanged(self):
        self.__updateModel()

    def __updateModel(self):
        vehicle = g_currentVehicle.item
        if isIncorrectVehicle(vehicle):
            return
        self.__setAmmo(vehicle)
        self.__setAbilities(vehicle)
        self.__setSpecialAbilities()
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

    def __updateVehicleInfo(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            with self.viewModel.transaction() as vm:
                vm.setVehName(vehicle.userName)
                vm.setVehType(vehicle.type)
                vm.setIsVehicleInBattle(vehicle.isInBattle)

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
