# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/race/race_widget_tooltip_model.py
from frameworks.wulf import ViewModel

class RaceWidgetTooltipModel(ViewModel):
    __slots__ = ()

    def getDays(self):
        return self._getString(0)

    def setDays(self, value):
        self._setString(0, value)

    def getIsEventStarted(self):
        return self._getBool(1)

    def setIsEventStarted(self, value):
        self._setBool(1, value)

    def getIsEventFinished(self):
        return self._getBool(2)

    def setIsEventFinished(self, value):
        self._setBool(2, value)

    def getTimeout(self):
        return self._getString(3)

    def setTimeout(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(RaceWidgetTooltipModel, self)._initialize()
        self._addStringProperty('days', '')
        self._addBoolProperty('isEventStarted', False)
        self._addBoolProperty('isEventFinished', False)
        self._addStringProperty('timeout', '')
