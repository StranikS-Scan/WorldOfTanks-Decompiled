# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/reward_model.py
from frameworks.wulf import ViewModel

class RewardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(RewardModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getHighlightIcon(self):
        return self._getString(2)

    def setHighlightIcon(self, value):
        self._setString(2, value)

    def getOverlayIcon(self):
        return self._getString(3)

    def setOverlayIcon(self, value):
        self._setString(3, value)

    def getTooltipId(self):
        return self._getString(4)

    def setTooltipId(self, value):
        self._setString(4, value)

    def getLabelCount(self):
        return self._getString(5)

    def setLabelCount(self, value):
        self._setString(5, value)

    def getDescription(self):
        return self._getString(6)

    def setDescription(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(RewardModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('icon', '')
        self._addStringProperty('highlightIcon', '')
        self._addStringProperty('overlayIcon', '')
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('labelCount', '')
        self._addStringProperty('description', '')
