# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/common/ability_model.py
from frameworks.wulf import ViewModel

class AbilityModel(ViewModel):
    __slots__ = ()
    TOOLTIP_ID = 'AbilitiTooltip'

    def __init__(self, properties=2, commands=0):
        super(AbilityModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getIconName(self):
        return self._getString(1)

    def setIconName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(AbilityModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('iconName', '')
