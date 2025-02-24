# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/special_crew.py
import typing
from debug_utils import LOG_WARNING
from items.components.component_constants import EMPTY_STRING
from items.components.tankmen_components import SPECIAL_CREW_TAG
from items.tankmen import hasTagInTankmenGroup, unpackCrewParams, getTankmenWithTag, getNationGroups
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleType
    from items.tankmen import TankmanDescr
    from gui.shared.gui_items.Tankman import Tankman

class CustomCrew(object):
    SABATON = 'sabaton'
    OFFSPRING = 'offspring'
    YHA = 'yha'
    WITCHES = 'witches'
    TAG_MAP = {SPECIAL_CREW_TAG.SABATON: SABATON,
     SPECIAL_CREW_TAG.OFFSPRING: OFFSPRING,
     SPECIAL_CREW_TAG.YHA: YHA,
     SPECIAL_CREW_TAG.WITCHES_CREW: WITCHES}

    @staticmethod
    def hasTagInTankmen(tankmanDescr, tag):
        return hasTagInTankmenGroup(tankmanDescr.nationID, tankmanDescr.gid, tankmanDescr.isPremium, tag)

    @staticmethod
    def getTankmanCrewName(tankmanDescr):
        return CustomCrew.getCrewName(tankmanDescr.nationID, tankmanDescr.gid, tankmanDescr.isPremium)

    @staticmethod
    def getCrewName(nationID, groupID, isPremium):
        nationGroups = getNationGroups(nationID, isPremium)
        if groupID not in nationGroups:
            LOG_WARNING('special_crew.CustomCrew.getCrewName: wrong value of the groupID (unknown groupID)', groupID)
            return EMPTY_STRING
        tags = list(nationGroups[groupID].tags.intersection(CustomCrew.TAG_MAP.iterkeys()))
        return CustomCrew.TAG_MAP.get(tags[0]) if tags else EMPTY_STRING


class CustomSkills(object):
    SABATON_BROTHERHOOD = 'sabaton_brotherhood'
    OFFSPRING_BROTHERHOOD = 'offspring_brotherhood'
    YHA_BROTHERHOOD = 'yha_brotherhood'
    WITCHES_BROTHERHOOD = 'witches_brotherhood'
    CUSTOM_CREW_MAP = {CustomCrew.SABATON: {'brotherhood': SABATON_BROTHERHOOD},
     CustomCrew.OFFSPRING: {'brotherhood': OFFSPRING_BROTHERHOOD},
     CustomCrew.YHA: {'brotherhood': YHA_BROTHERHOOD},
     CustomCrew.WITCHES: {'brotherhood': WITCHES_BROTHERHOOD}}

    @staticmethod
    def _getCustomSkill(skillName, customCrewName):
        return CustomSkills.CUSTOM_CREW_MAP.get(customCrewName, {}).get(skillName, EMPTY_STRING)

    @staticmethod
    def getCustomSkill(skillName, tankman=None, customCrewName=EMPTY_STRING):
        if tankman is not None:
            crewName = CustomCrew.getTankmanCrewName(tankman.descriptor)
            if crewName:
                return (crewName, CustomSkills._getCustomSkill(skillName, crewName))
        return (EMPTY_STRING, EMPTY_STRING) if not customCrewName else (customCrewName, CustomSkills._getCustomSkill(skillName, customCrewName))


def _isCrewCompleted(vehicleType, tankmenGroups, tag):
    _, _, isPremium = unpackCrewParams(tankmenGroups[0])
    nationID, _ = vehicleType.id
    requiredCrew = getTankmenWithTag(nationID, isPremium, tag)
    actualCrew = [ unpackCrewParams(tGroup)[0] for tGroup in tankmenGroups ]
    return set(actualCrew) <= requiredCrew if len(actualCrew) <= len(requiredCrew) else requiredCrew < set(actualCrew)


def isWitchesCrew(tankmanDescr):
    return CustomCrew.hasTagInTankmen(tankmanDescr, SPECIAL_CREW_TAG.WITCHES_CREW)


def isMihoCrewCompleted(vehicleType, tankmenGroups):
    return _isCrewCompleted(vehicleType, tankmenGroups, SPECIAL_CREW_TAG.MIHO)


def isMikaCrewCompleted(vehicleType, tankmenGroups):
    return _isCrewCompleted(vehicleType, tankmenGroups, SPECIAL_CREW_TAG.MIKA_CREW)


def isYhaCrewCompleted(vehicleType, tankmenGroups):
    return _isCrewCompleted(vehicleType, tankmenGroups, SPECIAL_CREW_TAG.YHA)


def isWitchesCrewCompleted(vehicleType, tankmenGroups):
    _, _, isPremium = unpackCrewParams(tankmenGroups[0])
    nationID, _ = vehicleType.id
    requiredGroupIDs = getTankmenWithTag(nationID, isPremium, SPECIAL_CREW_TAG.WITCHES_CREW)
    uniqueRoles = set([ role[0] for role in vehicleType.crewRoles ])
    actualGroupIDs = set([ unpackCrewParams(tGroup)[0] for tGroup in tankmenGroups ])
    return len(actualGroupIDs & requiredGroupIDs) == len(uniqueRoles)
