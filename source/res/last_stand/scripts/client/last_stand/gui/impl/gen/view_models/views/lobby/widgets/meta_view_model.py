# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/widgets/meta_view_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel

class ArtefactStates(Enum):
    NONE = 'none'
    INPROGRESS = 'inProgress'
    RECEIVE = 'receive'
    OPEN = 'open'


class MetaViewModel(ViewModel):
    __slots__ = ('onSkip', 'onDecrypt', 'onView', 'onSlideToNext')

    def __init__(self, properties=11, commands=4):
        super(MetaViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonus(self):
        return self._getViewModel(0)

    @staticmethod
    def getBonusType():
        return BonusItemViewModel

    def getId(self):
        return self._getString(1)

    def setId(self, value):
        self._setString(1, value)

    def getIndex(self):
        return self._getNumber(2)

    def setIndex(self, value):
        self._setNumber(2, value)

    def getName(self):
        return self._getString(3)

    def setName(self, value):
        self._setString(3, value)

    def getDescription(self):
        return self._getString(4)

    def setDescription(self, value):
        self._setString(4, value)

    def getSkipPrice(self):
        return self._getNumber(5)

    def setSkipPrice(self, value):
        self._setNumber(5, value)

    def getDecodePrice(self):
        return self._getNumber(6)

    def setDecodePrice(self, value):
        self._setNumber(6, value)

    def getKeys(self):
        return self._getNumber(7)

    def setKeys(self, value):
        self._setNumber(7, value)

    def getState(self):
        return ArtefactStates(self._getString(8))

    def setState(self, value):
        self._setString(8, value.value)

    def getTypes(self):
        return self._getArray(9)

    def setTypes(self, value):
        self._setArray(9, value)

    @staticmethod
    def getTypesType():
        return unicode

    def getHasProminentReward(self):
        return self._getBool(10)

    def setHasProminentReward(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(MetaViewModel, self)._initialize()
        self._addViewModelProperty('bonus', BonusItemViewModel())
        self._addStringProperty('id', '')
        self._addNumberProperty('index', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
        self._addNumberProperty('skipPrice', 0)
        self._addNumberProperty('decodePrice', 0)
        self._addNumberProperty('keys', 0)
        self._addStringProperty('state')
        self._addArrayProperty('types', Array())
        self._addBoolProperty('hasProminentReward', False)
        self.onSkip = self._addCommand('onSkip')
        self.onDecrypt = self._addCommand('onDecrypt')
        self.onView = self._addCommand('onView')
        self.onSlideToNext = self._addCommand('onSlideToNext')
