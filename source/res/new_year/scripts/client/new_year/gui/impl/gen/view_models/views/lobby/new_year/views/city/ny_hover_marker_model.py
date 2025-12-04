# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/city/ny_hover_marker_model.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.ny_marker_model import NyMarkerModel

class NyHoverMarkerModel(NyMarkerModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(NyHoverMarkerModel, self).__init__(properties=properties, commands=commands)

    def getIsZoneHovered(self):
        return self._getBool(5)

    def setIsZoneHovered(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(NyHoverMarkerModel, self)._initialize()
        self._addBoolProperty('isZoneHovered', False)
