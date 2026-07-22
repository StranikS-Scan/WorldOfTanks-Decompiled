# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/gen/view_models/views/lobby/tank_academy/tank_academy_entry_point_view_model.py
from gui.impl.gen.view_models.views.lobby.hangar.header_widget_view_model import HeaderWidgetViewModel

class TankAcademyEntryPointViewModel(HeaderWidgetViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=8, commands=2):
        super(TankAcademyEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getIsMainViewVisited(self):
        return self._getBool(0)

    def setIsMainViewVisited(self, value):
        self._setBool(0, value)

    def getCurrentProgress(self):
        return self._getNumber(1)

    def setCurrentProgress(self, value):
        self._setNumber(1, value)

    def getMaxProgress(self):
        return self._getNumber(2)

    def setMaxProgress(self, value):
        self._setNumber(2, value)

    def getQuestNumber(self):
        return self._getNumber(3)

    def setQuestNumber(self, value):
        self._setNumber(3, value)

    def getIsCompleted(self):
        return self._getBool(4)

    def setIsCompleted(self, value):
        self._setBool(4, value)

    def getIsPaused(self):
        return self._getBool(5)

    def setIsPaused(self, value):
        self._setBool(5, value)

    def getUnobtainedVehiclesCount(self):
        return self._getNumber(6)

    def setUnobtainedVehiclesCount(self, value):
        self._setNumber(6, value)

    def getEndDate(self):
        return self._getNumber(7)

    def setEndDate(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(TankAcademyEntryPointViewModel, self)._initialize()
        self._addBoolProperty('isMainViewVisited', False)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('maxProgress', 0)
        self._addNumberProperty('questNumber', 0)
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('isPaused', False)
        self._addNumberProperty('unobtainedVehiclesCount', 0)
        self._addNumberProperty('endDate', 0)
        self.onClick = self._addCommand('onClick')
