# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/advanced_animated_tooltip_content_model.py
from frameworks.wulf import ViewModel

class AdvancedAnimatedTooltipContentModel(ViewModel):
    __slots__ = ()

    def getHeader(self):
        return self._getString(0)

    def setHeader(self, value):
        self._setString(0, value)

    def getBody(self):
        return self._getString(1)

    def setBody(self, value):
        self._setString(1, value)

    def getAnimation(self):
        return self._getString(2)

    def setAnimation(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(AdvancedAnimatedTooltipContentModel, self)._initialize()
        self._addStringProperty('header', '')
        self._addStringProperty('body', '')
        self._addStringProperty('animation', '')
