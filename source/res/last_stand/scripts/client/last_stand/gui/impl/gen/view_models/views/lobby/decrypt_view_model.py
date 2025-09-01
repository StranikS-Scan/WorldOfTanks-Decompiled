# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/decrypt_view_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel

class ArtefactTypes(Enum):
    TEXT = 'text'
    SOUND = 'sound'
    FINAL = 'final'


class DecryptViewModel(ViewModel):
    __slots__ = ('onAffirmation', 'onMuted')

    def __init__(self, properties=8, commands=2):
        super(DecryptViewModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getIndex(self):
        return self._getNumber(1)

    def setIndex(self, value):
        self._setNumber(1, value)

    def getSelectedDifficulty(self):
        return self._getNumber(2)

    def setSelectedDifficulty(self, value):
        self._setNumber(2, value)

    def getName(self):
        return self._getString(3)

    def setName(self, value):
        self._setString(3, value)

    def getIsMuted(self):
        return self._getBool(4)

    def setIsMuted(self, value):
        self._setBool(4, value)

    def getIsTransition(self):
        return self._getBool(5)

    def setIsTransition(self, value):
        self._setBool(5, value)

    def getRewards(self):
        return self._getArray(6)

    def setRewards(self, value):
        self._setArray(6, value)

    @staticmethod
    def getRewardsType():
        return BonusItemViewModel

    def getTypes(self):
        return self._getArray(7)

    def setTypes(self, value):
        self._setArray(7, value)

    @staticmethod
    def getTypesType():
        return unicode

    def _initialize(self):
        super(DecryptViewModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addNumberProperty('index', 0)
        self._addNumberProperty('selectedDifficulty', 0)
        self._addStringProperty('name', '')
        self._addBoolProperty('isMuted', False)
        self._addBoolProperty('isTransition', False)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('types', Array())
        self.onAffirmation = self._addCommand('onAffirmation')
        self.onMuted = self._addCommand('onMuted')
