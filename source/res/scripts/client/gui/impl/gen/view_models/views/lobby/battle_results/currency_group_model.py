# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/currency_group_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_results.currency_record_model import CurrencyRecordModel

class CurrencyGroupModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CurrencyGroupModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getRecords(self):
        return self._getArray(1)

    def setRecords(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRecordsType():
        return CurrencyRecordModel

    def getUseSecondValues(self):
        return self._getBool(2)

    def setUseSecondValues(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(CurrencyGroupModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addArrayProperty('records', Array())
        self._addBoolProperty('useSecondValues', False)
