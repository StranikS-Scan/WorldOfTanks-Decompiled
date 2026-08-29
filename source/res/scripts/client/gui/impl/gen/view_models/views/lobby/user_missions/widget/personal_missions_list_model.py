# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/widget/personal_missions_list_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.user_missions.widget.personal_mission_model import PersonalMissionModel

class PersonalMissionsListModel(ViewModel):
    __slots__ = ('onClick', 'onMarkAsViewed')

    def __init__(self, properties=2, commands=2):
        super(PersonalMissionsListModel, self).__init__(properties=properties, commands=commands)

    def getMissions(self):
        return self._getArray(0)

    def setMissions(self, value):
        self._setArray(0, value)

    @staticmethod
    def getMissionsType():
        return PersonalMissionModel

    def getReadyForAnimations(self):
        return self._getBool(1)

    def setReadyForAnimations(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(PersonalMissionsListModel, self)._initialize()
        self._addArrayProperty('missions', Array())
        self._addBoolProperty('readyForAnimations', False)
        self.onClick = self._addCommand('onClick')
        self.onMarkAsViewed = self._addCommand('onMarkAsViewed')
