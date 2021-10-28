# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/event_keys_counter_panel_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class VisualTypeEnum(Enum):
    HANGAR = 'hangar'
    META = 'meta'
    SHOP = 'shop'
    CUSTOMIZATION = 'customization'


class EventKeysCounterPanelViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=5, commands=1):
        super(EventKeysCounterPanelViewModel, self).__init__(properties=properties, commands=commands)

    def getKeys(self):
        return self._getNumber(0)

    def setKeys(self, value):
        self._setNumber(0, value)

    def getIsPackAvailable(self):
        return self._getBool(1)

    def setIsPackAvailable(self, value):
        self._setBool(1, value)

    def getIsNotEnough(self):
        return self._getBool(2)

    def setIsNotEnough(self, value):
        self._setBool(2, value)

    def getIsAnimated(self):
        return self._getBool(3)

    def setIsAnimated(self, value):
        self._setBool(3, value)

    def getState(self):
        return VisualTypeEnum(self._getString(4))

    def setState(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(EventKeysCounterPanelViewModel, self)._initialize()
        self._addNumberProperty('keys', 0)
        self._addBoolProperty('isPackAvailable', False)
        self._addBoolProperty('isNotEnough', False)
        self._addBoolProperty('isAnimated', False)
        self._addStringProperty('state')
        self.onClick = self._addCommand('onClick')
