# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/crew_header_model.py
from gui.impl.gen.view_models.views.lobby.crew.idle_crew_bonus import IdleCrewBonus

class CrewHeaderModel(IdleCrewBonus):
    __slots__ = ('onCrewOperationsClick', 'onAccelerateCrewTrainingToggle', 'onIdleCrewBonusToggle')

    def __init__(self, properties=3, commands=3):
        super(CrewHeaderModel, self).__init__(properties=properties, commands=commands)

    def getIsAccelerateCrewTrainingActive(self):
        return self._getBool(1)

    def setIsAccelerateCrewTrainingActive(self, value):
        self._setBool(1, value)

    def getIsAccelerateCrewTrainingAvailable(self):
        return self._getBool(2)

    def setIsAccelerateCrewTrainingAvailable(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(CrewHeaderModel, self)._initialize()
        self._addBoolProperty('isAccelerateCrewTrainingActive', False)
        self._addBoolProperty('isAccelerateCrewTrainingAvailable', False)
        self.onCrewOperationsClick = self._addCommand('onCrewOperationsClick')
        self.onAccelerateCrewTrainingToggle = self._addCommand('onAccelerateCrewTrainingToggle')
        self.onIdleCrewBonusToggle = self._addCommand('onIdleCrewBonusToggle')
