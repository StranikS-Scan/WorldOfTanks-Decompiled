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
    RANK_UP = 'rank_up'
    PRESTIGE_POINTS = 'prestige_points'


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

    def __repr__(self):
        return self.__class__.__name__


class RegularDescription(IClientDescription):
    __slots__ = ('iconID', 'limiterID', 'isInOrGroup', 'priority')

    def __init__(self, iconID, limiterID=None, isInOrGroup=False, priority=0):
        self.iconID = iconID
        self.limiterID = limiterID
        self.isInOrGroup = isInOrGroup
        self.priority = priority

    @classmethod
    def getContainerType(cls):
        return CONTAINER.BODY

    def __repr__(self):
        return self.__class__.__name__ + ': ' + str(self.iconID) + ' ' + str(self.limiterID) + ' ' + str(self.isInOrGroup) + ' ' + str(self.priority)


class AverageDescription(RegularDescription):
    __slots__ = RegularDescription.__slots__ + ('counterID',)

    def __init__(self, iconID, counterID, limiterID=None, isInOrGroup=False, priority=0):
        super(AverageDescription, self).__init__(iconID, limiterID, isInOrGroup, priority)
        self.counterID = counterID

    def __repr__(self):
        return self.__class__.__name__ + ': ' + str(self.iconID) + ' ' + str(self.counterID) + ' ' + str(self.limiterID) + ' ' + str(self.isInOrGroup)


class HeaderDescription(IClientDescription):
    __slots__ = ('displayType', 'isInOrGroup')

    def __init__(self, displayType):
        self.displayType = displayType
        self.isInOrGroup = False

    @classmethod
    def getContainerType(cls):
        return CONTAINER.HEADER

    def __repr__(self):
        return self.__class__.__name__ + ': ' + str(self.displayType) + ' ' + str(self.isInOrGroup)


class DESCRIPTIONS(object):
    REGULAR = RegularDescription
    AVERAGE = AverageDescription
    HEADER = HeaderDescription


class PROCESSOR_PARAMETERS:
    ATTACK_REASONS = 'attackReasons'
    UNIQUE_TARGET = 'uniqueTarget'
    UNIQUE_ATTACKER = 'uniqueAttacker'
    TARGET_NATIONS = 'targetNations'
    TARGET_ALLIANCE = 'targetAlliance'
    TARGET_CLASSES = 'targetClasses'
    TARGET_IMMOBILIZED = 'targetImmobilized'
    TARGET_LEVEL_GREATER_OR_EQUAL = 'targetLevelGreaterOrEqual'
    TARGET_LEVEL_DIFF = 'targetLevelDiff'
    STUN_SEVERAL_TARGETS = 'stunSeveralTargets'
    DISTANCE_GREATER_OR_EQUAL = 'distanceGreatOrEqual'
    DISTANCE_SHORTER_OR_EQUAL = 'distanceShortOrEqual'
    ATTACKER_UNHARMED = 'attackerUnharmed'
    DISTANCE_IN_VISION_RADIUS = 'distanceInVisionRadius'
    ATTACKER_STAY_ALIVE = 'attackerStayAlive'
    ATTACKER_WAS_INVISIBLE = 'attackerWasInvisible'
    ATTACKER_DEALT_MORE_DAMAGE = 'attackerDealtMoreDamage'
    DIRECT_HITS_RECEIVED = 'directHitsReceived'
    ATTACKER_CLASSES = 'attackerClasses'
    ATTACKER_MOVING_SPEED_GREATER_OR_EQUAL = 'attackerMovingSpeedGreaterOrEqual'
    TARGET_IS_STATIONARY = 'targetIsStationary'
    DAMAGE_DEALT = 'damageDealt'
    TARGET_IS_NOT_SPOTTED = 'targetIsNotSpotted'
    DESIRED_POSITION = 'desiredPosition'
    MEDAL = 'medal'
    VEHICLE_HEALTH_FACTOR = 'vehicleHealthFactor'
    ASSIST_TYPES = 'assistTypes'
    SHOULD_BE_UNSPOTTED = 'shouldBeUnspotted'
    SHOULD_BE_INVISIBLE = 'shouldBeInvisible'
    MARK_OF_MASTERY = 'markOfMastery'
    CRIT_TYPES = 'critTypes'
    HITS = 'hits'


class CONFIG_KEYS:
    PARAMS = 'params'
    UNIQUE_VEHICLE = 'uniqueVehicle'
    GOAL = 'goal'
    IS_MAIN = 'isMain'
    IS_AWARD = 'isAward'
    VISIBLE_SCOPE = 'visibleScope'
    BATTLES_UNIQUE_VEHICLES = 'battlesUniqueVehicles'
    UNIQUE_BATTLES_COUNT = 'uniqueBattlesCount'


VEHICLE_RESTRICTION_MIN_LEVEL = 1
VEHICLE_RESTRICTION_MAX_LEVEL = 11
