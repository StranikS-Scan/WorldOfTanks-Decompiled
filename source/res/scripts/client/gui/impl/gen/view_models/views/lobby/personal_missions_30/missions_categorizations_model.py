# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/missions_categorizations_model.py
from gui.impl.gen.view_models.views.lobby.personal_missions_30.common.enums import MissionCategory
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.mission_model import MissionModel

class MissionsCategorizationsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(MissionsCategorizationsModel, self).__init__(properties=properties, commands=commands)

    def getMissionsCategory(self):
        return MissionCategory(self._getString(0))

    def setMissionsCategory(self, value):
        self._setString(0, value.value)

    def getMissions(self):
        return self._getArray(1)

    def setMissions(self, value):
        self._setArray(1, value)

    @staticmethod
    def getMissionsType():
        return MissionModel

    def _initialize(self):
        super(MissionsCategorizationsModel, self)._initialize()
        self._addStringProperty('missionsCategory')
        self._addArrayProperty('missions', Array())
