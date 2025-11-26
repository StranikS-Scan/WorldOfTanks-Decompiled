# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/key_bindings_model.py
from gui.impl.gen.view_models.views.lobby.common.settings_model import SettingsModel
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_key_bindings_model import VehicleMenuKeyBindingsModel

class KeyBindingsModel(SettingsModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=1):
        super(KeyBindingsModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleMenu(self):
        return self._getViewModel(1)

    @staticmethod
    def getVehicleMenuType():
        return VehicleMenuKeyBindingsModel

    def _initialize(self):
        super(KeyBindingsModel, self)._initialize()
        self._addViewModelProperty('vehicleMenu', VehicleMenuKeyBindingsModel())
