# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/demount_kit/selector_dialog_item_model.py
from frameworks.wulf import ViewModel

class SelectorDialogItemModel(ViewModel):
    __slots__ = ()
    GOLD = 'gold'
    DEMOUNT_KIT = 'demountKit'
    NOTHING = ''
    GOLD_TOOLTIP = 'goldAlternativeInfo'
    DK_TOOLTIP = 'awardDemountKit'

    def __init__(self, properties=7, commands=0):
        super(SelectorDialogItemModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getStorageCount(self):
        return self._getNumber(1)

    def setStorageCount(self, value):
        self._setNumber(1, value)

    def getIsDisabled(self):
        return self._getBool(2)

    def setIsDisabled(self, value):
        self._setBool(2, value)

    def getNeededItems(self):
        return self._getNumber(3)

    def setNeededItems(self, value):
        self._setNumber(3, value)

    def getIsItemEnough(self):
        return self._getBool(4)

    def setIsItemEnough(self, value):
        self._setBool(4, value)

    def getIsDiscount(self):
        return self._getBool(5)

    def setIsDiscount(self, value):
        self._setBool(5, value)

    def getTooltipName(self):
        return self._getString(6)

    def setTooltipName(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(SelectorDialogItemModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addNumberProperty('storageCount', 0)
        self._addBoolProperty('isDisabled', False)
        self._addNumberProperty('neededItems', 0)
        self._addBoolProperty('isItemEnough', True)
        self._addBoolProperty('isDiscount', False)
        self._addStringProperty('tooltipName', '')
