# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_main_widget_tooltip_model.py
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.common.ny_event_state_model import NyEventStateModel

class NyMainWidgetTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(NyMainWidgetTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def eventState(self):
        return self._getViewModel(0)

    @staticmethod
    def getEventStateType():
        return NyEventStateModel

    def getCurrentLevel(self):
        return self._getNumber(1)

    def setCurrentLevel(self, value):
        self._setNumber(1, value)

    def getCurrentPoints(self):
        return self._getNumber(2)

    def setCurrentPoints(self, value):
        self._setNumber(2, value)

    def getNextPoints(self):
        return self._getNumber(3)

    def setNextPoints(self, value):
        self._setNumber(3, value)

    def getDeltaFromPoints(self):
        return self._getNumber(4)

    def setDeltaFromPoints(self, value):
        self._setNumber(4, value)

    def getSecondsLeft(self):
        return self._getNumber(5)

    def setSecondsLeft(self, value):
        self._setNumber(5, value)

    def getIsFirstEntry(self):
        return self._getBool(6)

    def setIsFirstEntry(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(NyMainWidgetTooltipModel, self)._initialize()
        self._addViewModelProperty('eventState', NyEventStateModel())
        self._addNumberProperty('currentLevel', 1)
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('nextPoints', 0)
        self._addNumberProperty('deltaFromPoints', 0)
        self._addNumberProperty('secondsLeft', 0)
        self._addBoolProperty('isFirstEntry', False)
