# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/rts_battles_training/limits.py
from constants import PREBATTLE_TYPE, PREBATTLE_ACCOUNT_STATE
from gui.prb_control.entities.base.limits import TeamNoPlayersInBattle, LimitsCollection, TeamIsValid, AbstractTeamIsValid
from gui.prb_control.entities.training.legacy.limits import TrainingVehicleIsValid
from helpers import dependency
from items import vehicles
from skeletons.gui.shared import IItemsCache

class CommanderInTeamIsValid(AbstractTeamIsValid):
    itemsCache = dependency.descriptor(IItemsCache)

    def check(self, rosters, team, teamLimits):
        accountsInfo = self._getAccountsInfo(rosters, team)
        if len(accountsInfo) < teamLimits['minCount']:
            return (False, 'limit/minCount')
        return (False, 'commanders') if self.__isAllCommanders(accountsInfo) else (True, '')

    @classmethod
    def __isAllCommanders(cls, accountsInfo):
        if not accountsInfo:
            return False
        for accInfo in accountsInfo.itervalues():
            if not accInfo['state'] & PREBATTLE_ACCOUNT_STATE.READY:
                continue
            if 'vehTypeCompDescr' not in accInfo or 'vehLevel' not in accInfo:
                vehDescr = vehicles.VehicleDescr(compactDescr=accInfo['vehCompDescr'])
                vehTypeCompDescr = vehDescr.type.compactDescr
            else:
                vehTypeCompDescr = accInfo['vehTypeCompDescr']
            veh = cls.itemsCache.items.getItemByCD(vehTypeCompDescr)
            if not veh.isObserver or veh.isCommander:
                return False

        return True


class RtsTrainingLimits(LimitsCollection):

    def __init__(self, entity):
        super(RtsTrainingLimits, self).__init__(entity, (TrainingVehicleIsValid(),), (TeamNoPlayersInBattle(PREBATTLE_TYPE.RTS_TRAINING), TeamIsValid(), CommanderInTeamIsValid()))
