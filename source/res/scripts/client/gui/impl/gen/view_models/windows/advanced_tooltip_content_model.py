# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/advanced_tooltip_content_model.py
from frameworks.wulf import ViewModel

class AdvancedTooltipContentModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(AdvancedTooltipContentModel, self).__init__(properties=properties, commands=commands)

    def getShowAnim(self):
        return self._getBool(0)

    def setShowAnim(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(AdvancedTooltipContentModel, self)._initialize()
        self._addBoolProperty('showAnim', False)
