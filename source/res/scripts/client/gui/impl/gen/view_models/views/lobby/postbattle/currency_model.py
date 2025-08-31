# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/currency_model.py
from frameworks.wulf import ViewModel

class CurrencyModel(ViewModel):
    __slots__ = ()
    CREDITS = 'credits'
    CRYSTALS = 'crystal'
    XP = 'xp'
    FREE_XP = 'freeXp'

    def __init__(self, properties=2, commands=0):
        super(CurrencyModel, self).__init__(properties=properties, commands=commands)

    def getAmount(self):
        return self._getNumber(0)

    def setAmount(self, value):
        self._setNumber(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(CurrencyModel, self)._initialize()
        self._addNumberProperty('amount', 0)
        self._addStringProperty('type', '')
