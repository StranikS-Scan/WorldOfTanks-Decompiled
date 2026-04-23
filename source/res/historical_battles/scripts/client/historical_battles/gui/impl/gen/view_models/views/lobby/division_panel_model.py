# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/division_panel_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.division_model import DivisionModel

class DivisionPanelModel(ViewModel):
    __slots__ = ('onDivisionChanged', 'onNavigateToDivisionsClicked')

    def __init__(self, properties=4, commands=2):
        super(DivisionPanelModel, self).__init__(properties=properties, commands=commands)

    def getFrontName(self):
        return self._getString(0)

    def setFrontName(self, value):
        self._setString(0, value)

    def getDivisions(self):
        return self._getArray(1)

    def setDivisions(self, value):
        self._setArray(1, value)

    @staticmethod
    def getDivisionsType():
        return DivisionModel

    def getSelectedDivisionId(self):
        return self._getNumber(2)

    def setSelectedDivisionId(self, value):
        self._setNumber(2, value)

    def getIsSwitchingDisabled(self):
        return self._getBool(3)

    def setIsSwitchingDisabled(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(DivisionPanelModel, self)._initialize()
        self._addStringProperty('frontName', '')
        self._addArrayProperty('divisions', Array())
        self._addNumberProperty('selectedDivisionId', 0)
        self._addBoolProperty('isSwitchingDisabled', False)
        self.onDivisionChanged = self._addCommand('onDivisionChanged')
        self.onNavigateToDivisionsClicked = self._addCommand('onNavigateToDivisionsClicked')
