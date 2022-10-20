# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/common/stat_model.py
from frameworks.wulf import ViewModel

class StatModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(StatModel, self).__init__(properties=properties, commands=commands)

    def getStatName(self):
        return self._getString(0)

    def setStatName(self, value):
        self._setString(0, value)

    def getStatValue(self):
        return self._getString(1)

    def setStatValue(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(StatModel, self)._initialize()
        self._addStringProperty('statName', '')
        self._addStringProperty('statValue', '')
