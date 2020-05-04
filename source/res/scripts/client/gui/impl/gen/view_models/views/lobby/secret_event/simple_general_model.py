# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/simple_general_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class SimpleGeneralModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SimpleGeneralModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getGeneralIcon(self):
        return self._getResource(1)

    def setGeneralIcon(self, value):
        self._setResource(1, value)

    def _initialize(self):
        super(SimpleGeneralModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addResourceProperty('generalIcon', R.invalid())
