# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_talisman_progress_level_model.py
from frameworks.wulf import ViewModel

class NyTalismanProgressLevelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyTalismanProgressLevelModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getCost(self):
        return self._getNumber(1)

    def setCost(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NyTalismanProgressLevelModel, self)._initialize()
        self._addNumberProperty('level', 1)
        self._addNumberProperty('cost', 0)
