# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/renewable_subscription_common/passive_xp.py
import typing
from items import vehicles, tankmen
from items.tankmen import TankmanDescr, VEHICLE_CLASS_TAGS
if typing.TYPE_CHECKING:
    from typing import Set

class _Tank(object):

    def __init__(self, vehicleType):
        self.vehicleType = vehicleType

    @property
    def isPremium(self):
        return 'premium' in self.vehicleType.tags

    @property
    def nation(self):
        return self.vehicleType.id[0]

    def isSameClass(self, tank):
        return bool(VEHICLE_CLASS_TAGS & self.vehicleType.tags & tank.vehicleType.tags)

    def __str__(self):
        return 'Tank: id:[{}], tags:[{}], isPremium:[{}], nation:[{}]'.format(self.vehicleType.id, self.vehicleType.tags, self.isPremium, self.nation)

    def __eq__(self, other):
        return self.vehicleType.id == other.vehicleType.id


class CrewSlotValidationResult(object):

    def __init__(self):
        self.isEmpty = False
        self.tManValidRes = None
        return


class ValidationResult(object):

    class ERRORS:
        NOT_PREMIUM = 1
        NOT_THE_SAME_CLASS = 2
        NOT_THE_SAME_NATION = 3
        NO_VEHICLE_ASSOCIATED = 4

    def __init__(self):
        self.isValid = True
        self.errorList = []

    def appendError(self, error):
        self.errorList.append(error)


class CrewValidator(object):

    def __init__(self, vehicleType):
        self.tank = _Tank(vehicleType)

    def validateCrew(self, crew):
        return [ self.validateCrewSlot(compactDescr) for compactDescr in crew ]

    def validateCrewSlot(self, compactDescr):
        result = CrewSlotValidationResult()
        if not compactDescr:
            result.isEmpty = True
        else:
            result.tManValidRes = self._isTankmanOk(tankmen.TankmanDescr(compactDescr))
        return result

    def _isTankmanOk(self, tmanDescr):
        result = ValidationResult()
        if tmanDescr.vehicleTypeID is None:
            result.isValid = False
            result.appendError(ValidationResult.ERRORS.NO_VEHICLE_ASSOCIATED)
            return result
        else:
            associatedVehType = vehicles.g_cache.vehicle(tmanDescr.nationID, tmanDescr.vehicleTypeID)
            associatedTank = _Tank(associatedVehType)
            if associatedTank == self.tank:
                return result
            if not self.tank.isPremium:
                result.isValid = False
                result.appendError(ValidationResult.ERRORS.NOT_PREMIUM)
            if not self.tank.isSameClass(associatedTank):
                result.isValid = False
                result.appendError(ValidationResult.ERRORS.NOT_THE_SAME_CLASS)
            if self.tank.nation != associatedTank.nation:
                result.isValid = False
                result.appendError(ValidationResult.ERRORS.NOT_THE_SAME_NATION)
            return result


FORBIDDEN_TAGS = {'event_battles',
 'fallout',
 'epic_battles',
 'bob',
 'battle_royale'}

def isTagsSetOk(tags):
    improperTags = FORBIDDEN_TAGS.intersection(tags)
    return len(improperTags) == 0
