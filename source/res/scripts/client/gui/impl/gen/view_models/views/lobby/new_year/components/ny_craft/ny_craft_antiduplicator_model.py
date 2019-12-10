# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_craft/ny_craft_antiduplicator_model.py
from frameworks.wulf import ViewModel

class NyCraftAntiduplicatorModel(ViewModel):
    __slots__ = ('onTumblerToggleChanged',)
    EMPTY = 0
    INSERTED = 1
    USING = 2

    def __init__(self, properties=4, commands=1):
        super(NyCraftAntiduplicatorModel, self).__init__(properties=properties, commands=commands)

    def getCountFillers(self):
        return self._getNumber(0)

    def setCountFillers(self, value):
        self._setNumber(0, value)

    def getFillerState(self):
        return self._getNumber(1)

    def setFillerState(self, value):
        self._setNumber(1, value)

    def getEnabled(self):
        return self._getBool(2)

    def setEnabled(self, value):
        self._setBool(2, value)

    def getTumblerTurnOn(self):
        return self._getBool(3)

    def setTumblerTurnOn(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(NyCraftAntiduplicatorModel, self)._initialize()
        self._addNumberProperty('countFillers', 0)
        self._addNumberProperty('fillerState', -1)
        self._addBoolProperty('enabled', True)
        self._addBoolProperty('tumblerTurnOn', False)
        self.onTumblerToggleChanged = self._addCommand('onTumblerToggleChanged')
