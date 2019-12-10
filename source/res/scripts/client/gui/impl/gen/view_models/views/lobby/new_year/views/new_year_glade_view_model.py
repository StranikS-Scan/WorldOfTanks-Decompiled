# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_glade_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_group_slots_model import NyGroupSlotsModel

class NewYearGladeViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onSideBarBtnClick', 'onHoverSlot', 'onHoverOutSlot', 'onTalismanClick', 'onSelectNewTalismanClick')
    TALISMAN_DISABLED = 'disabled'
    TALISMAN_SELECT_NEW = 'selectNew'
    TALISMAN_GIFT_WAIT = 'giftWait'
    TALISMAN_GIFT_READY = 'giftReady'

    def __init__(self, properties=7, commands=6):
        super(NewYearGladeViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def groupSlots(self):
        return self._getViewModel(0)

    def getItemsTabBar(self):
        return self._getArray(1)

    def setItemsTabBar(self, value):
        self._setArray(1, value)

    def getStartIndex(self):
        return self._getNumber(2)

    def setStartIndex(self, value):
        self._setNumber(2, value)

    def getIsDragging(self):
        return self._getBool(3)

    def setIsDragging(self, value):
        self._setBool(3, value)

    def getIsVisible(self):
        return self._getBool(4)

    def setIsVisible(self, value):
        self._setBool(4, value)

    def getIsMascotTab(self):
        return self._getBool(5)

    def setIsMascotTab(self, value):
        self._setBool(5, value)

    def getTalismanGiftState(self):
        return self._getString(6)

    def setTalismanGiftState(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(NewYearGladeViewModel, self)._initialize()
        self._addViewModelProperty('groupSlots', UserListModel())
        self._addArrayProperty('itemsTabBar', Array())
        self._addNumberProperty('startIndex', 0)
        self._addBoolProperty('isDragging', False)
        self._addBoolProperty('isVisible', True)
        self._addBoolProperty('isMascotTab', False)
        self._addStringProperty('talismanGiftState', 'disabled')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onSideBarBtnClick = self._addCommand('onSideBarBtnClick')
        self.onHoverSlot = self._addCommand('onHoverSlot')
        self.onHoverOutSlot = self._addCommand('onHoverOutSlot')
        self.onTalismanClick = self._addCommand('onTalismanClick')
        self.onSelectNewTalismanClick = self._addCommand('onSelectNewTalismanClick')
