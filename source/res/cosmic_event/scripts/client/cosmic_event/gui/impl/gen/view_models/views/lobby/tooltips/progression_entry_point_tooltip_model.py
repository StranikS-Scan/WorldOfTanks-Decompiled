# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/tooltips/progression_entry_point_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class ProgressionEntryPointTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(ProgressionEntryPointTooltipModel, self).__init__(properties=properties, commands=commands)

    def getBonuses(self):
        return self._getArray(0)

    def setBonuses(self, value):
        self._setArray(0, value)

    @staticmethod
    def getBonusesType():
        return IconBonusModel

    def getMarsPoints(self):
        return self._getNumber(1)

    def setMarsPoints(self, value):
        self._setNumber(1, value)

    def getMarsPointsLimit(self):
        return self._getNumber(2)

    def setMarsPointsLimit(self, value):
        self._setNumber(2, value)

    def getCurrentProgressSectionIndex(self):
        return self._getNumber(3)

    def setCurrentProgressSectionIndex(self, value):
        self._setNumber(3, value)

    def getSeasonEnd(self):
        return self._getNumber(4)

    def setSeasonEnd(self, value):
        self._setNumber(4, value)

    def getIsProgressionFinished(self):
        return self._getBool(5)

    def setIsProgressionFinished(self, value):
        self._setBool(5, value)

    def getIsSomethingHappeningWithArtefact(self):
        return self._getBool(6)

    def setIsSomethingHappeningWithArtefact(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(ProgressionEntryPointTooltipModel, self)._initialize()
        self._addArrayProperty('bonuses', Array())
        self._addNumberProperty('marsPoints', 0)
        self._addNumberProperty('marsPointsLimit', 0)
        self._addNumberProperty('currentProgressSectionIndex', 0)
        self._addNumberProperty('seasonEnd', 0)
        self._addBoolProperty('isProgressionFinished', False)
        self._addBoolProperty('isSomethingHappeningWithArtefact', False)
