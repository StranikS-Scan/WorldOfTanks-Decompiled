# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/tankman_tooltip_view_model.py
from frameworks.wulf import ViewModel

class TankmanTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(TankmanTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getSubtitle(self):
        return self._getString(1)

    def setSubtitle(self, value):
        self._setString(1, value)

    def getMainIcon(self):
        return self._getString(2)

    def setMainIcon(self, value):
        self._setString(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getIconsTitle(self):
        return self._getString(4)

    def setIconsTitle(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(TankmanTooltipViewModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('subtitle', '')
        self._addStringProperty('mainIcon', '')
        self._addStringProperty('description', '')
        self._addStringProperty('iconsTitle', '')
