# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/progressive_items_reward/progressive_items_reward_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class ProgressiveItemsRewardViewModel(ViewModel):
    __slots__ = ('onOkClick', 'onSecondaryClick')

    def __init__(self, properties=15, commands=2):
        super(ProgressiveItemsRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getIsNewItem(self):
        return self._getBool(0)

    def setIsNewItem(self, value):
        self._setBool(0, value)

    def getTankLevel(self):
        return self._getString(1)

    def setTankLevel(self, value):
        self._setString(1, value)

    def getShowTankLevel(self):
        return self._getBool(2)

    def setShowTankLevel(self, value):
        self._setBool(2, value)

    def getTankTypeIcon(self):
        return self._getResource(3)

    def setTankTypeIcon(self, value):
        self._setResource(3, value)

    def getTankName(self):
        return self._getString(4)

    def setTankName(self, value):
        self._setString(4, value)

    def getCongratsText(self):
        return self._getString(5)

    def setCongratsText(self, value):
        self._setString(5, value)

    def getItemName(self):
        return self._getString(6)

    def setItemName(self, value):
        self._setString(6, value)

    def getFormFactor(self):
        return self._getString(7)

    def setFormFactor(self, value):
        self._setString(7, value)

    def getItemIcons(self):
        return self._getArray(8)

    def setItemIcons(self, value):
        self._setArray(8, value)

    def getOkButtonLabel(self):
        return self._getString(9)

    def setOkButtonLabel(self, value):
        self._setString(9, value)

    def getOkButtonTooltip(self):
        return self._getString(10)

    def setOkButtonTooltip(self, value):
        self._setString(10, value)

    def getIsOkButtonEnabled(self):
        return self._getBool(11)

    def setIsOkButtonEnabled(self, value):
        self._setBool(11, value)

    def getSecondaryButtonLabel(self):
        return self._getString(12)

    def setSecondaryButtonLabel(self, value):
        self._setString(12, value)

    def getSecondaryButtonTooltip(self):
        return self._getString(13)

    def setSecondaryButtonTooltip(self, value):
        self._setString(13, value)

    def getIsSecondaryButtonEnabled(self):
        return self._getBool(14)

    def setIsSecondaryButtonEnabled(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(ProgressiveItemsRewardViewModel, self)._initialize()
        self._addBoolProperty('isNewItem', False)
        self._addStringProperty('tankLevel', '')
        self._addBoolProperty('showTankLevel', False)
        self._addResourceProperty('tankTypeIcon', R.invalid())
        self._addStringProperty('tankName', '')
        self._addStringProperty('congratsText', '')
        self._addStringProperty('itemName', '')
        self._addStringProperty('formFactor', '')
        self._addArrayProperty('itemIcons', Array())
        self._addStringProperty('okButtonLabel', '')
        self._addStringProperty('okButtonTooltip', '')
        self._addBoolProperty('isOkButtonEnabled', False)
        self._addStringProperty('secondaryButtonLabel', '')
        self._addStringProperty('secondaryButtonTooltip', '')
        self._addBoolProperty('isSecondaryButtonEnabled', False)
        self.onOkClick = self._addCommand('onOkClick')
        self.onSecondaryClick = self._addCommand('onSecondaryClick')
