# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dog_tags_common/config/common.py
from enum import Enum
from soft_exception import SoftException
DOG_TAGS_FILE = 'scripts/item_defs/dog_tags/dog_tags.xml'
DOG_TAGS_SCHEMA_FILE = 'scripts/item_defs/dog_tags/dog_tags_schema.xsd'
DEFAULT_GRADE = 0
NO_PROGRESS = 0

class ComponentViewType(Enum):
    BACKGROUND = 'background'
    ENGRAVING = 'engraving'

    def getTabIdx(self):
        if self == self.ENGRAVING:
            return 0
        return 1 if self == self.BACKGROUND else None


TRIUMPH_GRADES = 4
DEDICATION_GRADES = 10
SKILL_GRADES = 10
STARTING_COMPONENT_TYPES = (ComponentViewType.BACKGROUND, ComponentViewType.ENGRAVING)

class ComponentPurpose(Enum):
    BASE = 'BASE'
    TRIUMPH_MEDAL = 'TRIUMPH_MEDAL'
    TRIUMPH = 'TRIUMPH'
    DEDICATION = 'DEDICATION'
    SKILL = 'SKILL'


SEND_NEW_GRADING_NOTIFICATION = (ComponentPurpose.TRIUMPH, ComponentPurpose.DEDICATION)

class ComponentNumberType(Enum):
    NUMBER = 'NUMBER'
    PERCENTAGE = 'PERCENTAGE'


class DogTagsException(SoftException):

    def __init__(self, err, *args):
        self.err = err
        self.args = args


class ParseException(DogTagsException):
    PREFIX = 'PARSE_ERR_%d: '
    PATH = "Error in section '%s': "
    CAN_NOT_OPEN_XML = 1
    XML_VALIDATION_FAILED = 2
    TAG_DUPLICITY = 3
    PARAM_DUPLICITY = 4
    WRONG_PARAM_VALUE = 5
    STARTING_COMPONENT_DUPLICITY = 6
    STARTING_COMPONENT_INVALID_ID = 7
    ERR_STR = {CAN_NOT_OPEN_XML: PREFIX + "Can not open '%s'. Error: '%s'",
     XML_VALIDATION_FAILED: PREFIX + "Validation failed with error: '%s'",
     TAG_DUPLICITY: PREFIX + 'Programming error: more than one class has tag  %s',
     PARAM_DUPLICITY: PREFIX + 'Programming error: more than one param has name %s',
     WRONG_PARAM_VALUE: PREFIX + PATH + "Wrong parameter value for '%s'",
     STARTING_COMPONENT_DUPLICITY: PREFIX + 'Starting components have same ID.',
     STARTING_COMPONENT_INVALID_ID: PREFIX + 'Component with id=%s does not exist.'}

    def __str__(self):
        return ParseException.ERR_STR[self.err] % ((self.err,) + self.args)


class ValidateException(DogTagsException):
    PREFIX = 'VALIDATE_ERR_%d: '
    HAS_GRADES = 1
    HAS_UNLOCK_KEY = 2
    WRONG_NUMBER_OF_GRADES = 3
    DEFAULT_WRONG_GRADES = 4
    WRONG_TYPE_VIEW_COMBINATION = 5
    STARTING_COMPONENT_INVALID_TYPE = 7
    STARTING_COMPONENT_WRONG_DATA = 9
    STARTING_COMPONENT_NON_DEFAULT = 10
    SHOULD_BE_DEFAULT_OR_HAS_UNLOCK_KEY = 11
    DEFAULT_HIDDEN = 12
    ERR_STR = {HAS_GRADES: PREFIX + 'Component with id = %s cannot have grades. Grades: %s',
     HAS_UNLOCK_KEY: PREFIX + 'Component with id = %s cannot have unlockKey. UnlockKey: %s',
     WRONG_NUMBER_OF_GRADES: PREFIX + 'Component with id = %s has wrong number of grades. It should have %s grades.',
     DEFAULT_WRONG_GRADES: PREFIX + 'Component with id = %s is default but grades are not correct. Grades: %s',
     WRONG_TYPE_VIEW_COMBINATION: PREFIX + 'Component with id = %s is type %s it cannot be viewType %s.',
     STARTING_COMPONENT_INVALID_TYPE: PREFIX + 'Starting components cannot be %s view type.',
     STARTING_COMPONENT_WRONG_DATA: PREFIX + 'Starting components should contain only types: %s but contains: %s',
     STARTING_COMPONENT_NON_DEFAULT: PREFIX + 'Starting component with id=%s is not default.',
     SHOULD_BE_DEFAULT_OR_HAS_UNLOCK_KEY: PREFIX + 'Component with id = %s should be default or has unlock key',
     DEFAULT_HIDDEN: PREFIX + 'Component with id=%s is default AND hidden. This is forbidden.'}

    def __str__(self):
        return ValidateException.ERR_STR[self.err] % ((self.err,) + self.args)


class ParameterType(Enum):
    INT = 0
    BOOL = 1
    STR = 2
    INT_LIST = 3
    STR_LIST = 4
    VIEW_TYPE = 5
    TYPE = 6
    NUMBER_TYPE = 7
    FLOAT_LIST = 8


class Visibility(Enum):
    SERVER = 0
    CLIENT = 1
    ALL = 2


class BotDogTagStrategy(Enum):
    DEFAULT = 1
    RANDOM = 2


DEFAULT_BOT_STRATEGY = BotDogTagStrategy.DEFAULT
DEFAULT_BOT_STRATEGY_DEVELOP = BotDogTagStrategy.RANDOM
MAX_GRADE = 9
