# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/advanced_tooltip_content_model.py
from frameworks.wulf import ViewModel

class AdvancedTooltipContentModel(ViewModel):
    __slots__ = ()

    def getNormalContent(self):
        return self._getView(0)

    def setNormalContent(self, value):
        self._setView(0, value)

    def getAdvancedContent(self):
        return self._getView(1)

    def setAdvancedContent(self, value):
        self._setView(1, value)

    def getShowAnim(self):
        return self._getBool(2)

    def setShowAnim(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(AdvancedTooltipContentModel, self)._initialize()
        self._addViewProperty('normalContent')
        self._addViewProperty('advancedContent')
        self._addBoolProperty('showAnim', False)
