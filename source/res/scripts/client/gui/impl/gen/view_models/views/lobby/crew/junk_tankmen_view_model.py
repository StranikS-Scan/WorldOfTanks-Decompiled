# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/junk_tankmen_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanModel

class JunkTankmenViewModel(ViewModel):
    __slots__ = ('onLoadCards', 'onConfirm', 'onClose')

    def __init__(self, properties=3, commands=3):
        super(JunkTankmenViewModel, self).__init__(properties=properties, commands=commands)

    def getItemsAmount(self):
        return self._getNumber(0)

    def setItemsAmount(self, value):
        self._setNumber(0, value)

    def getItemsOffset(self):
        return self._getNumber(1)

    def setItemsOffset(self, value):
        self._setNumber(1, value)

    def getTankmanList(self):
        return self._getArray(2)

    def setTankmanList(self, value):
        self._setArray(2, value)

    @staticmethod
    def getTankmanListType():
        return TankmanModel

    def _initialize(self):
        super(JunkTankmenViewModel, self)._initialize()
        self._addNumberProperty('itemsAmount', 0)
        self._addNumberProperty('itemsOffset', 0)
        self._addArrayProperty('tankmanList', Array())
        self.onLoadCards = self._addCommand('onLoadCards')
        self.onConfirm = self._addCommand('onConfirm')
        self.onClose = self._addCommand('onClose')
