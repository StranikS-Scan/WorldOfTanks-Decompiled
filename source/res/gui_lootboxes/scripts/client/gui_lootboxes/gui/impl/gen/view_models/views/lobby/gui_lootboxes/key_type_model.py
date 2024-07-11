# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/key_type_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class KeyType(Enum):
    SIMPLE = 'simpleKey'
    LOCKPICK = 'lockpick'


class KeyTypeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(KeyTypeModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return KeyType(self._getString(0))

    def setValue(self, value):
        self._setString(0, value.value)

    def _initialize(self):
        super(KeyTypeModel, self)._initialize()
        self._addStringProperty('value')
