# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/roster_view/roster_vehicle_crew_member_skill_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class CrewMemberSkill(Enum):
    REPAIR = 'repair'
    FIREFIGHTING = 'fireFighting'
    CAMOUFLAGE = 'camouflage'
    BROTHERHOOD = 'brotherhood'
    COMMANDERTUTOR = 'commander_tutor'
    COMMANDEREAGLEEYE = 'commander_eagleEye'
    COMMANDERSIXTHSENSE = 'commander_sixthSense'
    COMMANDEREXPERT = 'commander_expert'
    COMMANDERUNIVERSALIST = 'commander_universalist'
    COMMANDERENEMYSHOTPREDICTOR = 'commander_enemyShotPredictor'
    DRIVERVIRTUOSO = 'driver_virtuoso'
    DRIVERSMOOTHDRIVING = 'driver_smoothDriving'
    DRIVERBADROADSKING = 'driver_badRoadsKing'
    DRIVERRAMMINGMASTER = 'driver_rammingMaster'
    DRIVERTIDYPERSON = 'driver_tidyPerson'
    GUNNERGUNSMITH = 'gunner_gunsmith'
    GUNNERSNIPER = 'gunner_sniper'
    GUNNERSMOOTHTURRET = 'gunner_smoothTurret'
    GUNNERRANCOROUS = 'gunner_rancorous'
    LOADERPEDANT = 'loader_pedant'
    LOADERDESPERADO = 'loader_desperado'
    LOADERINTUITION = 'loader_intuition'
    RADIOMANINVENTOR = 'radioman_inventor'
    RADIOMANFINDER = 'radioman_finder'
    RADIOMANRETRANSMITTER = 'radioman_retransmitter'
    RADIOMANLASTEFFORT = 'radioman_lastEffort'


class RosterVehicleCrewMemberSkillViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(RosterVehicleCrewMemberSkillViewModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return CrewMemberSkill(self._getString(0))

    def setName(self, value):
        self._setString(0, value.value)

    def _initialize(self):
        super(RosterVehicleCrewMemberSkillViewModel, self)._initialize()
        self._addStringProperty('name')
