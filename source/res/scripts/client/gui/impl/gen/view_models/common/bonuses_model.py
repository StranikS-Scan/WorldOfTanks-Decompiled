# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/bonuses_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.bonus_model import BonusModel

class BonusesModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BonusesModel, self).__init__(properties=properties, commands=commands)

    def getItems(self):
        return self._getArray(0)

    def setItems(self, value):
        self._setArray(0, value)

    @staticmethod
    def getItemsType():
        return BonusModel

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(BonusesModel, self)._initialize()
        self._addArrayProperty('items', Array())
        self._addStringProperty('title', '')
