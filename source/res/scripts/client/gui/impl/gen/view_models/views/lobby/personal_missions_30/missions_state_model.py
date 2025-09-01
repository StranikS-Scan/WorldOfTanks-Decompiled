# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/missions_state_model.py
from gui.impl.gen.view_models.views.lobby.personal_missions_30.common.enums import MissionCategory
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.missions_model import MissionsModel

class MissionsStateModel(ViewModel):
    __slots__ = ('changeCategory',)

    def __init__(self, properties=2, commands=1):
        super(MissionsStateModel, self).__init__(properties=properties, commands=commands)

    def getAllMissions(self):
        return self._getArray(0)

    def setAllMissions(self, value):
        self._setArray(0, value)

    @staticmethod
    def getAllMissionsType():
        return MissionsModel

    def getMissionsCategory(self):
        return MissionCategory(self._getString(1))

    def setMissionsCategory(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(MissionsStateModel, self)._initialize()
        self._addArrayProperty('allMissions', Array())
        self._addStringProperty('missionsCategory')
        self.changeCategory = self._addCommand('changeCategory')
