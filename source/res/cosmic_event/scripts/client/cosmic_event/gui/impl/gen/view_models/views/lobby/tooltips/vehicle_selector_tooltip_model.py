# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/tooltips/vehicle_selector_tooltip_model.py
from frameworks.wulf import ViewModel

class VehicleSelectorTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(VehicleSelectorTooltipModel, self).__init__(properties=properties, commands=commands)

    def getRoverName(self):
        return self._getString(0)

    def setRoverName(self, value):
        self._setString(0, value)

    def getShortDescription(self):
        return self._getString(1)

    def setShortDescription(self, value):
        self._setString(1, value)

    def getLongDescription(self):
        return self._getString(2)

    def setLongDescription(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getString(3)

    def setIcon(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(VehicleSelectorTooltipModel, self)._initialize()
        self._addStringProperty('roverName', '')
        self._addStringProperty('shortDescription', '')
        self._addStringProperty('longDescription', '')
        self._addStringProperty('icon', '')
