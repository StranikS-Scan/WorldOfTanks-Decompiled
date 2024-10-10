# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/getter/detailed_stats.py
import typing
from collections import namedtuple
from frameworks.wulf import Array
from gui.battle_results.presenter.getter.common import Field
from gui.impl.gen.view_models.views.lobby.postbattle.currency_model import CurrencyModel
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable.records import ReplayRecords
StatsCurrencyBlock = namedtuple('CreditFields', ('detailed', 'total'))

class DetailedStatsField(Field):
    __slots__ = ('__blockIdx', '__tags', '_isShown', '__tooltipString')

    def __init__(self, stringID, blockIdx, tags, isShown, tooltipString):
        super(DetailedStatsField, self).__init__(stringID)
        self.__blockIdx = blockIdx
        self.__tags = tags if tags is not None else ('',)
        self.__tooltipString = tooltipString
        self._isShown = isShown
        return

    @property
    def blockIdx(self):
        return self.__blockIdx

    @property
    def tags(self):
        return self.__tags

    @property
    def tooltipStringID(self):
        return self.__tooltipString

    def getFieldValues(self, *args):
        pass

    def _getRecord(self, *args):
        pass

    def _getValue(self, *args):
        pass


class CurrencyField(DetailedStatsField):
    __slots__ = ('_recordItems', '_valueType')

    def __init__(self, stringID, blockIdx, recordItems, valueType, tags=None, isShown=False, tooltipString=R.invalid()):
        super(CurrencyField, self).__init__(stringID, blockIdx, tags, isShown, tooltipString)
        self._recordItems = recordItems
        self._valueType = valueType

    def _getRecord(self, value):
        if not value and not self._isShown:
            return None
        else:
            record = Array()
            record.reserve(1)
            valueModel = CurrencyModel()
            valueModel.setAmount(value)
            valueModel.setType(self._valueType)
            record.addViewModel(valueModel)
            return record


class EventField(CurrencyField):
    __slots__ = ()

    def getFieldValues(self, record):
        return self._getRecord(self._getValue(record))

    def _getValue(self, record):
        return sum([ record.findRecord(recordItem) for recordItem in self._recordItems ])
