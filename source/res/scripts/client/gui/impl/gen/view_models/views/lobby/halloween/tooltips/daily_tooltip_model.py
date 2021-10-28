# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/tooltips/daily_tooltip_model.py
from frameworks.wulf import ViewModel

class DailyTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DailyTooltipModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def getImage(self):
        return self._getString(2)

    def setImage(self, value):
        self._setString(2, value)

    def getFooter(self):
        return self._getString(3)

    def setFooter(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(DailyTooltipModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('type', '')
        self._addStringProperty('image', '')
        self._addStringProperty('footer', '')
