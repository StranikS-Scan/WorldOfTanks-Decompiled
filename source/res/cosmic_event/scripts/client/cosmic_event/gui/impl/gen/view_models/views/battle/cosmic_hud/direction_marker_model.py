# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/battle/cosmic_hud/direction_marker_model.py
from enum import Enum
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.marker_model import MarkerModel

class DirectionMarkerType(Enum):
    CORAL = 'coral'
    ARTIFACT_ZONE = 'artifactZone'


class DirectionMarkerModel(MarkerModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(DirectionMarkerModel, self).__init__(properties=properties, commands=commands)

    def getDistance(self):
        return self._getNumber(5)

    def setDistance(self, value):
        self._setNumber(5, value)

    def getAngle(self):
        return self._getReal(6)

    def setAngle(self, value):
        self._setReal(6, value)

    def getMarkerVisibility(self):
        return self._getBool(7)

    def setMarkerVisibility(self, value):
        self._setBool(7, value)

    def getMarkerType(self):
        return DirectionMarkerType(self._getString(8))

    def setMarkerType(self, value):
        self._setString(8, value.value)

    def getMarkerTimer(self):
        return self._getNumber(9)

    def setMarkerTimer(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(DirectionMarkerModel, self)._initialize()
        self._addNumberProperty('distance', 0)
        self._addRealProperty('angle', 0.0)
        self._addBoolProperty('markerVisibility', False)
        self._addStringProperty('markerType')
        self._addNumberProperty('markerTimer', 0)
