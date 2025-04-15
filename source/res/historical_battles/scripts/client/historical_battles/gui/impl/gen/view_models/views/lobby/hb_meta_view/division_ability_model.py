# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_meta_view/division_ability_model.py
from frameworks.wulf import ViewModel

class DivisionAbilityModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(DivisionAbilityModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(DivisionAbilityModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('icon', '')
