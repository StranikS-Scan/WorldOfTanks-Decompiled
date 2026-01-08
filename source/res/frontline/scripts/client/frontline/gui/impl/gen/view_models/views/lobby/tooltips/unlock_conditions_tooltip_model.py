# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/tooltips/unlock_conditions_tooltip_model.py
from frameworks.wulf import ViewModel

class UnlockConditionsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(UnlockConditionsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getObject(self):
        return self._getString(0)

    def setObject(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(UnlockConditionsTooltipModel, self)._initialize()
        self._addStringProperty('object', '')
