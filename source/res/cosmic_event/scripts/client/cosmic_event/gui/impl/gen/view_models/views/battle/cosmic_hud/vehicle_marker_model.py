# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/battle/cosmic_hud/vehicle_marker_model.py
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.marker_model import MarkerModel

class VehicleMarkerModel(MarkerModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(VehicleMarkerModel, self).__init__(properties=properties, commands=commands)

    def getPlayerName(self):
        return self._getString(4)

    def setPlayerName(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(VehicleMarkerModel, self)._initialize()
        self._addStringProperty('playerName', '')
