# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/tankman_option_model.py
from frameworks.wulf import ViewModel

class TankmanOptionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(TankmanOptionModel, self).__init__(properties=properties, commands=commands)

    def getTankman(self):
        return self._getString(0)

    def setTankman(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(TankmanOptionModel, self)._initialize()
        self._addStringProperty('tankman', '')
        self._addStringProperty('icon', '')
