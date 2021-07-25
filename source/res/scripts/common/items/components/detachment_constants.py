# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/detachment_constants.py
from items.components import StrEnum
from enum import IntEnum
from collections import namedtuple

class PaidOperationsContants(StrEnum):
    PARAM_EXP = 'exp'
    PARAM_EXP_MULTIPLIER = 'expMult'


class ExcludeInstructorOption(IntEnum):
    PAID = 0
    FREE = 1


class DemobilizeReason(IntEnum):
    DISMISS = 0
    SELL_VEHICLE = 1


class SpecializationPaymentType(IntEnum):
    GOLD = 0
    SILVER = 1
    FREE = 3


class SpecializationPaymentOption(IntEnum):
    GOLD = 0
    SILVER = 1
    SILVER_CLASS = 2
    FREE = 3
    FREE_CLASS = 4


SPECIALIZATION_PAYMENT_OPTION_TO_TYPE = {SpecializationPaymentOption.GOLD: SpecializationPaymentType.GOLD,
 SpecializationPaymentOption.SILVER: SpecializationPaymentType.SILVER,
 SpecializationPaymentOption.SILVER_CLASS: SpecializationPaymentType.SILVER,
 SpecializationPaymentOption.FREE: SpecializationPaymentType.FREE,
 SpecializationPaymentOption.FREE_CLASS: SpecializationPaymentType.FREE}
SPECIALIZATION_WITH_CHANGE_CLASS = (SpecializationPaymentOption.GOLD, SpecializationPaymentOption.SILVER_CLASS, SpecializationPaymentOption.FREE_CLASS)
REQUIRED_DROP_SKILL = {SpecializationPaymentOption.GOLD: False,
 SpecializationPaymentOption.SILVER: True,
 SpecializationPaymentOption.SILVER_CLASS: True,
 SpecializationPaymentOption.FREE: True,
 SpecializationPaymentOption.FREE_CLASS: True}

class ChangePerksMode(IntEnum):
    ADD_PERKS = 0
    DROP_PARTIAL = 1
    DROP_ALL = 2


class DropSkillPaymentOption(IntEnum):
    DEFAULT = 0
    FIRST = 1
    NEXT = 2


class DetachmentRemovingOptions(IntEnum):
    NO_REMOVE_INSTRUCTORS = 0
    REMOVE_ALL_INSTRUCTORS = 1
    REMOVE_LOCKED_INSTRUCTORS = 2


class DetachmentOperations(StrEnum):
    ASSIGN = 'assign'
    UNLOCK_VEHICLE_SLOT = 'expandSpecialization'
    SPECIALIZE_VEHICLE_SLOT = 'specialization'
    SPECIALIZE_VEHICLE_SLOT_AND_ASSIGN = 'specializationAndAssignment'
    UNLOCK_SPECIALIZE_VEHICLE_SLOT_AND_ASSIGN = 'unlockSpecializationAndAssignment'
    FREE_TRAIN_DETACHMENT = 'freeXPToDetXPRate'
    RECOVER_INSTRUCTOR = 'recoverInstructor'
    ADD_INSTRUCTOR_TO_SLOT = 'addInstructor'
    REMOVE_INSTRUCTOR_FROM_SLOT = 'removeInstructor'
    SPEED_UP_TRAINING_XP_FROM_VEH_RATE = 'speedUpTrainingXPFromVehRate'
    SPEED_UP_TRAINING_XP_TO_DET_RATE = 'speedUpTrainingXPToDetRate'
    DROP_SKILL = 'dropSkill'
    DISSOLVE = 'dissolve'
    RESTORE = 'restore'
    COMPLEX = '_complex'


class DetachmentSlotType(IntEnum):
    VEHICLES = 0
    INSTRUCTORS = 1


class DetachmentOperationsMaskBits(IntEnum):
    FIRST_DROP_SKILL_PRICE = 1
    NEXT_DROP_SKILL_PRICE = 2


DROP_SKILL_PAYMENT_OPTIONS = [(DetachmentOperationsMaskBits.FIRST_DROP_SKILL_PRICE, DropSkillPaymentOption.FIRST), (DetachmentOperationsMaskBits.NEXT_DROP_SKILL_PRICE, DropSkillPaymentOption.NEXT)]

class DetachmentConstants(object):
    DEFAULT_ATTR_VAL = 0
    DEFAULT_OPERATION_MASK = DetachmentOperationsMaskBits.FIRST_DROP_SKILL_PRICE


class DetachmentMaxValues(object):
    NATION_ID = 15
    PROGRESSION_ID = 65535
    LOCK_MASK = 65535
    PERKS_MATRIX_ID = 4080


class DetachmentLockMaskBits(IntEnum):
    DISSOLVE = 1
    POST_PROGRESSION = 2
    BUILD = 4
    COMMANDER_CUSTOMIZATION = 8
    VEHICLE_SLOTS = 240
    INSTRUCTORS = 3840
    DROP_SKILL = 4096


