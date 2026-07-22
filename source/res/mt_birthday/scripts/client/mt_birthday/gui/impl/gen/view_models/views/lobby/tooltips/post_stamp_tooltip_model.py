# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/tooltips/post_stamp_tooltip_model.py
from frameworks.wulf import ViewModel

class PostStampTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PostStampTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCurrencyCount(self):
        return self._getNumber(0)

    def setCurrencyCount(self, value):
        self._setNumber(0, value)

    def getCurrencyCountTest(self):
        return self._getNumber(1)

    def setCurrencyCountTest(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(PostStampTooltipModel, self)._initialize()
        self._addNumberProperty('currencyCount', 0)
        self._addNumberProperty('currencyCountTest', 0)
