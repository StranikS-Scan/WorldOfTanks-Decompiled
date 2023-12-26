# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_random_resource_tooltip_model.py
from frameworks.wulf import ViewModel

class NyRandomResourceTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyRandomResourceTooltipModel, self).__init__(properties=properties, commands=commands)

    def getResourceValue(self):
        return self._getNumber(0)

    def setResourceValue(self, value):
        self._setNumber(0, value)

    def getIsShownFromStore(self):
        return self._getBool(1)

    def setIsShownFromStore(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(NyRandomResourceTooltipModel, self)._initialize()
        self._addNumberProperty('resourceValue', 0)
        self._addBoolProperty('isShownFromStore', False)
