# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/ammunition_panel_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_hints_model import UserHintsModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_panel_model import AmmunitionPanelModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_action_model import TankSetupActionModel

class AmmunitionPanelViewModel(ViewModel):
    __slots__ = ('onViewSizeInitialized',)

    def __init__(self, properties=8, commands=1):
        super(AmmunitionPanelViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def ammunitionPanel(self):
        return self._getViewModel(0)

    @property
    def lastSlotAction(self):
        return self._getViewModel(1)

    @property
    def hints(self):
        return self._getViewModel(2)

    def getIsMaintenanceEnabled(self):
        return self._getBool(3)

    def setIsMaintenanceEnabled(self, value):
        self._setBool(3, value)

    def getIsDisabled(self):
        return self._getBool(4)

    def setIsDisabled(self, value):
        self._setBool(4, value)

    def getIsReady(self):
        return self._getBool(5)

    def setIsReady(self, value):
        self._setBool(5, value)

    def getIsBootcamp(self):
        return self._getBool(6)

    def setIsBootcamp(self, value):
        self._setBool(6, value)

    def getIsEvent(self):
        return self._getBool(7)

    def setIsEvent(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(AmmunitionPanelViewModel, self)._initialize()
        self._addViewModelProperty('ammunitionPanel', AmmunitionPanelModel())
        self._addViewModelProperty('lastSlotAction', TankSetupActionModel())
        self._addViewModelProperty('hints', UserHintsModel())
        self._addBoolProperty('isMaintenanceEnabled', True)
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isReady', False)
        self._addBoolProperty('isBootcamp', False)
        self._addBoolProperty('isEvent', False)
        self.onViewSizeInitialized = self._addCommand('onViewSizeInitialized')
