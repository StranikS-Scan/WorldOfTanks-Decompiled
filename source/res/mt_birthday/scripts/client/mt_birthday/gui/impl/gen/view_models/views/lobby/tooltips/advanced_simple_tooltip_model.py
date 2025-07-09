# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/tooltips/advanced_simple_tooltip_model.py
from frameworks.wulf import ViewModel

class AdvancedSimpleTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(AdvancedSimpleTooltipModel, self).__init__(properties=properties, commands=commands)

    def getHeader(self):
        return self._getString(0)

    def setHeader(self, value):
        self._setString(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getAdditionalDescription(self):
        return self._getString(2)

    def setAdditionalDescription(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(AdvancedSimpleTooltipModel, self)._initialize()
        self._addStringProperty('header', '')
        self._addStringProperty('description', '')
        self._addStringProperty('additionalDescription', '')
