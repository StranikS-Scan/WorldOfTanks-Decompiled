# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/gen/view_models/views/lobby/well_panel_model.py
from resource_well.gui.impl.gen.view_models.views.lobby.enums import EventMode
from frameworks.wulf import ViewModel

class WellPanelModel(ViewModel):
    __slots__ = ('onAction',)

    def __init__(self, properties=5, commands=1):
        super(WellPanelModel, self).__init__(properties=properties, commands=commands)

    def getTopRewardsCount(self):
        return self._getNumber(0)

    def setTopRewardsCount(self, value):
        self._setNumber(0, value)

    def getRegularRewardsCount(self):
        return self._getNumber(1)

    def setRegularRewardsCount(self, value):
        self._setNumber(1, value)

    def getVehicleName(self):
        return self._getString(2)

    def setVehicleName(self, value):
        self._setString(2, value)

    def getIsVisible(self):
        return self._getBool(3)

    def setIsVisible(self, value):
        self._setBool(3, value)

    def getEventMode(self):
        return EventMode(self._getString(4))

    def setEventMode(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(WellPanelModel, self)._initialize()
        self._addNumberProperty('topRewardsCount', 0)
        self._addNumberProperty('regularRewardsCount', 0)
        self._addStringProperty('vehicleName', '')
        self._addBoolProperty('isVisible', False)
        self._addStringProperty('eventMode')
        self.onAction = self._addCommand('onAction')
