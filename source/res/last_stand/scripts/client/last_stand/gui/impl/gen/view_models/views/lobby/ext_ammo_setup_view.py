# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/ext_ammo_setup_view.py
from gui.impl.gen.view_models.views.lobby.tank_setup.ammunition_setup_view_model import AmmunitionSetupViewModel

class ExtAmmoSetupView(AmmunitionSetupViewModel):
    __slots__ = ('onSwitch',)

    def __init__(self, properties=8, commands=5):
        super(ExtAmmoSetupView, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ExtAmmoSetupView, self)._initialize()
        self.onSwitch = self._addCommand('onSwitch')
