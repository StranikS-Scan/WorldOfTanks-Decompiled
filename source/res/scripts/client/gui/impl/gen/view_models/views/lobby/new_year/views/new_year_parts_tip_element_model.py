# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_parts_tip_element_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NewYearPartsTipElementModel(ViewModel):
    __slots__ = ()
    SHARDS_ENOUGH_TO_CREATE = 0
    SHARDS_NOT_ENOUGH_TO_CREATE = 1
    SHARDS_ENOUGH_TO_UPGRADE = 2
    SHARDS_NOT_ENOUGH_TO_UPGRADE = 3
    SHARDS_ALL_MEGA_TOYS_COLLECTED = 4

    def __init__(self, properties=3, commands=0):
        super(NewYearPartsTipElementModel, self).__init__(properties=properties, commands=commands)

    def getDecorationTypeIcon(self):
        return self._getResource(0)

    def setDecorationTypeIcon(self, value):
        self._setResource(0, value)

    def getShardsCountLeft(self):
        return self._getNumber(1)

    def setShardsCountLeft(self, value):
        self._setNumber(1, value)

    def getCurrentState(self):
        return self._getNumber(2)

    def setCurrentState(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(NewYearPartsTipElementModel, self)._initialize()
        self._addResourceProperty('decorationTypeIcon', R.invalid())
        self._addNumberProperty('shardsCountLeft', 0)
        self._addNumberProperty('currentState', 0)
