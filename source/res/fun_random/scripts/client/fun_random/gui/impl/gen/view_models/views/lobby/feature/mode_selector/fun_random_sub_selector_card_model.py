# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/mode_selector/fun_random_sub_selector_card_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class CardState(IntEnum):
    NOT_STARTED = 0
    ACTIVE = 1
    DISABLED = 2
    FINISHED = 3


class FunRandomSubSelectorCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(FunRandomSubSelectorCardModel, self).__init__(properties=properties, commands=commands)

    def getAssetsPointer(self):
        return self._getString(0)

    def setAssetsPointer(self, value):
        self._setString(0, value)

    def getSubModeId(self):
        return self._getNumber(1)

    def setSubModeId(self, value):
        self._setNumber(1, value)

    def getConditions(self):
        return self._getString(2)

    def setConditions(self, value):
        self._setString(2, value)

    def getState(self):
        return CardState(self._getNumber(3))

    def setState(self, value):
        self._setNumber(3, value.value)

    def getIsSelected(self):
        return self._getBool(4)

    def setIsSelected(self, value):
        self._setBool(4, value)

    def getTimeLeft(self):
        return self._getString(5)

    def setTimeLeft(self, value):
        self._setString(5, value)

    def getTimeToStart(self):
        return self._getNumber(6)

    def setTimeToStart(self, value):
        self._setNumber(6, value)

    def getModifiersDomains(self):
        return self._getArray(7)

    def setModifiersDomains(self, value):
        self._setArray(7, value)

    @staticmethod
    def getModifiersDomainsType():
        return unicode

    def _initialize(self):
        super(FunRandomSubSelectorCardModel, self)._initialize()
        self._addStringProperty('assetsPointer', '')
        self._addNumberProperty('subModeId', 0)
        self._addStringProperty('conditions', '')
        self._addNumberProperty('state')
        self._addBoolProperty('isSelected', False)
        self._addStringProperty('timeLeft', '')
        self._addNumberProperty('timeToStart', -1)
        self._addArrayProperty('modifiersDomains', Array())
