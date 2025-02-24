# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/cosmic_lobby_view/medal_model.py
from frameworks.wulf import ViewModel

class MedalModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(MedalModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getTooltipId(self):
        return self._getString(1)

    def setTooltipId(self, value):
        self._setString(1, value)

    def getTooltipContentId(self):
        return self._getString(2)

    def setTooltipContentId(self, value):
        self._setString(2, value)

    def getIsReceived(self):
        return self._getBool(3)

    def setIsReceived(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(MedalModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('tooltipContentId', '')
        self._addBoolProperty('isReceived', False)
