# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/side_bar_tab_model.py
from frameworks.wulf import ViewModel

class SideBarTabModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(SideBarTabModel, self).__init__(properties=properties, commands=commands)

    def getAlias(self):
        return self._getString(0)

    def setAlias(self, value):
        self._setString(0, value)

    def getTooltipHeader(self):
        return self._getString(1)

    def setTooltipHeader(self, value):
        self._setString(1, value)

    def getTooltipBody(self):
        return self._getString(2)

    def setTooltipBody(self, value):
        self._setString(2, value)

    def getLinkage(self):
        return self._getString(3)

    def setLinkage(self, value):
        self._setString(3, value)

    def getIcon(self):
        return self._getString(4)

    def setIcon(self, value):
        self._setString(4, value)

    def getEnabled(self):
        return self._getBool(5)

    def setEnabled(self, value):
        self._setBool(5, value)

    def getUnseenCount(self):
        return self._getNumber(6)

    def setUnseenCount(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(SideBarTabModel, self)._initialize()
        self._addStringProperty('alias', '')
        self._addStringProperty('tooltipHeader', '')
        self._addStringProperty('tooltipBody', '')
        self._addStringProperty('linkage', '')
        self._addStringProperty('icon', '')
        self._addBoolProperty('enabled', True)
        self._addNumberProperty('unseenCount', 0)
