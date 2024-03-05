# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/battle/cosmic_hud/direction_marker_model.py
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.marker_model import MarkerModel

class DirectionMarkerModel(MarkerModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(DirectionMarkerModel, self).__init__(properties=properties, commands=commands)

    def getDistance(self):
        return self._getNumber(4)

    def setDistance(self, value):
        self._setNumber(4, value)

    def getAngle(self):
        return self._getReal(5)

    def setAngle(self, value):
        self._setReal(5, value)

    def _initialize(self):
        super(DirectionMarkerModel, self)._initialize()
        self._addNumberProperty('distance', 0)
        self._addRealProperty('angle', 0.0)
