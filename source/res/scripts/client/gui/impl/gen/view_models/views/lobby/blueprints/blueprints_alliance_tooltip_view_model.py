# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/blueprints/blueprints_alliance_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_price import BlueprintPrice

class BlueprintsAllianceTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BlueprintsAllianceTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getPriceOptions(self):
        return self._getArray(0)

    def setPriceOptions(self, value):
        self._setArray(0, value)

    def getVehicleNationName(self):
        return self._getString(1)

    def setVehicleNationName(self, value):
        self._setString(1, value)

    def getAllianceName(self):
        return self._getString(2)

    def setAllianceName(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(BlueprintsAllianceTooltipViewModel, self)._initialize()
        self._addArrayProperty('priceOptions', Array())
        self._addStringProperty('vehicleNationName', '')
        self._addStringProperty('allianceName', '')
