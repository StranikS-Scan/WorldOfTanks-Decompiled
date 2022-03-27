# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/roster_view/roster_vehicle_crew_member_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_vehicle_crew_member_skill_view_model import RosterVehicleCrewMemberSkillViewModel

class CrewMemberType(Enum):
    COMMANDER = 'commander'
    GUNNER = 'gunner'
    DRIVER = 'driver'
    LOADER = 'loader'
    RADIOMAN = 'radioman'


class RosterVehicleCrewMemberViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RosterVehicleCrewMemberViewModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return CrewMemberType(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getSkills(self):
        return self._getArray(1)

    def setSkills(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(RosterVehicleCrewMemberViewModel, self)._initialize()
        self._addStringProperty('type')
        self._addArrayProperty('skills', Array())
