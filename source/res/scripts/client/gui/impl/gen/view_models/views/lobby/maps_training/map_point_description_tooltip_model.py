# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/maps_training/map_point_description_tooltip_model.py
from frameworks.wulf import ViewModel

class MapPointDescriptionTooltipModel(ViewModel):
    __slots__ = ()
    ARG_POINT_NAME = 'pointName'

    def __init__(self, properties=1, commands=0):
        super(MapPointDescriptionTooltipModel, self).__init__(properties=properties, commands=commands)

    def getPointName(self):
        return self._getString(0)

    def setPointName(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(MapPointDescriptionTooltipModel, self)._initialize()
        self._addStringProperty('pointName', '')
