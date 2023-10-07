# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tankman_container_tab_model.py
from frameworks.wulf import ViewModel

class TankmanContainerTabModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(TankmanContainerTabModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getCounter(self):
        return self._getNumber(2)

    def setCounter(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(TankmanContainerTabModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('title', '')
        self._addNumberProperty('counter', 0)
