# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/slot_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.platoon.player_model import PlayerModel
from gui.impl.gen.view_models.views.lobby.platoon.slot_label_element_model import SlotLabelElementModel

class SlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(SlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def player(self):
        return self._getViewModel(0)

    def getSlotId(self):
        return self._getNumber(1)

    def setSlotId(self, value):
        self._setNumber(1, value)

    def getIsSearching(self):
        return self._getBool(2)

    def setIsSearching(self, value):
        self._setBool(2, value)

    def getSearchStartTime(self):
        return self._getNumber(3)

    def setSearchStartTime(self, value):
        self._setNumber(3, value)

    def getIsEmpty(self):
        return self._getBool(4)

    def setIsEmpty(self, value):
        self._setBool(4, value)

    def getIsDisabled(self):
        return self._getBool(5)

    def setIsDisabled(self, value):
        self._setBool(5, value)

    def getIsInBattle(self):
        return self._getBool(6)

    def setIsInBattle(self, value):
        self._setBool(6, value)

    def getIsEvent(self):
        return self._getBool(7)

    def setIsEvent(self, value):
        self._setBool(7, value)

    def getInfoText(self):
        return self._getString(8)

    def setInfoText(self, value):
        self._setString(8, value)

    def getEstimatedTime(self):
        return self._getString(9)

    def setEstimatedTime(self, value):
        self._setString(9, value)

    def getSlotLabelElements(self):
        return self._getArray(10)

    def setSlotLabelElements(self, value):
        self._setArray(10, value)

    def _initialize(self):
        super(SlotModel, self)._initialize()
        self._addViewModelProperty('player', PlayerModel())
        self._addNumberProperty('slotId', 0)
        self._addBoolProperty('isSearching', False)
        self._addNumberProperty('searchStartTime', 0)
        self._addBoolProperty('isEmpty', False)
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isInBattle', False)
        self._addBoolProperty('isEvent', False)
        self._addStringProperty('infoText', '')
        self._addStringProperty('estimatedTime', '')
        self._addArrayProperty('slotLabelElements', Array())
