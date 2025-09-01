# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/ext_ammo_panel_view.py
from gui.impl.gen.view_models.views.lobby.tank_setup.ammunition_panel_view_model import AmmunitionPanelViewModel

class ExtAmmoPanelView(AmmunitionPanelViewModel):
    __slots__ = ('onSwitch',)

    def __init__(self, properties=7, commands=2):
        super(ExtAmmoPanelView, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ExtAmmoPanelView, self)._initialize()
        self.onSwitch = self._addCommand('onSwitch')
