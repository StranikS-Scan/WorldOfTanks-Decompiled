# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/cn_loot_boxes/china_loot_boxes_entry_point_model.py
from frameworks.wulf import ViewModel

class ChinaLootBoxesEntryPointModel(ViewModel):
    __slots__ = ('onWidgetClick',)

    def __init__(self, properties=3, commands=1):
        super(ChinaLootBoxesEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getBoxesCount(self):
        return self._getNumber(0)

    def setBoxesCount(self, value):
        self._setNumber(0, value)

    def getHasNew(self):
        return self._getBool(1)

    def setHasNew(self, value):
        self._setBool(1, value)

    def getTime(self):
        return self._getNumber(2)

    def setTime(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(ChinaLootBoxesEntryPointModel, self)._initialize()
        self._addNumberProperty('boxesCount', 0)
        self._addBoolProperty('hasNew', False)
        self._addNumberProperty('time', 0)
        self.onWidgetClick = self._addCommand('onWidgetClick')
