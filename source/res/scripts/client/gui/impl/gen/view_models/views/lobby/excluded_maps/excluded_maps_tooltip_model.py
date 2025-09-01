# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/excluded_maps/excluded_maps_tooltip_model.py
from frameworks.wulf import ViewModel

class ExcludedMapsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ExcludedMapsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getMapCount(self):
        return self._getNumber(0)

    def setMapCount(self, value):
        self._setNumber(0, value)

    def getMaxCooldownTimeStr(self):
        return self._getString(1)

    def setMaxCooldownTimeStr(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(ExcludedMapsTooltipModel, self)._initialize()
        self._addNumberProperty('mapCount', 0)
        self._addStringProperty('maxCooldownTimeStr', '')
