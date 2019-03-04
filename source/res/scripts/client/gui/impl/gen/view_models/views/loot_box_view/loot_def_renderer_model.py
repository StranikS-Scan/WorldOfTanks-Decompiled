# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_def_renderer_model.py
from frameworks.wulf import ViewModel

class LootDefRendererModel(ViewModel):
    __slots__ = ()

    def getLabelStr(self):
        return self._getString(0)

    def setLabelStr(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getTooltipId(self):
        return self._getNumber(2)

    def setTooltipId(self, value):
        self._setNumber(2, value)

    def getRendererType(self):
        return self._getString(3)

    def setRendererType(self, value):
        self._setString(3, value)

    def getIsSmall(self):
        return self._getBool(4)

    def setIsSmall(self, value):
        self._setBool(4, value)

    def getHasCompensation(self):
        return self._getBool(5)

    def setHasCompensation(self, value):
        self._setBool(5, value)

    def getLabelAlign(self):
        return self._getString(6)

    def setLabelAlign(self, value):
        self._setString(6, value)

    def getHighlightType(self):
        return self._getString(7)

    def setHighlightType(self, value):
        self._setString(7, value)

    def getOverlayType(self):
        return self._getString(8)

    def setOverlayType(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(LootDefRendererModel, self)._initialize()
        self._addStringProperty('labelStr', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('tooltipId', 0)
        self._addStringProperty('rendererType', '')
        self._addBoolProperty('isSmall', False)
        self._addBoolProperty('hasCompensation', False)
        self._addStringProperty('labelAlign', 'center')
        self._addStringProperty('highlightType', '')
        self._addStringProperty('overlayType', '')
