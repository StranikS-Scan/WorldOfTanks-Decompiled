# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/tank_setup_panel_view.py
from battle_royale.gui.Scaleform.daapi.view.lobby.respawn_ability import RespawnAbility
from battle_royale.gui.impl.gen.view_models.views.lobby.views.tank_setup_panel_view_model import TankSetupPanelViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.consumable_model import ConsumableModel
from collections import namedtuple
from battle_royale.gui.constants import AmmoTypes
from battle_royale.gui.impl.lobby.tooltips.ability_tooltip_view import AbilityTooltipView
from battle_royale.gui.impl.lobby.tooltips.respawn_tooltip_view import RespawnTooltipView
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from CurrentVehicle import g_currentVehicle
from adisp import adisp_process
from battle_royale.gui.impl.lobby.tank_setup.dialogs.need_repair import NeedRepairBattleRoyale
from battle_royale.gui.impl.lobby.tank_setup.dialogs.need_repair import NeedRepairMainContentBattleRoyale
from frameworks.wulf import ViewFlags, ViewSettings, Array
from gui import SystemMessages
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import isIncorrectVehicle
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.gui_items.items_actions.actions import VehicleRepairAction
from gui.shared.gui_items.processors.vehicle import VehicleRepairer
from gui.shared.items_parameters.params import ShellParams
from gui.shared.utils import decorators
from helpers import dependency
from items import vehicles, EQUIPMENT_TYPES
from helpers.time_utils import ONE_MINUTE
from gui.impl.backport.backport_tooltip import createTooltipData, BackportTooltipWindow
from skeletons.gui.game_control import IBattleRoyaleController
_ArtefactData = namedtuple('_ArtefactData', ('intCD', 'quantity', 'icon', 'tooltipType'))
_AbilityTooltipData = namedtuple('_AbilityTooltipData', ('title', 'iconName', 'cooldownSeconds', 'description'))
_RespawnTooltipData = namedtuple('_RespawnTooltipData', ('platoonTimeToRessurect', 'platoonRespawnPeriod', 'soloRespawnPeriod'))
_DEFAULT_SLOT_VALUE = 1
_RESPAWN_DATA = {'iconName': 'respawn',
 'quantity': 0,
 'intCD': -1,
 'tooltipType': TankSetupPanelViewModel.TOOLTIP_RESPAWN}

def createEquipmentById(equipmentId):
    return vehicles.g_cache.equipments()[equipmentId]


class TankSetupPanelComponent(InjectComponentAdaptor):

    def _onPopulate(self):
        g_currentVehicle.onChanged += self.__updateInjectView
        self.__updateInjectView()

    def _dispose(self):
        g_currentVehicle.onChanged -= self.__updateInjectView
        super(TankSetupPanelComponent, self)._dispose()

    def _makeInjectView(self):
        return TankSetupPanelView()

    def __updateInjectView(self):
        if not isIncorrectVehicle(g_currentVehicle.item):
            if self._injectView is None:
                self._createInjectView()
            else:
                self._injectView.onCurrentVehicleChanged()
        return