class DetachmentAttrs(StrEnum):
    PRESET_ID = '_presetID'
    NATION_ID = '_nationID'
    EXPERIENCE = '_experience'
    LOCK_MASK = '_lockMask'
    OPERATIONS_MASK = '_operationsMask'
    MAX_VEHICLE_SLOTS = '_maxVehicleSlots'
    PROGRESSION_LAYOUT_ID = '_progressionLayoutID'
    PERKS_MATRIX_ID = '_perksMatrixID'
    VEHICLE_SLOTS = '_vehicleSlots'
    INSTRUCTOR_SLOTS = '_instructorSlots'
    ACTIVE_INSTRUCTOR_SLOT_ID = '_activeInstructorSlotID'
    BUILD = '_build'
    CLASS_ID = '_classID'
    IS_FEMALE = '_isFemale'
    CMDR_FIRST_NAME_ID = '_cmdrFirstNameID'
    CMDR_SECOND_NAME_ID = '_cmdrSecondNameID'
    CMDR_PORTRAIT_ID = '_cmdrPortraitID'
    SLOTS_TRAITS = '__slotsTraits'


PerksOperationResult = namedtuple('PerksOperationResult', ['code', 'notValidIDs', 'build'])

class PerksOperationResultCode(IntEnum):
    NO_ERROR = 0
    PERK_NOT_VALID = 1
    PERK_NOT_IN_BUILD = 2
    PERK_MAX_LEVEL_REACHED = 3
    PERK_NEGATIVE_LEVEL = 4
    PERK_ZERO_LEVEL = 5
    PERK_NOT_IN_MATRIX = 6
    UPERK_ACTIVE_WRONG = 7
    LEVEL_LIMIT_REACHED = 8
    PERKS_RULES_FAILED = 9


class InstructorAttrs(StrEnum):
    SETTINGS_ID = '_settingsID'
    NATION_ID = '_nationID'
    PERKS_IDS = '_perksIDs'
    PROFESSION_ID = '_professionID'
    FIRST_NAME_ID = 'firstNameID'
    SECOND_NAME_ID = 'secondNameID'
    PORTRAIT_ID = 'portraitID'
    CLASS_ID = '_classID'
    IS_FEMALE = '_isFemale'
    VOICEOVER_ID = '_voiceOverID'
    PAGE_BACKGROUND = '_pageBackground'
    IS_INITED = '__isInited'


INSTRUCTOR_VOLATILE_PROPERTIES = (InstructorAttrs.FIRST_NAME_ID, InstructorAttrs.SECOND_NAME_ID, InstructorAttrs.PORTRAIT_ID)
INSTRUCTOR_VOLATILE_PROPERTIES_COUNT = len(INSTRUCTOR_VOLATILE_PROPERTIES)

class InstructorMaxValues(object):
    SETTINGS_ID = 65535
    NATION_ID = 15
    FIRST_NAME_ID = 65535
    SECOND_NAME_ID = 65535
    PORTRAIT_ID = 65535


class DetachmentConvertationPropertiesMasks(IntEnum):
    FULL_CREW = 1
    SPECIALIZATION = 2
    PRESET = 4
    EMPTY_MASK = 0


class RewardTypes(StrEnum):
    RANK = 'rank'
    BADGE_LEVEL = 'badgeLevel'
    SKILL_POINTS = 'skillPoints'
    AUTO_PERKS = 'autoPerks'
    SCHOOL_DISCOUNT = 'schoolDiscount'
    ACADEMY_DISCOUNT = 'academyDiscount'
    VEHICLE_SLOTS = 'vehicleSlots'
    INSTRUCTOR_SLOTS = 'instructorSlots'


class TypeDetachmentAssignToVehicle(IntEnum):
    IS_NONE = 0
    IS_BEST = 1
    IS_LAST = 2


POINTS_PER_LEVEL = 1
NO_DETACHMENT_ID = 0
NO_INSTRUCTOR_ID = 0
PROGRESS_MAX = 100
CREW2_BADGE_IDS = (200,)
BADGE_TOKEN_TMPL = 'crew2:badgeToken:{}'
DETACHMENT_DEFAULT_PRESET = 'Simple'
INVALID_INSTRUCTOR_SLOT_ID = -1
EMPTY_INSTRUCTOR_VOICEOVER = ''
INITIAL_BONUSES_OFFER_COUNT = 3
INSTRUCTOR_PROFESSIONS_NAMES = ('tactic', 'shooter', 'technician', 'driver', 'field')
INSTRUCTOR_PROFESSIONS_INDICES = dict(((n, i) for i, n in enumerate(INSTRUCTOR_PROFESSIONS_NAMES, 1)))
INSTRUCTOR_PROFESSIONS_MAP = {i:n for i, n in enumerate(INSTRUCTOR_PROFESSIONS_NAMES, 1)}
DOG_TAG = 'dog'
MAX_LONG = 4294967295L
