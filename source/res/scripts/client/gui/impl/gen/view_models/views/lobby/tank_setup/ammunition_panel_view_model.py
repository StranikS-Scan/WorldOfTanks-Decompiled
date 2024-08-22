# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/ammunition_panel_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_panel_model import AmmunitionPanelModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.role_skill_slot_model import RoleSkillSlotModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_action_model import TankSetupActionModel

class AmmunitionPanelViewModel(ViewModel):
    __slots__ = ('onEscKeyDown',)

    def __init__(self, properties=7, commands=1):
        super(AmmunitionPanelViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def ammunitionPanel(self):
        return self._getViewModel(0)

    @staticmethod
    def getAmmunitionPanelType():
        return AmmunitionPanelModel

    @property
    def lastSlotAction(self):
        return self._getViewModel(1)

    @staticmethod
    def getLastSlotActionType():
        return TankSetupActionModel

    @property
    def roleSkillSlot(self):
        return self._getViewModel(2)

    @staticmethod
    def getRoleSkillSlotType():
        return RoleSkillSlotModel

    def getVehicleCD(self):
        return self._getNumber(3)

    def setVehicleCD(self, value):
        self._setNumber(3, value)

    def getIsMaintenanceEnabled(self):
        return self._getBool(4)

    def setIsMaintenanceEnabled(self, value):
        self._setBool(4, value)

    def getIsDisabled(self):
        return self._getBool(5)

    def setIsDisabled(self, value):
        self._setBool(5, value)

    def getIsReady(self):
        return self._getBool(6)

    def setIsReady(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(AmmunitionPanelViewModel, self)._initialize()
        self._addViewModelProperty('ammunitionPanel', AmmunitionPanelModel())
        self._addViewModelProperty('lastSlotAction', TankSetupActionModel())
        self._addViewModelProperty('roleSkillSlot', RoleSkillSlotModel())
        self._addNumberProperty('vehicleCD', -1)
        self._addBoolProperty('isMaintenanceEnabled', True)
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isReady', False)
        self.onEscKeyDown = self._addCommand('onEscKeyDown')
