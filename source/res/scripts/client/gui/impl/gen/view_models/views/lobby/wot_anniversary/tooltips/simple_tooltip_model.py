# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/tooltips/simple_tooltip_model.py
from frameworks.wulf import ViewModel

class SimpleTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(SimpleTooltipModel, self).__init__(properties=properties, commands=commands)

    def getPayload(self):
        return self._getString(0)

    def setPayload(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(SimpleTooltipModel, self)._initialize()
        self._addStringProperty('payload', '')
