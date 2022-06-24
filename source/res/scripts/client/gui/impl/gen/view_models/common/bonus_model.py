# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/bonus_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.bonus_value_model import BonusValueModel

class BonusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BonusModel, self).__init__(properties=properties, commands=commands)

    def getLocaleName(self):
        return self._getString(0)

    def setLocaleName(self, value):
        self._setString(0, value)

    def getValues(self):
        return self._getArray(1)

    def setValues(self, value):
        self._setArray(1, value)

    @staticmethod
    def getValuesType():
        return BonusValueModel

    def _initialize(self):
        super(BonusModel, self)._initialize()
        self._addStringProperty('localeName', '')
        self._addArrayProperty('values', Array())
