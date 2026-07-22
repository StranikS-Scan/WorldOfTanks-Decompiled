# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/gen/view_models/views/lobby/tank_academy/tank_academy_vehicles_selection_tabs_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.quest_view_model import QuestViewModel

class TankAcademyVehiclesSelectionTabsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(TankAcademyVehiclesSelectionTabsModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getIsSelected(self):
        return self._getBool(1)

    def setIsSelected(self, value):
        self._setBool(1, value)

    def getIsNew(self):
        return self._getBool(2)

    def setIsNew(self, value):
        self._setBool(2, value)

    def getIsDone(self):
        return self._getBool(3)

    def setIsDone(self, value):
        self._setBool(3, value)

    def getIsPremium(self):
        return self._getBool(4)

    def setIsPremium(self, value):
        self._setBool(4, value)

    def getTokensCount(self):
        return self._getNumber(5)

    def setTokensCount(self, value):
        self._setNumber(5, value)

    def getTasks(self):
        return self._getArray(6)

    def setTasks(self, value):
        self._setArray(6, value)

    @staticmethod
    def getTasksType():
        return QuestViewModel

    def _initialize(self):
        super(TankAcademyVehiclesSelectionTabsModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isNew', False)
        self._addBoolProperty('isDone', False)
        self._addBoolProperty('isPremium', False)
        self._addNumberProperty('tokensCount', 0)
        self._addArrayProperty('tasks', Array())
