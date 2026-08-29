# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/widgets/tank_info_view_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.property_model import PropertyModel

class TankInfoViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(TankInfoViewModel, self).__init__(properties=properties, commands=commands)

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
        return PropertyModel

    def getCons(self):
        return self._getArray(2)

    def setCons(self, value):
        self._setArray(2, value)

    @staticmethod
    def getConsType():
        return PropertyModel

    def _initialize(self):
        super(TankInfoViewModel, self)._initialize()
        self._addResourceProperty('specialInfo', R.invalid())
        self._addArrayProperty('pros', Array())
        self._addArrayProperty('cons', Array())
