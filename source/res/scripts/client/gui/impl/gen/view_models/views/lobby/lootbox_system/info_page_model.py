# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/info_page_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.box_model import BoxModel

class InfoPageModel(ViewModel):
    __slots__ = ('onShowVideo', 'onShowShop', 'onClose', 'onShowLootList', 'onPreview', 'onChosenCategory')

    def __init__(self, properties=9, commands=6):
        super(InfoPageModel, self).__init__(properties=properties, commands=commands)

    def getEventName(self):
        return self._getString(0)

    def setEventName(self, value):
        self._setString(0, value)

    def getBoxes(self):
        return self._getArray(1)

    def setBoxes(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBoxesType():
        return BoxModel

    def getChosenCategory(self):
        return self._getString(2)

    def setChosenCategory(self, value):
        self._setString(2, value)

    def getHasVideoButton(self):
        return self._getBool(3)

    def setHasVideoButton(self, value):
        self._setBool(3, value)

    def getHasShopButton(self):
        return self._getBool(4)

    def setHasShopButton(self, value):
        self._setBool(4, value)

    def getUseExternal(self):
        return self._getBool(5)

    def setUseExternal(self, value):
        self._setBool(5, value)

    def getHasLootListLink(self):
        return self._getBool(6)

    def setHasLootListLink(self, value):
        self._setBool(6, value)

    def getStartDate(self):
        return self._getNumber(7)

    def setStartDate(self, value):
        self._setNumber(7, value)

    def getEndDate(self):
        return self._getNumber(8)

    def setEndDate(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(InfoPageModel, self)._initialize()
        self._addStringProperty('eventName', '')
        self._addArrayProperty('boxes', Array())
        self._addStringProperty('chosenCategory', '')
        self._addBoolProperty('hasVideoButton', False)
        self._addBoolProperty('hasShopButton', False)
        self._addBoolProperty('useExternal', False)
        self._addBoolProperty('hasLootListLink', False)
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self.onShowVideo = self._addCommand('onShowVideo')
        self.onShowShop = self._addCommand('onShowShop')
        self.onClose = self._addCommand('onClose')
        self.onShowLootList = self._addCommand('onShowLootList')
        self.onPreview = self._addCommand('onPreview')
        self.onChosenCategory = self._addCommand('onChosenCategory')
