# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/slot_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.platoon.player_model import PlayerModel
from gui.impl.gen.view_models.views.lobby.platoon.slot_label_element_model import SlotLabelElementModel

class PrebattleType(Enum):
    SQUAD = 'squad'
    EVENT = 'event'
    COMP7 = 'comp7'
    BATTLEROYAL = 'battle_royal'
    EPIC = 'epic'
    MAPBOX = 'mapbox'


class ErrorType(IntEnum):
    NONE = 0
    MODEOFFLINE = 1


class SlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(SlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def player(self):
        return self._getViewModel(0)

    @staticmethod
    def getPlayerType():
        return PlayerModel

    def getPrebattleType(self):
        return PrebattleType(self._getString(1))

    def setPrebattleType(self, value):
        self._setString(1, value.value)

    def getSlotId(self):
        return self._getNumber(2)

    def setSlotId(self, value):
        self._setNumber(2, value)

    def getIsSearching(self):
        return self._getBool(3)

    def setIsSearching(self, value):
        self._setBool(3, value)

    def getSearchStartTime(self):
        return self._getNumber(4)

    def setSearchStartTime(self, value):
        self._setNumber(4, value)

    def getIsEmpty(self):
        return self._getBool(5)

    def setIsEmpty(self, value):
        self._setBool(5, value)

    def getIsDisabled(self):
        return self._getBool(6)

    def setIsDisabled(self, value):
        self._setBool(6, value)

    def getIsInBattle(self):
        return self._getBool(7)

    def setIsInBattle(self, value):
        self._setBool(7, value)

    def getInfoText(self):
        return self._getString(8)

    def setInfoText(self, value):
        self._setString(8, value)

    def getEstimatedTime(self):
        return self._getString(9)

    def setEstimatedTime(self, value):
        self._setString(9, value)

    def getErrorType(self):
        return ErrorType(self._getNumber(10))

    def setErrorType(self, value):
        self._setNumber(10, value.value)

    def getSlotLabelElements(self):
        return self._getArray(11)

    def setSlotLabelElements(self, value):
        self._setArray(11, value)

    @staticmethod
    def getSlotLabelElementsType():
        return SlotLabelElementModel

    def _initialize(self):
        super(SlotModel, self)._initialize()
        self._addViewModelProperty('player', PlayerModel())
        self._addStringProperty('prebattleType')
        self._addNumberProperty('slotId', 0)
        self._addBoolProperty('isSearching', False)
        self._addNumberProperty('searchStartTime', 0)
        self._addBoolProperty('isEmpty', False)
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isInBattle', False)
        self._addStringProperty('infoText', '')
        self._addStringProperty('estimatedTime', '')
        self._addNumberProperty('errorType')
        self._addArrayProperty('slotLabelElements', Array())
