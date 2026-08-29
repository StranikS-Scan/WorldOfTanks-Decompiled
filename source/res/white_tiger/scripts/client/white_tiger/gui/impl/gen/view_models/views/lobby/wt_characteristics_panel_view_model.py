# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_characteristics_panel_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_characteristic_model import WtCharacteristicModel

class WtCharacteristicsPanelViewModel(ViewModel):
    __slots__ = ('onLeaveClicked',)

    def __init__(self, properties=3, commands=1):
        super(WtCharacteristicsPanelViewModel, self).__init__(properties=properties, commands=commands)

    def getSpecialInfo(self):
        return self._getResource(0)

    def setSpecialInfo(self, value):
        self._setResource(0, value)

    def getPros(self):
        return self._getArray(1)

    def setPros(self, value):
        self._setArray(1, value)

    @staticmethod
    def getProsType():
        return WtCharacteristicModel

    def getCons(self):
        return self._getArray(2)

    def setCons(self, value):
        self._setArray(2, value)

    @staticmethod
    def getConsType():
        return WtCharacteristicModel

    def _initialize(self):
        super(WtCharacteristicsPanelViewModel, self)._initialize()
        self._addResourceProperty('specialInfo', R.invalid())
        self._addArrayProperty('pros', Array())
        self._addArrayProperty('cons', Array())
        self.onLeaveClicked = self._addCommand('onLeaveClicked')
