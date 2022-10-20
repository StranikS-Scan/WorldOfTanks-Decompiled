# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/vehicle_compare_ammunition_panel_model.py
from gui.impl.gen.view_models.views.lobby.tank_setup.ammunition_panel_view_model import AmmunitionPanelViewModel

class VehicleCompareAmmunitionPanelModel(AmmunitionPanelViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=8, commands=3):
        super(VehicleCompareAmmunitionPanelModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(VehicleCompareAmmunitionPanelModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
