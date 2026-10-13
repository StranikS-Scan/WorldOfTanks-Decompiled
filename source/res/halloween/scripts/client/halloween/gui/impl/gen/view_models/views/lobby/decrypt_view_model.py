# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/decrypt_view_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from halloween.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel

class ArtefactTypes(Enum):
    TEXT = 'text'
    SOUND = 'sound'
    FINAL = 'final'


class DecryptViewModel(ViewModel):
    __slots__ = ('onAffirmation', 'onMuted', 'onOutroVideo', 'onChangeQuest')

    def __init__(self, properties=11, commands=4):
        super(DecryptViewModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getIndex(self):
        return self._getNumber(1)

    def setIndex(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getIsMuted(self):
        return self._getBool(3)

    def setIsMuted(self, value):
        self._setBool(3, value)

    def getIsOutroDisabled(self):
        return self._getBool(4)

    def setIsOutroDisabled(self, value):
        self._setBool(4, value)

    def getIsOutroVisible(self):
        return self._getBool(5)

    def setIsOutroVisible(self, value):
        self._setBool(5, value)

    def getIsTransition(self):
        return self._getBool(6)

    def setIsTransition(self, value):
        self._setBool(6, value)

    def getIsNextArtefactAvailable(self):
        return self._getBool(7)

    def setIsNextArtefactAvailable(self, value):
        self._setBool(7, value)

    def getIsPreviousArtefactAvailable(self):
        return self._getBool(8)

    def setIsPreviousArtefactAvailable(self, value):
        self._setBool(8, value)

    def getRewards(self):
        return self._getArray(9)

    def setRewards(self, value):
        self._setArray(9, value)

    @staticmethod
    def getRewardsType():
        return BonusItemViewModel

    def getTypes(self):
        return self._getArray(10)

    def setTypes(self, value):
        self._setArray(10, value)

    @staticmethod
    def getTypesType():
        return unicode

    def _initialize(self):
        super(DecryptViewModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addNumberProperty('index', 0)
        self._addStringProperty('name', '')
        self._addBoolProperty('isMuted', False)
        self._addBoolProperty('isOutroDisabled', False)
        self._addBoolProperty('isOutroVisible', True)
        self._addBoolProperty('isTransition', False)
        self._addBoolProperty('isNextArtefactAvailable', False)
        self._addBoolProperty('isPreviousArtefactAvailable', False)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('types', Array())
        self.onAffirmation = self._addCommand('onAffirmation')
        self.onMuted = self._addCommand('onMuted')
        self.onOutroVideo = self._addCommand('onOutroVideo')
        self.onChangeQuest = self._addCommand('onChangeQuest')
