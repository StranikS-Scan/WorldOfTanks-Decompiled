# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/counter_model.py
from frameworks.wulf import ViewModel

class CounterModel(ViewModel):
    __slots__ = ()

    def getValue(self):
        return self._getNumber(0)

    def setValue(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(CounterModel, self)._initialize()
        self._addNumberProperty('value', -1)
