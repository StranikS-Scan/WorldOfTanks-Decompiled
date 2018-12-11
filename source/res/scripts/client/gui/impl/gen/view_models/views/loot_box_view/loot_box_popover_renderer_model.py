# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_box_popover_renderer_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class LootBoxPopoverRendererModel(ViewModel):
    __slots__ = ('onEventBtnClick',)

    def getLabelStr(self):
        return self._getString(0)

    def setLabelStr(self, value):
        self._setString(0, value)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getBtnLabel(self):
        return self._getResource(2)

    def setBtnLabel(self, value):
        self._setResource(2, value)

    def getIsOrangeBtn(self):
        return self._getBool(3)

    def setIsOrangeBtn(self, value):
        self._setBool(3, value)

    def getCount(self):
        return self._getNumber(4)

    def setCount(self, value):
        self._setNumber(4, value)

    def getIsLastElement(self):
        return self._getBool(5)

    def setIsLastElement(self, value):
        self._setBool(5, value)

    def getIsEnabled(self):
        return self._getBool(6)

    def setIsEnabled(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(LootBoxPopoverRendererModel, self)._initialize()
        self._addStringProperty('labelStr', '')
        self._addNumberProperty('id', 0)
        self._addResourceProperty('btnLabel', Resource.INVALID)
        self._addBoolProperty('isOrangeBtn', False)
        self._addNumberProperty('count', 0)
        self._addBoolProperty('isLastElement', False)
        self._addBoolProperty('isEnabled', True)
        self.onEventBtnClick = self._addCommand('onEventBtnClick')
