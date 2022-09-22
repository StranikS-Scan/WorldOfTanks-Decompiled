# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/details_record_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.currency_model import CurrencyModel
from gui.impl.gen.view_models.views.lobby.postbattle.details_item_model import DetailsItemModel

class DetailsRecordModel(DetailsItemModel):
    __slots__ = ()
    EARNED = 'earned'
    EARNED_RECORD = 'earned_record'
    SUBGROUP_TOTAL = 'subgroupTotal'
    TOTAL = 'total'
    ALTERNATIVE_TOTAL = 'alternativeTotal'

    def __init__(self, properties=6, commands=0):
        super(DetailsRecordModel, self).__init__(properties=properties, commands=commands)

    def getStringID(self):
        return self._getResource(2)

    def setStringID(self, value):
        self._setResource(2, value)

    def getTooltipStringID(self):
        return self._getResource(3)

    def setTooltipStringID(self, value):
        self._setResource(3, value)

    def getTags(self):
        return self._getArray(4)

    def setTags(self, value):
        self._setArray(4, value)

    @staticmethod
    def getTagsType():
        return str

    def getCurrencies(self):
        return self._getArray(5)

    def setCurrencies(self, value):
        self._setArray(5, value)

    @staticmethod
    def getCurrenciesType():
        return CurrencyModel

    def _initialize(self):
        super(DetailsRecordModel, self)._initialize()
        self._addResourceProperty('stringID', R.invalid())
        self._addResourceProperty('tooltipStringID', R.invalid())
        self._addArrayProperty('tags', Array())
        self._addArrayProperty('currencies', Array())
