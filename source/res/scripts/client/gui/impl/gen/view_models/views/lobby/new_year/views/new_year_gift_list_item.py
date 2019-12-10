# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_gift_list_item.py
from frameworks.wulf import ViewModel

class NewYearGiftListItem(ViewModel):
    __slots__ = ('onButtonClick',)

    def __init__(self, properties=3, commands=1):
        super(NewYearGiftListItem, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getIsShowButton(self):
        return self._getBool(1)

    def setIsShowButton(self, value):
        self._setBool(1, value)

    def getIsBrowserIconVisible(self):
        return self._getBool(2)

    def setIsBrowserIconVisible(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(NewYearGiftListItem, self)._initialize()
        self._addStringProperty('type', '')
        self._addBoolProperty('isShowButton', False)
        self._addBoolProperty('isBrowserIconVisible', False)
        self.onButtonClick = self._addCommand('onButtonClick')
