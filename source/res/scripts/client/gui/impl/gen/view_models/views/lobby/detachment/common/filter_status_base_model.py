# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/filter_status_base_model.py
from frameworks.wulf import ViewModel

class FilterStatusBaseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(FilterStatusBaseModel, self).__init__(properties=properties, commands=commands)

    def getCurrent(self):
        return self._getNumber(0)

    def setCurrent(self, value):
        self._setNumber(0, value)

    def getTotal(self):
        return self._getNumber(1)

    def setTotal(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(FilterStatusBaseModel, self)._initialize()
        self._addNumberProperty('current', 0)
        self._addNumberProperty('total', 0)
