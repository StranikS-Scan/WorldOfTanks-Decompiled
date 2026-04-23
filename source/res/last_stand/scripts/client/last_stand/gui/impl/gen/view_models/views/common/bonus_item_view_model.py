# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/common/bonus_item_view_model.py
from frameworks.wulf import ViewModel

class BonusItemViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(BonusItemViewModel, self).__init__(properties=properties, commands=commands)

    def getUserName(self):
        return self._getString(0)

    def setUserName(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getValue(self):
        return self._getString(2)

    def setValue(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getString(3)

    def setIcon(self, value):
        self._setString(3, value)

    def getOverlayType(self):
        return self._getString(4)

    def setOverlayType(self, value):
        self._setString(4, value)

    def getTooltipId(self):
        return self._getString(5)

    def setTooltipId(self, value):
        self._setString(5, value)

    def getTooltipContentId(self):
        return self._getString(6)

    def setTooltipContentId(self, value):
        self._setString(6, value)

    def getLabel(self):
        return self._getString(7)

    def setLabel(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(BonusItemViewModel, self)._initialize()
        self._addStringProperty('userName', '')
        self._addStringProperty('name', '')
        self._addStringProperty('value', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('overlayType', '')
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('tooltipContentId', '')
        self._addStringProperty('label', '')
