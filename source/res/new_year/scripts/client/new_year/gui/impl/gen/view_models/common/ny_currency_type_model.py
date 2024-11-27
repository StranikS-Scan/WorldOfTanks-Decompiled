# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/common/ny_currency_type_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class NyCurrencyType(Enum):
    MANDARIN = 'ny25_mandarin'
    NYGIFTMACHINETOKEN = 'ny25Token'
    GOLD = 'gold'


class NyCurrencyTypeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NyCurrencyTypeModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return NyCurrencyType(self._getString(0))

    def setValue(self, value):
        self._setString(0, value.value)

    def _initialize(self):
        super(NyCurrencyTypeModel, self)._initialize()
        self._addStringProperty('value', NyCurrencyType.MANDARIN.value)
