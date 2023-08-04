# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/lootboxes_storage_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootbox_view_model import LootboxViewModel

class States(Enum):
    STORAGE_VIEWING = 'STORAGE_VIEWING'
    REQUEST_TO_OPEN = 'REQUEST_TO_OPEN'
    OPENING = 'OPENING'
    OPENING_ERROR = 'OPENING_ERROR'
    UNIQUE_REWARDING = 'UNIQUE_REWARDING'
    REWARDING = 'REWARDING'


class LootboxesStorageViewModel(ViewModel):
    __slots__ = ('openLootBoxes', 'onClose', 'buyBox', 'openningFinished', 'onLootboxSelected', 'changeAnimationEnabledSetting', 'showBonusProbabilities')

    def __init__(self, properties=5, commands=7):
        super(LootboxesStorageViewModel, self).__init__(properties=properties, commands=commands)

    def getLootboxes(self):
        return self._getArray(0)

    def setLootboxes(self, value):
        self._setArray(0, value)

    @staticmethod
    def getLootboxesType():
        return LootboxViewModel

    def getCurrentState(self):
        return States(self._getString(1))

    def setCurrentState(self, value):
        self._setString(1, value.value)

    def getCurrentLootboxID(self):
        return self._getNumber(2)

    def setCurrentLootboxID(self, value):
        self._setNumber(2, value)

    def getIsAnimationEnabled(self):
        return self._getBool(3)

    def setIsAnimationEnabled(self, value):
        self._setBool(3, value)

    def getIsBuyAvailable(self):
        return self._getBool(4)

    def setIsBuyAvailable(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(LootboxesStorageViewModel, self)._initialize()
        self._addArrayProperty('lootboxes', Array())
        self._addStringProperty('currentState')
        self._addNumberProperty('currentLootboxID', 0)
        self._addBoolProperty('isAnimationEnabled', True)
        self._addBoolProperty('isBuyAvailable', True)
        self.openLootBoxes = self._addCommand('openLootBoxes')
        self.onClose = self._addCommand('onClose')
        self.buyBox = self._addCommand('buyBox')
        self.openningFinished = self._addCommand('openningFinished')
        self.onLootboxSelected = self._addCommand('onLootboxSelected')
        self.changeAnimationEnabledSetting = self._addCommand('changeAnimationEnabledSetting')
        self.showBonusProbabilities = self._addCommand('showBonusProbabilities')
