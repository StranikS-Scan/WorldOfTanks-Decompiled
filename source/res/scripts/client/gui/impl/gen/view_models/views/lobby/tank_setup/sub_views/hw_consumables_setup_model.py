# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/hw_consumables_setup_model.py
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel

class HwConsumablesSetupModel(BaseSetupModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=7):
        super(HwConsumablesSetupModel, self).__init__(properties=properties, commands=commands)

    def getTempString(self):
        return self._getString(5)

    def setTempString(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(HwConsumablesSetupModel, self)._initialize()
        self._addStringProperty('tempString', '')
