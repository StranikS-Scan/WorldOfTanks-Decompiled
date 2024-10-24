# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_loot_box_entry_point_model.py
from frameworks.wulf import ViewModel

class WtLootBoxEntryPointModel(ViewModel):
    __slots__ = ('onWidgetClick',)

    def __init__(self, properties=4, commands=1):
        super(WtLootBoxEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getHunterLootBoxesCount(self):
        return self._getNumber(0)

    def setHunterLootBoxesCount(self, value):
        self._setNumber(0, value)

    def getBossLootBoxesCount(self):
        return self._getNumber(1)

    def setBossLootBoxesCount(self, value):
        self._setNumber(1, value)

    def getHunterHasNew(self):
        return self._getBool(2)

    def setHunterHasNew(self, value):
        self._setBool(2, value)

    def getBossHasNew(self):
        return self._getBool(3)

    def setBossHasNew(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(WtLootBoxEntryPointModel, self)._initialize()
        self._addNumberProperty('hunterLootBoxesCount', 0)
        self._addNumberProperty('bossLootBoxesCount', 0)
        self._addBoolProperty('hunterHasNew', False)
        self._addBoolProperty('bossHasNew', False)
        self.onWidgetClick = self._addCommand('onWidgetClick')
