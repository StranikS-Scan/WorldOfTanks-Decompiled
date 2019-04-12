# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/personal_missions_constants.py


class CONDITION_ICON:
    ASSIST = 'assist'
    ASSIST_RADIO = 'assist_radio'
    ASSIST_TRACK = 'assist_track'
    ASSIST_STUN = 'assist_stun'
    ASSIST_STUN_DURATION = 'assist_stun_time'
    ASSIST_STUN_MULTY = 'assist_stun_multy'
    AWARD = 'award'
    BASE_CAPTURE = 'base_capture'
    BASE_DEF = 'base_def'
    BATTLES = 'battles'
    CREDITS = 'credits'
    DAMAGE = 'damage'
    DAMAGE_BLOCK = 'damage_block'
    DISCOVER = 'discover'
    EXPERIENCE = 'experience'
    FIRE = 'fire'
    GET_DAMAGE = 'get_damage'
    GET_HIT = 'get_hit'
    HIT = 'hit'
    HURT_1SHOT = 'hurt_1shot'
    HURT_VEHICLES = 'hurt_vehicles'
    KILL_1SHOT = 'kill_1shot'
    KILL_VEHICLES = 'kill_vehicles'
    MASTER = 'master'
    METERS = 'meters'
    MODULE_CRIT = 'module_crit'
    PREPARATION = 'preparation'
    SAVE_HP = 'save_hp'
    SEC_ALIVE = 'sec_alive'
    SURVIVE = 'survive'
    TIMES_GET_DAMAGE = 'times_get_damage'
    TOP = 'top'
    WIN = 'win'
    FOLDER = 'folder'
    BARREL_MARK = 'barrel_mark'
    RAM = 'ram'
    MAIN_REPEAT = 'main_repeat'
    IMPROVE = 'improve'


class PROGRESS_TEMPLATE:
    BINARY = 'binaryProgress'
    VALUE = 'valueProgress'
    COUNTER = 'counterProgress'
    BIATHLON = 'biathlonProgress'


class MISSION_TYPES:
    KILL = 0
    WIN = 1
    ASSIST = 2
    AUTO = 3
    DAMAGE = 4


class VISIBLE_SCOPE:
    BATTLE = 'battle'
    HANGAR = 'hangar'


class TARGET_NATIONS:
    SAME_ALLIANCE = 'sameAlliance'
    ANOTHER_ALLIANCE = 'anotherAlliance'


class CRIT_TYPES(object):
    INNER_MODULES_AND_TANKMEN = 0
    DESTROYED_TRACKS = 1
    ALL_MODULES = 2
    DESTROYED_INNER_MODULES_AND_TANKMAN = 3


class CONTAINER:
    HEADER = 'header'
    BODY = 'body'


class DISPLAY_TYPE:
    BIATHLON = 'biathlon'
    LIMITED = 'limited'
    SERIES = 'series'
    COUNTER = 'counter'
    SIMPLE = 'simple'
    NONE = 'none'


class MULTIPLIER_TYPE:
    ATTEMPTS = 'attempts'
    PROGRESS = 'progress'


class MULTIPLIER_SCOPE:
    POST_BATTLE = 'postBattle'
    CARD = 'card'


class IClientDescription(object):

    @classmethod
    def getContainerType(cls):
        raise NotImplementedError


class RegularDescription(IClientDescription):
    __slots__ = ('iconID', 'limiterID', 'isInOrGroup')

    def __init__(self, iconID, limiterID=None, isInOrGroup=False):
        self.iconID = iconID
        self.limiterID = limiterID
        self.isInOrGroup = isInOrGroup

    @classmethod
    def getContainerType(cls):
        return CONTAINER.BODY


class AverageDescription(RegularDescription):
    __slots__ = RegularDescription.__slots__ + ('counterID',)

    def __init__(self, iconID, counterID, limiterID=None, isInOrGroup=False):
        super(AverageDescription, self).__init__(iconID, limiterID, isInOrGroup)
        self.counterID = counterID


class HeaderDescription(IClientDescription):
    __slots__ = ('displayType', 'isInOrGroup')

    def __init__(self, displayType):
        self.displayType = displayType
        self.isInOrGroup = False

    @classmethod
    def getContainerType(cls):
        return CONTAINER.HEADER


class DESCRIPTIONS(object):
    REGULAR = RegularDescription
    AVERAGE = AverageDescription
    HEADER = HeaderDescription
