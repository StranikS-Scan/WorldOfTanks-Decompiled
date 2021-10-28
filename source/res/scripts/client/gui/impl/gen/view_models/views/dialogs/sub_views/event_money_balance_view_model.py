# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/sub_views/event_money_balance_view_model.py
from frameworks.wulf import ViewModel

class EventMoneyBalanceViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(EventMoneyBalanceViewModel, self).__init__(properties=properties, commands=commands)

    def getKeyCount(self):
        return self._getNumber(0)

    def setKeyCount(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(EventMoneyBalanceViewModel, self)._initialize()
        self._addNumberProperty('keyCount', 0)
