# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/main_tank_setup_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_boosters_setup_model import BattleBoostersSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.consumables_setup_model import ConsumablesSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.frontline_setup_model import FrontlineSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.opt_devices_setup_model import OptDevicesSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.shells_setup_model import ShellsSetupModel

class MainTankSetupModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(MainTankSetupModel, self).__init__(properties=properties, commands=commands)

    @property
    def consumablesSetup(self):
        return self._getViewModel(0)

    @property
    def shellsSetup(self):
        return self._getViewModel(1)

    @property
    def battleBoostersSetup(self):
        return self._getViewModel(2)

    @property
    def optDevicesSetup(self):
        return self._getViewModel(3)

    @property
    def frontlineSetup(self):
        return self._getViewModel(4)

    def getSelectedSetup(self):
        return self._getString(5)

    def setSelectedSetup(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(MainTankSetupModel, self)._initialize()
        self._addViewModelProperty('consumablesSetup', ConsumablesSetupModel())
        self._addViewModelProperty('shellsSetup', ShellsSetupModel())
        self._addViewModelProperty('battleBoostersSetup', BattleBoostersSetupModel())
        self._addViewModelProperty('optDevicesSetup', OptDevicesSetupModel())
        self._addViewModelProperty('frontlineSetup', FrontlineSetupModel())
        self._addStringProperty('selectedSetup', '')
