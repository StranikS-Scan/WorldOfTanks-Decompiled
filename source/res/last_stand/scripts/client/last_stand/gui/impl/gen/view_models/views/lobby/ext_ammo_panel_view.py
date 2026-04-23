# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/ext_ammo_panel_view.py
from gui.impl.gen.view_models.views.lobby.loadout.panel.ammunition.ammunition_panel_model import AmmunitionPanelModel

class ExtAmmoPanelView(AmmunitionPanelModel):
    __slots__ = ('onSwitch',)

    def __init__(self, properties=6, commands=3):
        super(ExtAmmoPanelView, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ExtAmmoPanelView, self)._initialize()
        self.onSwitch = self._addCommand('onSwitch')
