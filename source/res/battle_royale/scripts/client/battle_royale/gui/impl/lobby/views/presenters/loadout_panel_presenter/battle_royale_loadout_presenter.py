# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/presenters/loadout_panel_presenter/battle_royale_loadout_presenter.py
from helpers import dependency, time_utils
from items import EQUIPMENT_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub.view_component import ViewComponent
from skeletons.gui.game_control import IBattleRoyaleController
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_royale_shell_model import BattleRoyaleShellModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.loadout_view_model import LoadoutViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_royale_equipment_model import BattleRoyaleEquipmentModel
from battle_royale.gui.impl.lobby.br_helpers.respawn_ability import RespawnAbility
from battle_royale.gui.shared.event_dispatcher import showHangarVehicleConfigurator

class BattleRoyaleLoadoutPresenter(ViewComponent[LoadoutViewModel]):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, *args, **kwargs):
        self.__vehicle = None
        super(BattleRoyaleLoadoutPresenter, self).__init__(model=LoadoutViewModel, *args, **kwargs)
        return

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BattleRoyaleLoadoutPresenter, self).createToolTip(event)

    @staticmethod
    def getTooltipData(event):
        intCD = int(event.getArgument('intCD', 0))
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_MAIN_SHELL, specialArgs=(intCD,))

    def _getEvents(self):
        return super(BattleRoyaleLoadoutPresenter, self)._getEvents() + ((self.getViewModel().showUpgrades, self.__showUpgrades), (self.__battleRoyaleController.onUpdated, self.__updateModel))

    def _onLoading(self, *args, **kwargs):
        super(BattleRoyaleLoadoutPresenter, self)._onLoading()
        self.__updateModel()

    def _finalize(self):
        super(BattleRoyaleLoadoutPresenter, self)._finalize()
        self.__vehicle = None
        return

    def __updateModel(self, *_):
        if not self.__vehicle:
            return
        with self.getViewModel().transaction() as model:
            self.__setShells(self.__vehicle, model)
            self.__setEquipmentAndAbilities(self.__vehicle, model)
            self.__setRespawnAbility(model.respawnAbility)

    def __setShells(self, vehicle, model):
        shells = model.getShells()
        shells.clear()
        for shell, quantity in self.__battleRoyaleController.getVehicleShells(vehicle.name):
            shellModel = BattleRoyaleShellModel()
            shellModel.setIconName(shell.descriptor.iconName)
            shellModel.setIntCD(shell.intCD)
            shellModel.setQuantity(quantity)
            shells.addViewModel(shellModel)

        shells.invalidate()

    def __setEquipmentAndAbilities(self, vehicle, model):
        equipment = model.getEquipment()
        equipment.clear()
        for eq, quantity in self.__battleRoyaleController.getVehicleEquipment(vehicle.name):
            equipmentModel = BattleRoyaleEquipmentModel()
            equipmentModel.setIconName(eq.iconName)
            equipmentModel.setTitle(eq.userString)
            equipmentModel.setCooldownSeconds(eq.cooldownTime if hasattr(eq, 'cooldownTime') else eq.cooldownSeconds)
            equipmentModel.setIntCD(eq.id[1])
            equipmentModel.setQuantity(quantity)
            description = ''
            if eq.equipmentType == EQUIPMENT_TYPES.regular:
                description = eq.longDescriptionSpecial
            elif eq.equipmentType == EQUIPMENT_TYPES.battleAbilities:
                description = eq.longDescription
            equipmentModel.setDescription(description)
            equipment.addViewModel(equipmentModel)

        equipment.invalidate()

    @staticmethod
    def __setRespawnAbility(respawn):
        respawn.setPlatoonTimeToResurrect(RespawnAbility.getPlatoonTimeToResurrect())
        respawn.setPlatoonRespawnPeriod(RespawnAbility.getPlatoonRespawnPeriod() / time_utils.ONE_MINUTE)
        respawn.setSoloRespawnPeriod(RespawnAbility.getSoloRespawnPeriod() / time_utils.ONE_MINUTE)

    @staticmethod
    def __showUpgrades():
        showHangarVehicleConfigurator()

    def update(self, vehicle):
        self.__vehicle = vehicle
        self.__updateModel()
