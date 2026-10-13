# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/ext_ammo_panel_view.py
from gui.impl.gen.view_models.views.lobby.loadout.panel.ammunition.ammunition_panel_model import AmmunitionPanelModel

class ExtAmmoPanelView(AmmunitionPanelModel):
    __slots__ = ('onSwitch',)

    def __init__(self, properties=8, commands=3):
        super(ExtAmmoPanelView, self).__init__(properties=properties, commands=commands)

    def getAccelerationKeyName(self):
        return self._getString(6)

    def setAccelerationKeyName(self, value):
        self._setString(6, value)

    def getAccelerationIntCD(self):
        return self._getNumber(7)

    def setAccelerationIntCD(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(ExtAmmoPanelView, self)._initialize()
        self._addStringProperty('accelerationKeyName', '')
        self._addNumberProperty('accelerationIntCD', 0)
        self.onSwitch = self._addCommand('onSwitch')
