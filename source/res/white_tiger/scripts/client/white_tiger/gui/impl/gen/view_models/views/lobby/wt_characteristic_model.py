# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_characteristic_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class WtCharacteristicModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WtCharacteristicModel, self).__init__(properties=properties, commands=commands)

    def getParameter(self):
        return self._getString(0)

    def setParameter(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def _initialize(self):
        super(WtCharacteristicModel, self)._initialize()
        self._addStringProperty('parameter', '')
        self._addResourceProperty('icon', R.invalid())
