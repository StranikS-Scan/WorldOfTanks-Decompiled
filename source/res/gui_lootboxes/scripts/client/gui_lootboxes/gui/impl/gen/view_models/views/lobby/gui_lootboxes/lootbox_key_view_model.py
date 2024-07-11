# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/lootbox_key_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.key_type_model import KeyTypeModel

class KeyType(Enum):
    SIMPLE = 'simpleKey'
    LOCKPICK = 'lockpick'


class LootboxKeyViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(LootboxKeyViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def keyType(self):
        return self._getViewModel(0)

    @staticmethod
    def getKeyTypeType():
        return KeyTypeModel

    def getKeyID(self):
        return self._getNumber(1)

    def setKeyID(self, value):
        self._setNumber(1, value)

    def getCount(self):
        return self._getNumber(2)

    def setCount(self, value):
        self._setNumber(2, value)

    def getIconName(self):
        return self._getString(3)

    def setIconName(self, value):
        self._setString(3, value)

    def getUserName(self):
        return self._getString(4)

    def setUserName(self, value):
        self._setString(4, value)

    def getOpenProbability(self):
        return self._getReal(5)

    def setOpenProbability(self, value):
        self._setReal(5, value)

    def _initialize(self):
        super(LootboxKeyViewModel, self)._initialize()
        self._addViewModelProperty('keyType', KeyTypeModel())
        self._addNumberProperty('keyID', 0)
        self._addNumberProperty('count', 0)
        self._addStringProperty('iconName', 'unknown')
        self._addStringProperty('userName', 'unknown')
        self._addRealProperty('openProbability', 100.0)
