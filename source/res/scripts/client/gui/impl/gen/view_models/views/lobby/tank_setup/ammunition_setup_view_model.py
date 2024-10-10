# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/ammunition_setup_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ability_slot_model import AbilitySlotModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_panel_model import AmmunitionPanelModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.role_skill_slot_model import RoleSkillSlotModel
from gui.impl.gen.view_models.views.lobby.tank_setup.main_tank_setup_model import MainTankSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_action_model import TankSetupActionModel

class AmmunitionSetupViewModel(ViewModel):
    __slots__ = ('onClose', 'onResized', 'onViewRendered', 'onAnimationEnd')

    def __init__(self, properties=9, commands=4):
        super(AmmunitionSetupViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def tankSetup(self):
        return self._getViewModel(0)

    @staticmethod
    def getTankSetupType():
        return MainTankSetupModel

    @property
    def ammunitionPanel(self):
        return self._getViewModel(1)

    @staticmethod
    def getAmmunitionPanelType():
        return AmmunitionPanelModel

    @property
    def lastSlotAction(self):
        return self._getViewModel(2)

    @staticmethod
    def getLastSlotActionType():
        return TankSetupActionModel

    @property
    def vehicleInfo(self):
        return self._getViewModel(3)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    @property
    def roleSkillSlot(self):
        return self._getViewModel(4)

    @staticmethod
    def getRoleSkillSlotType():
        return RoleSkillSlotModel

    @property
    def abilitySlot(self):
        return self._getViewModel(5)

    @staticmethod
    def getAbilitySlotType():
        return AbilitySlotModel

    def getShow(self):
        return self._getBool(6)

    def setShow(self, value):
        self._setBool(6, value)

    def getIsReady(self):
        return self._getBool(7)

    def setIsReady(self, value):
        self._setBool(7, value)

    def getIsBootcamp(self):
        return self._getBool(8)

    def setIsBootcamp(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(AmmunitionSetupViewModel, self)._initialize()
        self._addViewModelProperty('tankSetup', MainTankSetupModel())
        self._addViewModelProperty('ammunitionPanel', AmmunitionPanelModel())
        self._addViewModelProperty('lastSlotAction', TankSetupActionModel())
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addViewModelProperty('roleSkillSlot', RoleSkillSlotModel())
        self._addViewModelProperty('abilitySlot', AbilitySlotModel())
        self._addBoolProperty('show', False)
        self._addBoolProperty('isReady', False)
        self._addBoolProperty('isBootcamp', False)
        self.onClose = self._addCommand('onClose')
        self.onResized = self._addCommand('onResized')
        self.onViewRendered = self._addCommand('onViewRendered')
        self.onAnimationEnd = self._addCommand('onAnimationEnd')
