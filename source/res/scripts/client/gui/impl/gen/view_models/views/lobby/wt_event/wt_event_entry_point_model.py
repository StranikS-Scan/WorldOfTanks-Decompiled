# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_entry_point_model.py
from frameworks.wulf import ViewModel

class WtEventEntryPointModel(ViewModel):
    __slots__ = ('onClick',)
    STATE_ACTIVE = 0
    STATE_NOBATTLE = 1

    def __init__(self, properties=4, commands=1):
        super(WtEventEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getNumber(0)

    def setState(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getHunterLootBoxesCount(self):
        return self._getNumber(2)

    def setHunterLootBoxesCount(self, value):
        self._setNumber(2, value)

    def getBossLootBoxesCount(self):
        return self._getNumber(3)

    def setBossLootBoxesCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(WtEventEntryPointModel, self)._initialize()
        self._addNumberProperty('state', 0)
        self._addNumberProperty('endDate', -1)
        self._addNumberProperty('hunterLootBoxesCount', 0)
        self._addNumberProperty('bossLootBoxesCount', 0)
        self.onClick = self._addCommand('onClick')
