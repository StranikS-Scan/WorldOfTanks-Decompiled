# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/utils/detachment.py
import random
import nations
from typing import TYPE_CHECKING, Tuple, Any, List
from crew2 import settings_globals, crew2_consts
from crew2.crew2_consts import BOOL_TO_GENDER
from items.components.detachment_constants import DetachmentAttrs, DetachmentMaxValues, DetachmentConstants, INVALID_INSTRUCTOR_SLOT_ID
from items.components.detachment_components import getVehicleIdentification, raiseAttrException, getCommonClassForVehicles
if TYPE_CHECKING:
    from items.detachment import DetachmentDescr
    from items.instructor import InstructorDescr

def validateSpecialization(detDescr, vehTypeCompDescr):
    vehIdent = getVehicleIdentification(vehTypeCompDescr)
    if detDescr.nationID != vehIdent.nationID:
        return (False, 'vehicle with not suitable nation')
    elif detDescr.classID is not None and detDescr.classID != vehIdent.classID:
        return (False, 'vehicle with not suitable class')
    else:
        return (False, 'vehicle is premium') if vehIdent.isPremium else (True, '')


def validateInstructor(detDescr, instrDescr):
    return (False, 'instructor with not suitable nation') if detDescr.nationID != instrDescr.nationID else (True, '')


def validateNationID(_, val):
    return val != nations.NONE_INDEX and val <= DetachmentMaxValues.NATION_ID


def validateProgressionID(_, proID):
    return settings_globals.g_detachmentSettings.progression.getProgressionByID(proID) is not None and proID <= DetachmentMaxValues.PROGRESSION_ID


def validateLockMask(_, val):
    return val <= DetachmentMaxValues.LOCK_MASK


def validateMaxVehicleSlots(_, val):
    return val <= settings_globals.g_detachmentSettings.maxVehicleSlots


def validatePerksMatrixID(_, matrixID):
    return settings_globals.g_perkSettings.matrices.getMatrix(matrixID) is not None and matrixID <= DetachmentMaxValues.PERKS_MATRIX_ID


def validateInstructorSlots(_, slots):
    return isinstance(slots, list) and len(slots) <= settings_globals.g_detachmentSettings.maxInstructorSlots


def validateClass(detachment, val):
    if val is None:
        return False
    else:
        classID = getCommonClassForVehicles(detachment._vehicleSlots)
        return classID is None or val == classID


def validateVehicleSlots(detachment, slots):
    if not isinstance(slots, list):
        return False
    elif len(slots) > settings_globals.g_detachmentSettings.maxVehicleSlots:
        return False
    else:
        for vehTypeCompDescr in slots:
            if vehTypeCompDescr is not None:
                isOk, _ = validateSpecialization(detachment, vehTypeCompDescr)
                if not isOk:
                    return False

        return True


def validateCmdrFirstName(detachment, nameID):
    gender = crew2_consts.BOOL_TO_GENDER[detachment.isFemale]
    firstName = settings_globals.g_characterProperties.getFirstNameByID(detachment.nationID, nameID, gender)
    return firstName is not None


def validateCmdrSecondName(detachment, nameID):
    gender = crew2_consts.BOOL_TO_GENDER[detachment.isFemale]
    secondName = settings_globals.g_characterProperties.getSecondNameByID(detachment.nationID, nameID, gender)
    return secondName is not None


def validateCmdrPortrait(detachment, portraitID):
    gender = crew2_consts.BOOL_TO_GENDER[detachment.isFemale]
    portrait = settings_globals.g_characterProperties.getPortraitByID(detachment.nationID, portraitID, gender)
    return portrait is not None


def generateIsFemale(detachment):
    return bool(random.getrandbits(1))


def generateCmdrFirstName(detachment):
    gender = BOOL_TO_GENDER[detachment.isFemale]
    commonIDS = settings_globals.g_characterProperties.getCommonFirstNameIDs(detachment.nationID, gender)
    return random.choice(commonIDS)


def generateCmdrSecondName(detachment):
    gender = BOOL_TO_GENDER[detachment.isFemale]
    commonIDS = settings_globals.g_characterProperties.getCommonSecondNameIDs(detachment.nationID, gender)
    return random.choice(commonIDS)


def generateCmdrPortrait(detachment):
    gender = BOOL_TO_GENDER[detachment.isFemale]
    commonIDS = settings_globals.g_characterProperties.getCommonPortraitIDs(detachment.nationID, gender)
    return random.choice(commonIDS)


DETACHMENT_GENERATORS = ((DetachmentAttrs.PRESET_ID, DetachmentConstants.DEFAULT_ATTR_VAL),
 (DetachmentAttrs.NATION_ID, lambda _: raiseAttrException(DetachmentAttrs.NATION_ID)),
 (DetachmentAttrs.PROGRESSION_LAYOUT_ID, lambda _: raiseAttrException(DetachmentAttrs.PROGRESSION_LAYOUT_ID)),
 (DetachmentAttrs.PERKS_MATRIX_ID, lambda _: raiseAttrException(DetachmentAttrs.PERKS_MATRIX_ID)),
 (DetachmentAttrs.CLASS_ID, lambda _: raiseAttrException(DetachmentAttrs.CLASS_ID)),
 (DetachmentAttrs.LOCK_MASK, DetachmentConstants.DEFAULT_ATTR_VAL),
 (DetachmentAttrs.OPERATIONS_MASK, DetachmentConstants.DEFAULT_OPERATION_MASK),
 (DetachmentAttrs.MAX_VEHICLE_SLOTS, lambda _: settings_globals.g_detachmentSettings.maxVehicleSlots),
 (DetachmentAttrs.IS_FEMALE, generateIsFemale),
 (DetachmentAttrs.CMDR_FIRST_NAME_ID, generateCmdrFirstName),
 (DetachmentAttrs.CMDR_SECOND_NAME_ID, generateCmdrSecondName),
 (DetachmentAttrs.CMDR_PORTRAIT_ID, generateCmdrPortrait),
 (DetachmentAttrs.BUILD, {}),
 (DetachmentAttrs.EXPERIENCE, DetachmentConstants.DEFAULT_ATTR_VAL),
 (DetachmentAttrs.VEHICLE_SLOTS, [None]),
 (DetachmentAttrs.INSTRUCTOR_SLOTS, []),
 (DetachmentAttrs.ACTIVE_INSTRUCTOR_SLOT_ID, INVALID_INSTRUCTOR_SLOT_ID))
DETACHMENT_VALIDATORS = ((DetachmentAttrs.NATION_ID, validateNationID),
 (DetachmentAttrs.LOCK_MASK, validateLockMask),
 (DetachmentAttrs.MAX_VEHICLE_SLOTS, validateMaxVehicleSlots),
 (DetachmentAttrs.PROGRESSION_LAYOUT_ID, validateProgressionID),
 (DetachmentAttrs.PERKS_MATRIX_ID, validatePerksMatrixID),
 (DetachmentAttrs.CLASS_ID, validateClass),
 (DetachmentAttrs.VEHICLE_SLOTS, validateVehicleSlots),
 (DetachmentAttrs.INSTRUCTOR_SLOTS, validateInstructorSlots),
 (DetachmentAttrs.CMDR_FIRST_NAME_ID, validateCmdrFirstName),
 (DetachmentAttrs.CMDR_SECOND_NAME_ID, validateCmdrSecondName),
 (DetachmentAttrs.CMDR_PORTRAIT_ID, validateCmdrPortrait))
