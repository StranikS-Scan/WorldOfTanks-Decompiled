# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/entry_point_view_model.py
from frameworks.wulf import ViewModel

class EntryPointViewModel(ViewModel):
    __slots__ = ('onEntryClick',)

    def __init__(self, properties=5, commands=1):
        super(EntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getEventName(self):
        return self._getString(0)

    def setEventName(self, value):
        self._setString(0, value)

    def getIsEnabled(self):
        return self._getBool(1)

    def setIsEnabled(self, value):
        self._setBool(1, value)

    def getBoxesCount(self):
        return self._getNumber(2)

    def setBoxesCount(self, value):
        self._setNumber(2, value)

    def getHasNew(self):
        return self._getBool(3)

    def setHasNew(self, value):
        self._setBool(3, value)

    def getEventExpireTime(self):
        return self._getNumber(4)

    def setEventExpireTime(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(EntryPointViewModel, self)._initialize()
        self._addStringProperty('eventName', '')
        self._addBoolProperty('isEnabled', False)
        self._addNumberProperty('boxesCount', 0)
        self._addBoolProperty('hasNew', False)
        self._addNumberProperty('eventExpireTime', 0)
        self.onEntryClick = self._addCommand('onEntryClick')
