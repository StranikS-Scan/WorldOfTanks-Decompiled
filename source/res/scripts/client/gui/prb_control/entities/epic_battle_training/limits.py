# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/epic_battle_training/limits.py
from constants import PREBATTLE_ACCOUNT_STATE, PREBATTLE_TYPE
from gui.prb_control.entities.base.limits import AbstractTeamIsValid, LimitsCollection, VehicleIsValid, TeamNoPlayersInBattle, TeamIsValid
from skeletons.gui.shared import IItemsCache
from helpers import dependency
from items import vehicles

class ObserverInTeamIsValid(AbstractTeamIsValid):
    itemsCache = dependency.descriptor(IItemsCache)

    def check(self, rosters, team, teamLimits):
        accountsInfo = self._getAccountsInfo(rosters, team)
        if len(accountsInfo) < teamLimits['minCount']:
            return (False, 'limit/minCount')
        return (False, 'observers') if self.__isAllObservers(accountsInfo) else (True, '')

    @classmethod
    def __isAllObservers(cls, accountsInfo):
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
            if not cls.itemsCache.items.getItemByCD(vehTypeCompDescr).isObserver:
                return False

        return True


class EpicBattleTrainingLimits(LimitsCollection):

    def __init__(self, entity):
        super(EpicBattleTrainingLimits, self).__init__(entity, (VehicleIsValid(),), (TeamNoPlayersInBattle(PREBATTLE_TYPE.EPIC_TRAINING), TeamIsValid(), ObserverInTeamIsValid()))