class TankSetupPanelView(ViewImpl, IGlobalListener):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self):
        settings = ViewSettings(R.views.battle_royale.lobby.views.TankSetupPanelView())
        settings.flags = ViewFlags.VIEW
        settings.model = TankSetupPanelViewModel()
        super(TankSetupPanelView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TankSetupPanelView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TankSetupPanelView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__updateModel()

    def _finalize(self):
        self.__removeListeners()
        self.__removeListeners()
        super(TankSetupPanelView, self)._finalize()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.battle_royale.lobby.tooltips.AbilityTooltipView():
            tooltipData = self.__getTooltipData(event)
            return AbilityTooltipView(tooltipData)
        if contentID == R.views.battle_royale.lobby.tooltips.RespawnTooltipView():
            tooltipData = self.__getTooltipData(event)
            return RespawnTooltipView(tooltipData)
        return super(TankSetupPanelView, self).createToolTipContent(event, contentID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(TankSetupPanelView, self).createToolTip(event)

    def __getTooltipData(self, event):
        tooltipType = event.getArgument('tooltipType')
        intCD = event.getArgument('intCD')
        if not tooltipType or not intCD:
            return None
        elif tooltipType == TankSetupPanelViewModel.TOOLTIP_RESPAWN:
            return self.__getRespawnTooltipData()
        else:
            return self.__getAbilityTooltipData(intCD) if tooltipType == TankSetupPanelViewModel.TOOLTIP_ABILITY else self.__getAmmoTooltipData(intCD)

    def __getAbilityTooltipData(self, intCD):
        module = vehicles.g_cache.equipments()[intCD]
        cooldownSeconds = self.__getCooldownTime(module)
        description = self.__getDescription(module)
        return _AbilityTooltipData(title=module.userString, iconName=module.iconName, cooldownSeconds=cooldownSeconds, description=description)

    @staticmethod
    def __getRespawnTooltipData():
        respawnData = RespawnAbility()
        platoonTimeToRessurect = respawnData.getPlatoonTimeToRessurect()
        platoonRespawnPeriod = respawnData.getPlatoonRespawnPeriod() / ONE_MINUTE
        soloRespawnPeriod = respawnData.getSoloRespawnPeriod() / ONE_MINUTE
        return _RespawnTooltipData(platoonTimeToRessurect=platoonTimeToRessurect, platoonRespawnPeriod=platoonRespawnPeriod, soloRespawnPeriod=soloRespawnPeriod)

    @staticmethod
    def __getAmmoTooltipData(intCD):
        return createTooltipData(isSpecial=True, specialAlias=TankSetupPanelViewModel.TOOLTIP_SHELL, specialArgs=(intCD, _DEFAULT_SLOT_VALUE))

    @staticmethod
    def __getCooldownTime(item):
        return item.cooldownTime if hasattr(item, 'cooldownTime') else item.cooldownSeconds

    @staticmethod
    def __getDescription(item):
        descr = ''
        if item.equipmentType == EQUIPMENT_TYPES.regular:
            descr = item.longDescriptionSpecial
        elif item.equipmentType == EQUIPMENT_TYPES.battleAbilities:
            descr = item.longDescription
        return descr

    @decorators.adisp_process('updateMyVehicles')
    def __repair(self):
        vehicle = g_currentVehicle.item
        result = yield VehicleRepairer(vehicle).request()
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __addListeners(self):
        self.viewModel.onClick += self.__onClick
        self.__battleRoyaleController.onUpdated += self.__updateModel
        self.startGlobalListening()

    def __removeListeners(self):
        self.viewModel.onClick -= self.__onClick
        self.__battleRoyaleController.onUpdated -= self.__updateModel
        self.stopGlobalListening()

    @adisp_process
    def __onClick(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            yield VehicleRepairAction(vehicle, NeedRepairBattleRoyale, NeedRepairMainContentBattleRoyale).doAction()

    def onCurrentVehicleChanged(self):
        self.__updateModel()

    def __updateModel(self):
        vehicle = g_currentVehicle.item
        consumableArray = self.viewModel.getConsumable()
        consumableArray.clear()
        self.__setAmmo(vehicle, consumableArray)
        self.__setAbilities(vehicle, consumableArray)
        self.__setSpecialAbilities(consumableArray)
        self.__updateVehicleInfo()

    def __setAmmo(self, vehicle, items):
        self.__fillArtefactGroup(items, vehicle.shells.installed, False, vehicle)

    def __setAbilities(self, vehicle, items):
        vehicleEquipment = []
        vehicleEquipmentIds = self.__battleRoyaleController.getBrVehicleEquipmentIds(vehicle.name)
        if vehicleEquipmentIds is not None:
            vehicleEquipment = [ createEquipmentById(eqId) for eqId in vehicleEquipmentIds ]
        self.__fillArtefactGroup(items, vehicleEquipment, True, vehicle)
        return

    def __setSpecialAbilities(self, model):
        consumableArray = Array()
        itemModel = ConsumableModel()
        itemModel.setIconName(_RESPAWN_DATA.get('iconName'))
        itemModel.setQuantity(_RESPAWN_DATA.get('quantity'))
        itemModel.setIntCD(_RESPAWN_DATA.get('intCD'))
        itemModel.setTooltipType(_RESPAWN_DATA.get('tooltipType'))
        consumableArray.addViewModel(itemModel)
        model.addArray(consumableArray)
        model.invalidate()

    def __updateVehicleInfo(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            with self.viewModel.transaction() as vm:
                vm.setVehicleName(vehicle.userName)
                vm.setVehicleType(vehicle.type)
                vm.setIsVehicleInBattle(vehicle.isInBattle)

    def __fillArtefactGroup(self, model, artefactGroup, isEquipment, vehicle):
        if model is None:
            return
        else:
            consumable = Array()
            for artefact in artefactGroup:
                data = self.__getArtefactData(artefact, vehicle, isEquipment)
                itemModel = ConsumableModel()
                itemModel.setIconName(data.icon)
                itemModel.setQuantity(data.quantity)
                itemModel.setIntCD(data.intCD)
                itemModel.setTooltipType(data.tooltipType)
                consumable.addViewModel(itemModel)

            model.addArray(consumable)
            model.invalidate()
            return

    def __getArtefactData(self, artefact, vehicle, isEquipment):
        return self.__getAbilityData(artefact, vehicle.name) if isEquipment else self.__getAmmoData(artefact, vehicle)

    def __getAbilityData(self, equipment, vehicleName):
        intCD = equipment.id[1]
        count = self.__getEquipmentCount(AmmoTypes.ITEM, intCD, vehicleName)
        return _ArtefactData(intCD=intCD, quantity=count, icon=equipment.iconName, tooltipType=TankSetupPanelViewModel.TOOLTIP_ABILITY)

    def __getAmmoData(self, shell, vehicle):
        isBasic = ShellParams(shell.descriptor, vehicle.descriptor).isBasic
        ammoType = AmmoTypes.BASIC_SHELL if isBasic else AmmoTypes.PREMIUM_SHELL
        configCount = self.__getEquipmentCount(ammoType)
        count = max(configCount * vehicle.gun.maxAmmo if configCount < 1.0 else int(configCount), 0)
        return _ArtefactData(intCD=shell.intCD, quantity=count, icon=shell.descriptor.iconName, tooltipType=TankSetupPanelViewModel.TOOLTIP_SHELL)

    def __getEquipmentCount(self, typeKey, intCD=None, vehicleName=None):
        return self.__battleRoyaleController.getDefaultAmmoCount(typeKey, intCD, vehicleName)
