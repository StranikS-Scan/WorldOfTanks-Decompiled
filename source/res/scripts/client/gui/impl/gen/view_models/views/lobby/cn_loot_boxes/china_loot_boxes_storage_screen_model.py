# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/cn_loot_boxes/china_loot_boxes_storage_screen_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.storage_box_model import StorageBoxModel

class ChinaLootBoxesStorageScreenModel(ViewModel):
    __slots__ = ('onBuyBoxes', 'onClose')

    def __init__(self, properties=9, commands=2):
        super(ChinaLootBoxesStorageScreenModel, self).__init__(properties=properties, commands=commands)

    @property
    def boxes(self):
        return self._getViewModel(0)

    @staticmethod
    def getBoxesType():
        return StorageBoxModel

    def getBoxesLeft(self):
        return self._getNumber(1)

    def setBoxesLeft(self, value):
        self._setNumber(1, value)

    def getEventEndTimeLeft(self):
        return self._getNumber(2)

    def setEventEndTimeLeft(self, value):
        self._setNumber(2, value)

    def getTimeLeft(self):
        return self._getNumber(3)

    def setTimeLeft(self, value):
        self._setNumber(3, value)

    def getIsLootBoxesEnabled(self):
        return self._getBool(4)

    def setIsLootBoxesEnabled(self, value):
        self._setBool(4, value)

    def getIsBuyAvailable(self):
        return self._getBool(5)

    def setIsBuyAvailable(self, value):
        self._setBool(5, value)

    def getIsLastDay(self):
        return self._getBool(6)

    def setIsLastDay(self, value):
        self._setBool(6, value)

    def getDayLimit(self):
        return self._getNumber(7)

    def setDayLimit(self, value):
        self._setNumber(7, value)

    def getIsEntitlementCacheInited(self):
        return self._getBool(8)

    def setIsEntitlementCacheInited(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(ChinaLootBoxesStorageScreenModel, self)._initialize()
        self._addViewModelProperty('boxes', UserListModel())
        self._addNumberProperty('boxesLeft', 0)
        self._addNumberProperty('eventEndTimeLeft', 0)
        self._addNumberProperty('timeLeft', 0)
        self._addBoolProperty('isLootBoxesEnabled', False)
        self._addBoolProperty('isBuyAvailable', False)
        self._addBoolProperty('isLastDay', False)
        self._addNumberProperty('dayLimit', 0)
        self._addBoolProperty('isEntitlementCacheInited', True)
        self.onBuyBoxes = self._addCommand('onBuyBoxes')
        self.onClose = self._addCommand('onClose')
