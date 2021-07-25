# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/detachmnet_convert_helper.py
import random
import typing
from crew2 import settings_globals
from crew2.conversion_helpers import convertCrewSkills
from crew2.crew2_consts import BOOL_TO_GENDER
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from items.components.detachment_constants import DetachmentAttrs, DETACHMENT_DEFAULT_PRESET
from items.detachment import DetachmentDescr
from items.instructor import InstructorDescr
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items import Vehicle
_COMMON_INSTRUCTORS = ('men1', 'women1')
_savedOverrides = {}

def __canUseRecruitPassport(recruit):
    characterProperties = settings_globals.g_characterProperties
    nationID = recruit.nationID
    gender = BOOL_TO_GENDER[recruit.isFemale]
    passportIsCommon = recruit.descriptor.firstNameID in characterProperties.getCommonFirstNameIDs(nationID, gender) and recruit.descriptor.lastNameID in characterProperties.getCommonSecondNameIDs(nationID, gender) and recruit.descriptor.iconID in characterProperties.getCommonPortraitIDs(nationID, gender)
    instructorSettings, _ = settings_globals.g_conversion.getInstructorForTankman(recruit.descriptor)
    return passportIsCommon and (instructorSettings is None or instructorSettings.name in _COMMON_INSTRUCTORS)


def __getDetachmentOverride(recruits, nationID):
    characterProperties = settings_globals.g_characterProperties
    detachmentIsFemale = None
    specialSkinID = NO_CREW_SKIN_ID
    for _, recruit in recruits:
        if not recruit:
            continue
        if detachmentIsFemale is None:
            detachmentIsFemale = recruit.isFemale
        skinIDForTankman = settings_globals.g_conversion.getSkinIDForTankman(recruit.descriptor)
        if skinIDForTankman and not specialSkinID:
            specialSkinID = skinIDForTankman
        if not __canUseRecruitPassport(recruit) or skinIDForTankman is not None:
            continue
        return ({DetachmentAttrs.IS_FEMALE: recruit.isFemale,
          DetachmentAttrs.CMDR_FIRST_NAME_ID: recruit.descriptor.firstNameID,
          DetachmentAttrs.CMDR_SECOND_NAME_ID: recruit.descriptor.lastNameID,
          DetachmentAttrs.CMDR_PORTRAIT_ID: recruit.descriptor.iconID}, specialSkinID or recruit.skinID)

    key = tuple((recruit.invID for _, recruit in recruits if recruit))
    if key not in _savedOverrides:
        gender = BOOL_TO_GENDER[detachmentIsFemale]
        _savedOverrides[key] = {DetachmentAttrs.IS_FEMALE: detachmentIsFemale,
         DetachmentAttrs.CMDR_FIRST_NAME_ID: random.choice(characterProperties.getCommonFirstNameIDs(nationID, gender)),
         DetachmentAttrs.CMDR_SECOND_NAME_ID: random.choice(characterProperties.getCommonSecondNameIDs(nationID, gender)),
         DetachmentAttrs.CMDR_PORTRAIT_ID: random.choice(characterProperties.getCommonPortraitIDs(nationID, gender))}
    return (_savedOverrides[key], specialSkinID)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isBarracksNotEmpty(nationID, tmenToExclude=None, excludeLockedCrew=True, itemsCache=None):
    criteria = REQ_CRITERIA.NATIONS([nationID]) | ~REQ_CRITERIA.TANKMAN.DISMISSED
    allTankmen = itemsCache.items.getTankmen(criteria)
    vehicleCriteria = ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
    if excludeLockedCrew:
        vehicleCriteria |= ~REQ_CRITERIA.VEHICLE.IS_CREW_LOCKED
    tmen = itemsCache.items.removeUnsuitableTankmen(allTankmen.values(), vehicleCriteria)
    if tmenToExclude:
        tmen = [ t for t in tmen if t.invID not in tmenToExclude ]
    return bool(tmen)


def getDetachmentFromVehicle(vehicle, recruits):
    conversion = settings_globals.g_conversion
    crewDescrs = [ (recruit.descriptor if recruit else None) for _, recruit in recruits ]
    leadersInCrew = len([ recruit for _, recruit in recruits if recruit and recruit.isLeader ])
    preset = conversion.getDetachmentForCrew(crewDescrs).name if leadersInCrew <= 1 else DETACHMENT_DEFAULT_PRESET
    isUnique = preset != DETACHMENT_DEFAULT_PRESET
    overrideCtx, skinID = None, NO_CREW_SKIN_ID
    if not isUnique:
        overrideCtx, skinID = __getDetachmentOverride(recruits, vehicle.nationID)
    vehCompDescr = vehicle.descriptor.makeCompactDescr()
    detDescr, instDescrs = DetachmentDescr.createByPreset(preset, vehCompDescr, overrideDetachmentCtx=overrideCtx)
    detachmentXP, _ = DetachmentDescr.getDetachmentXPFromVehicleCrew(crewDescrs)
    detDescr.addXP(detachmentXP)
    convertCrewSkills(detDescr, crewDescrs)
    return (detDescr,
     instDescrs,
     preset,
     skinID)
