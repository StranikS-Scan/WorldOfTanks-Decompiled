# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/common/wt_run_portal_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class WtRunPortalModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(WtRunPortalModel, self).__init__(properties=properties, commands=commands)

    def getAttemptPrice(self):
        return self._getNumber(0)

    def setAttemptPrice(self, value):
        self._setNumber(0, value)

    def getOpenLootBoxesCount(self):
        return self._getArray(1)

    def setOpenLootBoxesCount(self, value):
        self._setArray(1, value)

    @staticmethod
    def getOpenLootBoxesCountType():
        return int

    def getLootBoxesCount(self):
        return self._getNumber(2)

    def setLootBoxesCount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(WtRunPortalModel, self)._initialize()
        self._addNumberProperty('attemptPrice', 0)
        self._addArrayProperty('openLootBoxesCount', Array())
        self._addNumberProperty('lootBoxesCount', 0)
