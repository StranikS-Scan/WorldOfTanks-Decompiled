# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/widgets/lootbox_entry_view_model.py
from frameworks.wulf import ViewModel

class LootboxEntryViewModel(ViewModel):
    __slots__ = ('onEntryClick',)

    def __init__(self, properties=2, commands=1):
        super(LootboxEntryViewModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(0)

    def setIsEnabled(self, value):
        self._setBool(0, value)

    def getBoxesCount(self):
        return self._getNumber(1)

    def setBoxesCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(LootboxEntryViewModel, self)._initialize()
        self._addBoolProperty('isEnabled', False)
        self._addNumberProperty('boxesCount', 0)
        self.onEntryClick = self._addCommand('onEntryClick')
