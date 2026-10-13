# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/progression/progression_view_model.py
from frameworks.wulf import Array, ViewModel
from fort_rush.gui.impl.gen.view_models.views.progression.milestone_model import MilestoneModel
from fort_rush.gui.impl.gen.view_models.views.progression.mission_model import MissionModel

class ProgressionViewModel(ViewModel):
    __slots__ = ('onMessageClick',)

    def __init__(self, properties=7, commands=1):
        super(ProgressionViewModel, self).__init__(properties=properties, commands=commands)

    def getEventStartDateTime(self):
        return self._getNumber(0)

    def setEventStartDateTime(self, value):
        self._setNumber(0, value)

    def getEventEndDateTime(self):
        return self._getNumber(1)

    def setEventEndDateTime(self, value):
        self._setNumber(1, value)

    def getNewMissionsDateTime(self):
        return self._getNumber(2)

    def setNewMissionsDateTime(self, value):
        self._setNumber(2, value)

    def getMissions(self):
        return self._getArray(3)

    def setMissions(self, value):
        self._setArray(3, value)

    @staticmethod
    def getMissionsType():
        return MissionModel

    def getPreviousEventPoints(self):
        return self._getNumber(4)

    def setPreviousEventPoints(self, value):
        self._setNumber(4, value)

    def getCurrentEventPoints(self):
        return self._getNumber(5)

    def setCurrentEventPoints(self, value):
        self._setNumber(5, value)

    def getMilestones(self):
        return self._getArray(6)

    def setMilestones(self, value):
        self._setArray(6, value)

    @staticmethod
    def getMilestonesType():
        return MilestoneModel

    def _initialize(self):
        super(ProgressionViewModel, self)._initialize()
        self._addNumberProperty('eventStartDateTime', 0)
        self._addNumberProperty('eventEndDateTime', 0)
        self._addNumberProperty('newMissionsDateTime', 0)
        self._addArrayProperty('missions', Array())
        self._addNumberProperty('previousEventPoints', 0)
        self._addNumberProperty('currentEventPoints', 0)
        self._addArrayProperty('milestones', Array())
        self.onMessageClick = self._addCommand('onMessageClick')
