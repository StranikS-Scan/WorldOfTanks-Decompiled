# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/squad/components.py
import typing
import account_helpers
from constants import PLATOON_RESTRICTED_VEHICLE_TAGS
from items import vehicles
if typing.TYPE_CHECKING:
    from gui.prb_control.entities.base.squad.entity import SquadEntity

def getRestrictedVehicleClassTag(vehicleTags):
    for tag in PLATOON_RESTRICTED_VEHICLE_TAGS:
        if tag in vehicleTags:
            return tag

    return None


class RestrictedRoleTagDataProvider(object):
    __slots__ = ('_unitEntity',)

    def __init__(self):
        self._unitEntity = None
        return

    def init(self, unitEntity):
        self._unitEntity = unitEntity

    def fini(self):
        self._unitEntity = None
        return

    def isValid(self):
        return self._unitEntity is not None

    def getRestrictionLevels(self, roleTag):
        return self.squadRestrictions.get(roleTag, {}).get('levels', [])

    def getMaxPossibleVehicles(self, roleTag):
        return self.squadRestrictions.get(roleTag, {}).get('maxCount', 0)

    def hasSlotForVehicle(self, roleTag):
        accountDbID = account_helpers.getAccountDatabaseID()
        return self.getMaxPossibleVehicles(roleTag) > 0 and (self.getCurrentVehiclesCount(roleTag) < self.getMaxPossibleVehicles(roleTag) or self._unitEntity.isCommander(accountDbID))

    def getCurrentVehiclesCount(self, roleTag):
        enableVehicleCount = 0
        _, unit = self._unitEntity.getUnit(safe=True)
        if unit is None:
            return enableVehicleCount
        else:
            unitVehicles = unit.getVehicles()
            for _, vInfos in unitVehicles.iteritems():
                for vInfo in vInfos:
                    vehType = vehicles.getVehicleType(vInfo.vehTypeCompDescr)
                    if self.getRestrictionLevels(roleTag) and vehType.level not in self.getRestrictionLevels(roleTag):
                        continue
                    vehicleTag = getRestrictedVehicleClassTag(vehType.tags)
                    if roleTag == vehicleTag:
                        enableVehicleCount += 1

            return enableVehicleCount

    def isTagVehicleAvailable(self, tags):
        accountDbID = account_helpers.getAccountDatabaseID()
        roleTag = getRestrictedVehicleClassTag(tags)
        if roleTag is None or roleTag not in self.squadRestrictions:
            return True
        availableVehicles = self.getMaxPossibleVehicles(roleTag) - self.getCurrentVehiclesCount(roleTag)
        if self.getMaxPossibleVehicles(roleTag) == 0:
            return False
        elif self._unitEntity.isCommander(accountDbID):
            return True
        elif availableVehicles == 0:
            _, _ = self._unitEntity.getUnit()
            vInfos = self._unitEntity.getVehiclesInfo()
            for vInfo in vInfos:
                if self.getRestrictionLevels(roleTag) is not None and vInfo.vehLevel not in self.getRestrictionLevels(roleTag):
                    continue
                vehicleTag = getRestrictedVehicleClassTag(vehicles.getVehicleType(vInfo.vehTypeCD).tags)
                if roleTag == vehicleTag:
                    return True

            return False
        else:
            return availableVehicles > 0

    @property
    def squadRestrictions(self):
        return self._unitEntity.squadRestrictions
