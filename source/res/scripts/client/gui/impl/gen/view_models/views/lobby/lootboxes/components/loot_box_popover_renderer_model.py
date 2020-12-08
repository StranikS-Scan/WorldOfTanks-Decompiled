# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/components/loot_box_popover_renderer_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class LootBoxPopoverRendererModel(ViewModel):
    __slots__ = ('onEventBtnClick',)

    def __init__(self, properties=10, commands=1):
        super(LootBoxPopoverRendererModel, self).__init__(properties=properties, commands=commands)

    def getLabelStr(self):
        return self._getString(0)

    def setLabelStr(self, value):
        self._setString(0, value)

    def getLabelDesc(self):
        return self._getString(1)

    def setLabelDesc(self, value):
        self._setString(1, value)

    def getId(self):
        return self._getNumber(2)

    def setId(self, value):
        self._setNumber(2, value)

    def getBtnLabel(self):
        return self._getResource(3)

    def setBtnLabel(self, value):
        self._setResource(3, value)

    def getIsOrangeBtn(self):
        return self._getBool(4)

    def setIsOrangeBtn(self, value):
        self._setBool(4, value)

    def getIsBrowserIconVisible(self):
        return self._getBool(5)

    def setIsBrowserIconVisible(self, value):
        self._setBool(5, value)

    def getCount(self):
        return self._getNumber(6)

    def setCount(self, value):
        self._setNumber(6, value)

    def getIsLastElement(self):
        return self._getBool(7)

    def setIsLastElement(self, value):
        self._setBool(7, value)

    def getIsEnabled(self):
        return self._getBool(8)

    def setIsEnabled(self, value):
        self._setBool(8, value)

    def getIsAvailable(self):
        return self._getBool(9)

    def setIsAvailable(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(LootBoxPopoverRendererModel, self)._initialize()
        self._addStringProperty('labelStr', '')
        self._addStringProperty('labelDesc', '')
        self._addNumberProperty('id', 0)
        self._addResourceProperty('btnLabel', R.invalid())
        self._addBoolProperty('isOrangeBtn', False)
        self._addBoolProperty('isBrowserIconVisible', False)
        self._addNumberProperty('count', 0)
        self._addBoolProperty('isLastElement', False)
        self._addBoolProperty('isEnabled', True)
        self._addBoolProperty('isAvailable', True)
        self.onEventBtnClick = self._addCommand('onEventBtnClick')
