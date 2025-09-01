# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/param_tooltip_model.py
from frameworks.wulf import ViewModel

class ParamTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ParamTooltipModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getParams(self):
        return self._getString(1)

    def setParams(self, value):
        self._setString(1, value)

    def getResId(self):
        return self._getNumber(2)

    def setResId(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(ParamTooltipModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addStringProperty('params', '{}')
        self._addNumberProperty('resId', 0)
