# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/battle/cosmic_hud/loot_marker_model.py
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.marker_model import MarkerModel

class LootMarkerModel(MarkerModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(LootMarkerModel, self).__init__(properties=properties, commands=commands)

    def getDistance(self):
        return self._getNumber(5)

    def setDistance(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(LootMarkerModel, self)._initialize()
        self._addNumberProperty('distance', 0)
