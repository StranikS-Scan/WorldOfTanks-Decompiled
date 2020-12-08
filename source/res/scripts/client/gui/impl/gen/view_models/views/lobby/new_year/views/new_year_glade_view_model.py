# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_glade_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_group_slots_model import NyGroupSlotsModel

class NewYearGladeViewModel(ViewModel):
    __slots__ = ('onIncreaseLevel', 'onHoverSlot', 'onHoverOutSlot', 'onSelectNewTalismanClick', 'onMouseEnterProgress')

    def __init__(self, properties=14, commands=5):
        super(NewYearGladeViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def groupSlots(self):
        return self._getViewModel(0)

    def getIsDragging(self):
        return self._getBool(1)

    def setIsDragging(self, value):
        self._setBool(1, value)

    def getTabType(self):
        return self._getNumber(2)

    def setTabType(self, value):
        self._setNumber(2, value)

    def getTalismanGiftState(self):
        return self._getString(3)

    def setTalismanGiftState(self, value):
        self._setString(3, value)

    def getTalismanLevel(self):
        return self._getNumber(4)

    def setTalismanLevel(self, value):
        self._setNumber(4, value)

    def getExpectedTalismanLevel(self):
        return self._getNumber(5)

    def setExpectedTalismanLevel(self, value):
        self._setNumber(5, value)

    def getTotalReceivedToys(self):
        return self._getNumber(6)

    def setTotalReceivedToys(self, value):
        self._setNumber(6, value)

    def getPrevTotalReceivedToys(self):
        return self._getNumber(7)

    def setPrevTotalReceivedToys(self, value):
        self._setNumber(7, value)

    def getMaxReceivedToys(self):
        return self._getNumber(8)

    def setMaxReceivedToys(self, value):
        self._setNumber(8, value)

    def getTalismanLevelsInfo(self):
        return self._getArray(9)

    def setTalismanLevelsInfo(self, value):
        self._setArray(9, value)

    def getTalismanGiftCooldown(self):
        return self._getNumber(10)

    def setTalismanGiftCooldown(self, value):
        self._setNumber(10, value)

    def getCurrentShards(self):
        return self._getNumber(11)

    def setCurrentShards(self, value):
        self._setNumber(11, value)

    def getHasTalismanToSelect(self):
        return self._getBool(12)

    def setHasTalismanToSelect(self, value):
        self._setBool(12, value)

    def getShowTalismanHint(self):
        return self._getBool(13)

    def setShowTalismanHint(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(NewYearGladeViewModel, self)._initialize()
        self._addViewModelProperty('groupSlots', UserListModel())
        self._addBoolProperty('isDragging', False)
        self._addNumberProperty('tabType', 1)
        self._addStringProperty('talismanGiftState', 'disabled')
        self._addNumberProperty('talismanLevel', 0)
        self._addNumberProperty('expectedTalismanLevel', 0)
        self._addNumberProperty('totalReceivedToys', -1)
        self._addNumberProperty('prevTotalReceivedToys', 0)
        self._addNumberProperty('maxReceivedToys', 0)
        self._addArrayProperty('talismanLevelsInfo', Array())
        self._addNumberProperty('talismanGiftCooldown', 0)
        self._addNumberProperty('currentShards', 0)
        self._addBoolProperty('hasTalismanToSelect', False)
        self._addBoolProperty('showTalismanHint', False)
        self.onIncreaseLevel = self._addCommand('onIncreaseLevel')
        self.onHoverSlot = self._addCommand('onHoverSlot')
        self.onHoverOutSlot = self._addCommand('onHoverOutSlot')
        self.onSelectNewTalismanClick = self._addCommand('onSelectNewTalismanClick')
        self.onMouseEnterProgress = self._addCommand('onMouseEnterProgress')
