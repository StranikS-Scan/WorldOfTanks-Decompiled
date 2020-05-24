# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/progressive_items_view/item_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.customization.progressive_items_view.item_level_info_model import ItemLevelInfoModel

class ItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(ItemModel, self).__init__(properties=properties, commands=commands)

    @property
    def eachLevelInfo(self):
        return self._getViewModel(0)

    def getMaxLevel(self):
        return self._getNumber(1)

    def setMaxLevel(self, value):
        self._setNumber(1, value)

    def getCurrentLevel(self):
        return self._getNumber(2)

    def setCurrentLevel(self, value):
        self._setNumber(2, value)

    def getItemId(self):
        return self._getNumber(3)

    def setItemId(self, value):
        self._setNumber(3, value)

    def getScaleFactor(self):
        return self._getString(4)

    def setScaleFactor(self, value):
        self._setString(4, value)

    def getItemUserString(self):
        return self._getString(5)

    def setItemUserString(self, value):
        self._setString(5, value)

    def getItemType(self):
        return self._getString(6)

    def setItemType(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(ItemModel, self)._initialize()
        self._addViewModelProperty('eachLevelInfo', UserListModel())
        self._addNumberProperty('maxLevel', -1)
        self._addNumberProperty('currentLevel', -1)
        self._addNumberProperty('itemId', 0)
        self._addStringProperty('scaleFactor', '')
        self._addStringProperty('itemUserString', '')
        self._addStringProperty('itemType', '')
