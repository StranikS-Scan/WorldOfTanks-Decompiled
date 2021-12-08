# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/craft/ny_craft_antiduplicator_model.py
from frameworks.wulf import ViewModel

class NyCraftAntiduplicatorModel(ViewModel):
    __slots__ = ('onTumblerStateChanged', 'onFillerHidingStart')
    INACTIVE = 0
    USE_CHARGES = 1
    USE_SHARDS = 2
    ERROR = -1

    def __init__(self, properties=3, commands=2):
        super(NyCraftAntiduplicatorModel, self).__init__(properties=properties, commands=commands)

    def getFillersCount(self):
        return self._getNumber(0)

    def setFillersCount(self, value):
        self._setNumber(0, value)

    def getShardsCount(self):
        return self._getNumber(1)

    def setShardsCount(self, value):
        self._setNumber(1, value)

    def getState(self):
        return self._getNumber(2)

    def setState(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(NyCraftAntiduplicatorModel, self)._initialize()
        self._addNumberProperty('fillersCount', 0)
        self._addNumberProperty('shardsCount', 0)
        self._addNumberProperty('state', 0)
        self.onTumblerStateChanged = self._addCommand('onTumblerStateChanged')
        self.onFillerHidingStart = self._addCommand('onFillerHidingStart')
