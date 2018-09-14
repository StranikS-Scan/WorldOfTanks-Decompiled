# Embedded file name: scripts/common/constants.py
try:
    import BigWorld
    if BigWorld.component in ('web', 'Unknown'):
        raise Exception
except:
    IS_CLIENT = False
    IS_CELLAPP = False
    IS_BASEAPP = False
    IS_WEB = True
    IS_BOT = False
else:
    IS_CLIENT = BigWorld.component == 'client'
    IS_BOT = BigWorld.component == 'bot'
    IS_CELLAPP = BigWorld.component == 'cell'
    IS_BASEAPP = BigWorld.component in ('base', 'service')
    IS_WEB = False

DEFAULT_LANGUAGE = 'ru'
IS_DEVELOPMENT = False
IS_CHINA = False
IS_VIETNAM = False
IS_KOREA = False
IS_SINGAPORE = False
SPECIAL_OL_FILTER = IS_KOREA or IS_SINGAPORE
IS_RENTALS_ENABLED = False
AUTH_REALM = 'RU'
if not sum([IS_CHINA,
 IS_VIETNAM,
 IS_KOREA,
 IS_SINGAPORE]) <= 1:
    raise AssertionError
    IS_SHOW_SERVER_STATS = not (IS_CHINA or IS_VIETNAM)
    IS_VN_AOGAS = IS_VIETNAM
    IS_CAT_LOADED = False
    IS_TUTORIAL_ENABLED = True
    IS_IGR_ENABLED = IS_KOREA or IS_CHINA
    SERVER_TICK_LENGTH = 0.1
    SHELL_TRAJECTORY_EPSILON_CLIENT = 0.03
    SHELL_TRAJECTORY_EPSILON_SERVER = 0.1
    ARENA_TYPE_XML_PATH = 'scripts/arena_defs/'
    ITEM_DEFS_PATH = 'scripts/item_defs/'
    SPACE_DATA_ITEMS_VISIBILITY_MASK = 300
    VOICE_CHAT_INIT_TIMEOUT = 10
    DEFAULT_GUN_PITCH_LIMITS_TRANSITION = 0.4
    MAX_OPENED_ANOTHER_DOSSIERS = 4

    class SPT_MATKIND:
        SOLID = 71
        LEAVES = 72


    class DESTRUCTIBLE_MATKIND:
        MIN = 71
        MAX = 100
        NORMAL_MIN = 73
        NORMAL_MAX = 86
        DAMAGED_MIN = 87
        DAMAGED_MAX = 100


    class DOSSIER_TYPE:
        ACCOUNT = 1
        VEHICLE = 2
        TANKMAN = 4
        FORTIFIED_REGIONS = 8


    ARENA_GAMEPLAY_NAMES = ('ctf', 'domination', 'assault', 'nations', 'ctf2', 'domination2', 'assault2')
    ARENA_GAMEPLAY_IDS = dict(((value, index) for index, value in enumerate(ARENA_GAMEPLAY_NAMES)))

    class ARENA_GUI_TYPE:
        UNKNOWN = 0
        RANDOM = 1
        TRAINING = 2
        COMPANY = 3
        TUTORIAL = 4
        CYBERSPORT = 5
        HISTORICAL = 6
        EVENT_BATTLES = 7
        SORTIE = 8
        FORT_BATTLE = 9
        RANGE = (UNKNOWN,
         RANDOM,
         TRAINING,
         COMPANY,
         TUTORIAL,
         CYBERSPORT,
         HISTORICAL,
         EVENT_BATTLES,
         SORTIE,
         FORT_BATTLE)


    class ARENA_GUI_TYPE_LABEL:
        LABELS = {ARENA_GUI_TYPE.UNKNOWN: 'random',
         ARENA_GUI_TYPE.RANDOM: 'random',
         ARENA_GUI_TYPE.TRAINING: 'training',
         ARENA_GUI_TYPE.COMPANY: 'team',
         ARENA_GUI_TYPE.TUTORIAL: 'tutorial',
         ARENA_GUI_TYPE.CYBERSPORT: 'team7x7',
         ARENA_GUI_TYPE.HISTORICAL: 'historical',
         ARENA_GUI_TYPE.EVENT_BATTLES: 'random',
         ARENA_GUI_TYPE.SORTIE: 'fortifications',
         ARENA_GUI_TYPE.FORT_BATTLE: 'fortifications'}


    class ARENA_BONUS_TYPE:
        UNKNOWN = 0
        REGULAR = 1
        TRAINING = 2
        COMPANY = 3
        TOURNAMENT = 4
        CLAN = 5
        TUTORIAL = 6
        CYBERSPORT = 7
        HISTORICAL = 8
        EVENT_BATTLES = 9
        SORTIE = 10
        FORT_BATTLE = 11
        RANGE = (UNKNOWN,
         REGULAR,
         TRAINING,
         COMPANY,
         TOURNAMENT,
         CLAN,
         TUTORIAL,
         CYBERSPORT,
         HISTORICAL,
         EVENT_BATTLES,
         SORTIE,
         FORT_BATTLE)


    class ARENA_BONUS_MASK:
        TYPE_BITS = dict(((name, 2 ** id) for id, name in enumerate(ARENA_BONUS_TYPE.RANGE[1:])))
        ANY = 2147483647

        @staticmethod
        def mask(*args):
            return reduce(lambda v, x: v | x, [ ARENA_BONUS_MASK.TYPE_BITS[arg] for arg in args ])

        @staticmethod
        def exclude(*args):
            return reduce(lambda v, x: v & ~x, [ ARENA_BONUS_MASK.TYPE_BITS[arg] for arg in args ], ARENA_BONUS_MASK.ANY)


    class ARENA_BONUS_TYPE_CAPS:
        RESULTS = 1
        DAMAGE_VEHICLE = 2
        CREDITS = 4
        XP = 8
        RANSOM = 16
        REWARD_FOR_ACHIEVEMENT = 32
        QUESTS = 64
        DOSSIER_TOTAL = 128
        DOSSIER_KILL_LIST = 256
        DOSSIER_15X15 = 512
        DOSSIER_7X7 = 1024
        DOSSIER_COMPANY = 2048
        DOSSIER_CLAN = 4096
        DOSSIER_HISTORICAL = 8192
        DOSSIER_ACHIEVEMENTS_15X15 = 16384
        DOSSIER_ACHIEVEMENTS_7X7 = 32768
        DOSSIER_ACHIEVEMENTS_HISTORICAL = 65536
        DOSSIER_MAX15X15 = 131072
        DOSSIER_MAX7X7 = 262144
        DOSSIER_MAXHISTORICAL = 524288
        CYBERSPORT_RATING = 1048576
        XP_FACTOR_15X15 = 2097152
        XP_FACTOR_7X7 = 4194304
        CREDITS_FACTOR_15X15 = 8388608
        CREDITS_FACTOR_7X7 = 16777216
        TKILL_RATING = 33554432
        DOSSIER_SORTIE = 67108864
        DOSSIER_MAXSORTIE = 134217728
        DOSSIER_ACHIEVEMENTS_SORTIE = 268435456
        FORT_RESOURCE = 536870912
        FORT_QUESTS = 1073741824
        FORT_BATTLE_RESULTS = 2147483648L
        DOSSIER_FORT_BATTLE = 4294967296L
        DOSSIER_MAXFORTBATTLE = 8589934592L
        REF_SYSTEM_BONUS = 17179869184L
        REGULAR = RESULTS | DAMAGE_VEHICLE | CREDITS | CREDITS_FACTOR_15X15 | XP | XP_FACTOR_15X15 | REWARD_FOR_ACHIEVEMENT | QUESTS | DOSSIER_TOTAL | DOSSIER_KILL_LIST | DOSSIER_15X15 | DOSSIER_ACHIEVEMENTS_15X15 | DOSSIER_MAX15X15 | TKILL_RATING | REF_SYSTEM_BONUS
        TRAINING = RESULTS
        COMPANY = RESULTS | DAMAGE_VEHICLE | CREDITS | CREDITS_FACTOR_15X15 | XP | XP_FACTOR_15X15 | RANSOM | QUESTS | DOSSIER_TOTAL | DOSSIER_KILL_LIST | DOSSIER_15X15 | DOSSIER_COMPANY | DOSSIER_MAX15X15
        TOURNAMENT = RESULTS
        CLAN = RESULTS | DAMAGE_VEHICLE | CREDITS | CREDITS_FACTOR_15X15 | XP | XP_FACTOR_15X15 | RANSOM | QUESTS | DOSSIER_TOTAL | DOSSIER_KILL_LIST | DOSSIER_15X15 | DOSSIER_CLAN
        TUTORIAL = 0
        CYBERSPORT = RESULTS | DAMAGE_VEHICLE | CREDITS | CREDITS_FACTOR_7X7 | XP | XP_FACTOR_7X7 | RANSOM | QUESTS | DOSSIER_TOTAL | DOSSIER_KILL_LIST | DOSSIER_7X7 | DOSSIER_MAX7X7 | CYBERSPORT_RATING | DOSSIER_ACHIEVEMENTS_7X7
        HISTORICAL = RESULTS | DAMAGE_VEHICLE | CREDITS | CREDITS_FACTOR_15X15 | XP | XP_FACTOR_15X15 | QUESTS | DOSSIER_KILL_LIST | DOSSIER_HISTORICAL | DOSSIER_ACHIEVEMENTS_HISTORICAL | DOSSIER_MAXHISTORICAL | TKILL_RATING
        EVENT_BATTLES = RESULTS | DAMAGE_VEHICLE | QUESTS | TKILL_RATING
        SORTIE = RESULTS | DAMAGE_VEHICLE | CREDITS | XP | RANSOM | DOSSIER_TOTAL | DOSSIER_KILL_LIST | DOSSIER_SORTIE | DOSSIER_MAXSORTIE | DOSSIER_ACHIEVEMENTS_SORTIE | FORT_RESOURCE | QUESTS
        FORT_BATTLE = RESULTS | DAMAGE_VEHICLE | CREDITS | XP | RANSOM | DOSSIER_TOTAL | DOSSIER_KILL_LIST | FORT_BATTLE_RESULTS | DOSSIER_FORT_BATTLE | DOSSIER_MAXFORTBATTLE | QUESTS
        DOSSIER_ACHIEVEMENTS = DOSSIER_ACHIEVEMENTS_7X7 | DOSSIER_ACHIEVEMENTS_15X15 | DOSSIER_ACHIEVEMENTS_SORTIE | DOSSIER_ACHIEVEMENTS_HISTORICAL
        __typeToCaps = {ARENA_BONUS_TYPE.REGULAR: REGULAR,
         ARENA_BONUS_TYPE.TRAINING: TRAINING,
         ARENA_BONUS_TYPE.COMPANY: COMPANY,
         ARENA_BONUS_TYPE.TOURNAMENT: TOURNAMENT,
         ARENA_BONUS_TYPE.CLAN: CLAN,
         ARENA_BONUS_TYPE.TUTORIAL: TUTORIAL,
         ARENA_BONUS_TYPE.CYBERSPORT: CYBERSPORT,
         ARENA_BONUS_TYPE.HISTORICAL: HISTORICAL,
         ARENA_BONUS_TYPE.EVENT_BATTLES: EVENT_BATTLES,
         ARENA_BONUS_TYPE.SORTIE: SORTIE,
         ARENA_BONUS_TYPE.FORT_BATTLE: FORT_BATTLE}

        @staticmethod
        def get(arenaBonusType):
            return ARENA_BONUS_TYPE_CAPS.__typeToCaps.get(arenaBonusType, 0)


    class ARENA_PERIOD:
        IDLE = 0
        WAITING = 1
        PREBATTLE = 2
        BATTLE = 3
        AFTERBATTLE = 4


    class ARENA_UPDATE:
        VEHICLE_LIST = 1
        VEHICLE_ADDED = 2
        PERIOD = 3
        STATISTICS = 4
        VEHICLE_STATISTICS = 5
        VEHICLE_KILLED = 6
        AVATAR_READY = 7
        BASE_POINTS = 8
        BASE_CAPTURED = 9
        TEAM_KILLER = 10
        VEHICLE_UPDATED = 11


    class JOIN_FAILURE:
        TIME_OUT = 1
        NOT_FOUND = 2
        ACCOUNT_LOCK = 3
        WRONG_VEHICLE = 4
        TEAM_IS_FULL = 5
        WRONG_ARGS = 6
        CAPTCHA = 7
        WRONG_ARENA_STATE = 8
        CANNOT_CREATE = 9
        PRIVACY = 10
        WRONG_ACCOUNT_TYPE = 11
        COOLDOWN = 12
        WRONG_BATTLE_ID = 13
        WRONG_VEHICLE_TYPE = 14
        WRONG_GAME_PARAMS = 15


    JOIN_FAILURE_NAMES = dict([ (v, k) for k, v in JOIN_FAILURE.__dict__.iteritems() if not k.startswith('_') ])

    class KICK_REASON:
        ARENA_CREATION_FAILURE = 1
        AVATAR_CREATION_FAILURE = 2
        VEHICLE_CREATION_FAILURE = 3
        PREBATTLE_CREATION_FAILURE = 4
        BASEAPP_CRASH = 5
        CELLAPP_CRASH = 6
        UNKNOWN_FAILURE = 7
        FINISHED = 8
        CREATOR_LEFT = 9
        PLAYERKICK = 10
        TIMEOUT = 11


    KICK_REASON_NAMES = dict([ (v, k) for k, v in KICK_REASON.__dict__.iteritems() if not k.startswith('_') ])

    class FINISH_REASON:
        UNKNOWN = 0
        EXTERMINATION = 1
        BASE = 2
        TIMEOUT = 3
        FAILURE = 4
        TECHNICAL = 5


    class PREBATTLE_TYPE:
        NONE = 0
        SQUAD = 1
        TRAINING = 2
        COMPANY = 3
        TOURNAMENT = 4
        CLAN = 5
        UNIT = 6
        SORTIE = 7
        FORT_BATTLE = 8
        RANGE = (SQUAD,
         TRAINING,
         COMPANY,
         TOURNAMENT,
         CLAN,
         UNIT,
         SORTIE,
         FORT_BATTLE)


    PREBATTLE_TYPE_NAMES = dict([ (v, k) for k, v in PREBATTLE_TYPE.__dict__.iteritems() if not k.startswith('_') ])

    class PREBATTLE_START_TYPE:
        DIRECT = 1
        SQUAD = 2
        COMPANY = 3
        RANGE = (DIRECT, SQUAD, COMPANY)


    class PREBATTLE_ROLE:
        TEAM_READY_1 = 1
        TEAM_READY_2 = 2
        ASSIGNMENT_1 = 4
        ASSIGNMENT_2 = 8
        ASSIGNMENT_1_2 = 16
        SEE_1 = 32
        SEE_2 = 64
        KICK_1 = 512
        KICK_2 = 1024
        CHANGE_ARENA = 2048
        CHANGE_COMMENT = 4096
        OPEN_CLOSE = 8192
        INVITE = 16384
        CHANGE_ARENA_VOIP = 32768
        CHANGE_DIVISION = 65536
        CHANGE_GAMEPLAYSMASK = 131072
        TRAINING_DEFAULT = SEE_1 | SEE_2
        TRAINING_CREATOR = TRAINING_DEFAULT | TEAM_READY_1 | TEAM_READY_2 | ASSIGNMENT_1 | ASSIGNMENT_2 | ASSIGNMENT_1_2 | KICK_1 | KICK_2 | CHANGE_ARENA | CHANGE_COMMENT | OPEN_CLOSE | INVITE | CHANGE_ARENA_VOIP
        SQUAD_DEFAULT = SEE_1
        SQUAD_CREATOR = SQUAD_DEFAULT | TEAM_READY_1 | KICK_1 | INVITE | CHANGE_GAMEPLAYSMASK
        COMPANY_DEFAULT = SEE_1
        COMPANY_CREATOR = COMPANY_DEFAULT | TEAM_READY_1 | ASSIGNMENT_1 | KICK_1 | CHANGE_COMMENT | OPEN_CLOSE | INVITE | CHANGE_DIVISION


    class PREBATTLE_STATE:
        IDLE = 0
        IN_QUEUE = 1
        IN_BATTLE = 2


    class PREBATTLE_TEAM_STATE:
        NOT_READY = 1
        READY = 2
        LOCKED = 3


    class PREBATTLE_ACCOUNT_STATE:
        UNKNOWN = 0
        NOT_READY = 1
        AFK = 2 | NOT_READY
        READY = 4
        IN_BATTLE = 8
        OFFLINE = 16
        MAIN_STATE_MASK = NOT_READY | AFK | READY | IN_BATTLE


    PREBATTLE_COMMENT_MAX_LENGTH = 400

    class PREBATTLE_UPDATE:
        ROSTER = 1
        PLAYER_ADDED = 2
        PLAYER_REMOVED = 3
        PLAYER_STATE = 4
        PLAYER_ROSTER = 5
        TEAM_STATES = 6
        SETTINGS = 7
        SETTING = 8
        KICKED_FROM_QUEUE = 9
        PROPERTIES = 10
        PROPERTY = 11


    class PREBATTLE_CACHE_KEY:
        TYPE = 1
        IS_OPENED = 2
        STATE = 3
        IS_FULL = 4
        PLAYER_COUNT = 5
        CREATOR = 6
        CREATE_TIME = 7
        START_TIME = 8
        COMMENT = 9
        DESCRIPTION = 10
        ARENA_TYPE_ID = 11
        ROUND_LENGTH = 12
        CREATOR_CLAN_DB_ID = 14
        CREATOR_CLAN_ABBREV = 15
        DIVISION = 16
        CREATOR_IGR_TYPE = 17
        CREATOR_DB_ID = 18


    class PREBATTLE_COMPANY_DIVISION:
        JUNIOR = 1
        MIDDLE = 2
        CHAMPION = 3
        ABSOLUTE = 4
        _CYBER_7x42 = 5
        RANGE = (JUNIOR,
         MIDDLE,
         CHAMPION,
         ABSOLUTE)


    PREBATTLE_COMPANY_DIVISION_NAMES = dict([ (v, k) for k, v in PREBATTLE_COMPANY_DIVISION.__dict__.iteritems() if not k.startswith('_') and k != 'RANGE' ])

    class PREBATTLE_INVITE_STATE:
        ACTIVE = 1
        ACCEPTED = 2
        DECLINED = 3
        EXPIRED = 4


    UNIT_COMMENT_MAX_LENGTH = 400
    UNIT_MAX_SEND_INVITES = 100

    class UNIT_FINDER:
        RESULTSET_SIZE = 20


    class ACCOUNT_TYPE2:
        FIRST_FLAG = 1
        LAST_FLAG = 16384
        ACCOUNT_TYPE_DEFAULT = 16777216

        @staticmethod
        def getPrimaryGroup(type):
            return type >> 24 & 255

        @staticmethod
        def getSecondaryGroup(type):
            return type >> 16 & 255

        @staticmethod
        def getFlags(type):
            return type & 65535

        @staticmethod
        def getAttrs(cache, type):
            attrsDct = cache['primary'].get(ACCOUNT_TYPE2.getPrimaryGroup(type), None)
            raise attrsDct is not None or AssertionError
            attrsPrimaryGroup = attrsDct['attributes']
            attrsDct = cache['secondary'].get(ACCOUNT_TYPE2.getSecondaryGroup(type), None)
            attrsSecondaryGroup = attrsDct and attrsDct['attributes'] or 0
            return attrsPrimaryGroup | attrsSecondaryGroup

        @staticmethod
        def makeAccountType(primary, secondary, flags):
            return (primary & 255) << 24 | (secondary & 255) << 16 | flags & 65535


    class ACCOUNT_ATTR:
        RANDOM_BATTLES = 1
        TRADING = 2
        CLAN = 4
        MERCENARY = 8
        RATING = 16
        USER_INFO = 32
        STATISTICS = 64
        ARENA_CHANGE = 128
        CHAT_ADMIN = 256
        ADMIN = 512
        ROAMING = 1024
        DAILY_MULTIPLIED_XP = 2048
        PAYMENTS = 4096
        OUT_OF_SESSION_WALLET = 8192
        DAILY_BONUS_1 = 2097152
        DAILY_BONUS_2 = 4194304
        ALPHA = 536870912
        CBETA = 1073741824
        OBETA = 2147483648L
        PREMIUM = 4294967296L
        AOGAS = 8589934592L
        TUTORIAL_COMPLETED = 17179869184L
        IGR_BASE = 34359738368L
        IGR_PREMIUM = 68719476736L


    class RESTRICTION_TYPE:
        NONE = 0
        BAN = 1
        CHAT_BAN = 3
        TRADING = 4
        CLAN = 5
        RANGE = (BAN,
         CHAT_BAN,
         TRADING,
         CLAN)


    class RESTRICTION_SOURCE:
        UNKNOWN = 0
        SERVER = 1
        CLIENT = 2
        BACKYARD = 3
        MIGRATOR = 4


    SPA_RESTR_NAME_TO_RESTR_TYPE = {'game': RESTRICTION_TYPE.BAN,
     'chat': RESTRICTION_TYPE.CHAT_BAN,
     'clan': RESTRICTION_TYPE.CLAN,
     'trading': RESTRICTION_TYPE.TRADING}
    RESTR_TYPE_TO_SPA_NAME = dict(((x[1], x[0]) for x in SPA_RESTR_NAME_TO_RESTR_TYPE.iteritems()))

    class CLAN_MEMBER_FLAGS(object):
        LEADER = 1
        VICE_LEADER = 2
        RECRUITER = 4
        TREASURER = 8
        DIPLOMAT = 16
        COMMANDER = 32
        PRIVATE = 64
        RECRUIT = 128
        STAFF = 256
        JUNIOR = 512
        RESERVIST = 1024
        MAY_CHANGE_SETTINGS = LEADER | VICE_LEADER
        MAY_EDIT_RECRUIT_PROFILE = LEADER | VICE_LEADER | STAFF | RECRUITER
        MAY_CHANGE_ROLE = LEADER | VICE_LEADER | STAFF | COMMANDER
        MAY_CHANGE_COMMANDER = LEADER
        MAY_HANDLE_INVITES = LEADER | VICE_LEADER | STAFF | RECRUITER
        MAY_INVITE = LEADER | VICE_LEADER | STAFF | RECRUITER
        MAY_REMOVE_MEMBERS = LEADER | VICE_LEADER | STAFF
        MAY_REMOVE_CLAN = LEADER
        MAY_TRADE = LEADER | VICE_LEADER | TREASURER
        MAY_EXCHANGE_MONEY = LEADER | VICE_LEADER | STAFF | COMMANDER | DIPLOMAT | TREASURER | RECRUITER | JUNIOR | PRIVATE


    class AIMING_MODE:
        SHOOTING = 1
        TARGET_LOCK = 16
        USER_DISABLED = 256


    class SCOUT_EVENT_TYPE:
        SPOTTED = 0
        HIT_ASSIST = 1
        KILL_ASSIST = 2


    SCOUT_EVENTS_PLURALITY_COOLDOWN = 2.0

    class VEHICLE_SETTING:
        CURRENT_SHELLS = 0
        NEXT_SHELLS = 1
        AUTOROTATION_ENABLED = 2
        ACTIVATE_EQUIPMENT = 16
        RELOAD_PARTIAL_CLIP = 17


    class VEHICLE_MISC_STATUS:
        OTHER_VEHICLE_DAMAGED_DEVICES_VISIBLE = 0
        IS_OBSERVED_BY_ENEMY = 1
        LOADER_INTUITION_WAS_USED = 2
        VEHICLE_IS_OVERTURNED = 3
        VEHICLE_DROWN_WARNING = 4
        IN_DEATH_ZONE = 5
        HORN_BANNED = 6
        DESTROYED_DEVICE_IS_REPAIRING = 7


    class DEVELOPMENT_INFO:
        ATTACK_RESULT = 1
        FIRE_RESULT = 2
        BONUSES = 3
        VISIBILITY = 4
        VEHICLE_ATTRS = 5
        ENABLE_SENDING_VEH_ATTRS_TO_CLIENT = False


    class AMMOBAY_DESTRUCTION_MODE:
        POWDER_BURN_OFF = 0
        POWDER_EXPLOSION = 1
        HE_DETONATION = 2


    class SPECIAL_VEHICLE_HEALTH:
        AMMO_BAY_DESTROYED = -1
        TURRET_DETACHED = -2
        FULL_DISASSEMBLY = -3
        FUEL_EXPLODED = -4
        DESTR_BY_FALL_RAMMING = -5
        AMMO_BAY_EXPLOSION = (AMMO_BAY_DESTROYED, TURRET_DETACHED, FULL_DISASSEMBLY)


    ATTACK_REASONS = ('shot', 'fire', 'ramming', 'world_collision', 'death_zone', 'drowning')
    ATTACK_REASON_INDICES = dict(((value, index) for index, value in enumerate(ATTACK_REASONS)))

    class VEHICLE_HIT_EFFECT:
        INTERMEDIATE_RICOCHET = 0
        FINAL_RICOCHET = 1
        ARMOR_NOT_PIERCED = 2
        ARMOR_PIERCED_NO_DAMAGE = 3
        ARMOR_PIERCED = 4
        CRITICAL_HIT = 5
        MAX_CODE = CRITICAL_HIT
        RICOCHETS = (INTERMEDIATE_RICOCHET, FINAL_RICOCHET)


    class VEHICLE_HIT_FLAGS:
        VEHICLE_KILLED = 1
        VEHICLE_WAS_DEAD_BEFORE_ATTACK = 2
        FIRE_STARTED = 4
        RICOCHET = 8
        MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_PROJECTILE = 16
        MATERIAL_WITH_POSITIVE_DF_NOT_PIERCED_BY_PROJECTILE = 32
        ARMOR_WITH_ZERO_DF_PIERCED_BY_PROJECTILE = 64
        ARMOR_WITH_ZERO_DF_NOT_PIERCED_BY_PROJECTILE = 128
        DEVICE_PIERCED_BY_PROJECTILE = 256
        DEVICE_NOT_PIERCED_BY_PROJECTILE = 512
        CHASSIS_DAMAGED_BY_PROJECTILE = 1024
        GUN_DAMAGED_BY_PROJECTILE = 2048
        MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_EXPLOSION = 4096
        ARMOR_WITH_ZERO_DF_PIERCED_BY_EXPLOSION = 8192
        DEVICE_PIERCED_BY_EXPLOSION = 16384
        CHASSIS_DAMAGED_BY_EXPLOSION = 32768
        GUN_DAMAGED_BY_EXPLOSION = 65536
        DEVICE_DAMAGED_BY_RAMMING = 131072
        CHASSIS_DAMAGED_BY_RAMMING = 262144
        ATTACK_IS_DIRECT_PROJECTILE = 524288
        ATTACK_IS_EXTERNAL_EXPLOSION = 1048576
        IS_ANY_DAMAGE_MASK = MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_PROJECTILE | MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_EXPLOSION | DEVICE_PIERCED_BY_PROJECTILE | DEVICE_PIERCED_BY_EXPLOSION
        IS_ANY_PIERCING_MASK = IS_ANY_DAMAGE_MASK | ARMOR_WITH_ZERO_DF_PIERCED_BY_PROJECTILE | ARMOR_WITH_ZERO_DF_PIERCED_BY_EXPLOSION


    DAMAGE_INFO_CODES = ('DEVICE_CRITICAL', 'DEVICE_DESTROYED', 'TANKMAN_HIT', 'FIRE', 'DEVICE_CRITICAL_AT_SHOT', 'DEVICE_DESTROYED_AT_SHOT', 'DEVICE_CRITICAL_AT_RAMMING', 'DEVICE_DESTROYED_AT_RAMMING', 'DEVICE_STARTED_FIRE_AT_SHOT', 'DEVICE_STARTED_FIRE_AT_RAMMING', 'TANKMAN_HIT_AT_SHOT', 'DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT', 'DEVICE_CRITICAL_AT_FIRE', 'DEVICE_DESTROYED_AT_FIRE', 'DEVICE_CRITICAL_AT_WORLD_COLLISION', 'DEVICE_DESTROYED_AT_WORLD_COLLISION', 'DEVICE_CRITICAL_AT_DROWNING', 'DEVICE_DESTROYED_AT_DROWNING', 'DEVICE_REPAIRED_TO_CRITICAL', 'DEVICE_REPAIRED', 'TANKMAN_HIT_AT_WORLD_COLLISION', 'TANKMAN_HIT_AT_DROWNING', 'TANKMAN_RESTORED', 'DEATH_FROM_DEVICE_EXPLOSION_AT_FIRE', 'ENGINE_CRITICAL_AT_UNLIMITED_RPM', 'ENGINE_DESTROYED_AT_UNLIMITED_RPM', 'DEATH_FROM_SHOT', 'DEATH_FROM_INACTIVE_CREW_AT_SHOT', 'DEATH_FROM_RAMMING', 'DEATH_FROM_FIRE', 'DEATH_FROM_INACTIVE_CREW', 'DEATH_FROM_DROWNING', 'DEATH_FROM_WORLD_COLLISION', 'DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION', 'DEATH_FROM_DEATH_ZONE', 'FIRE_STOPPED')

    class IGR_TYPE:
        NONE = 0
        BASE = 1
        PREMIUM = 2
        RANGE = (BASE, PREMIUM)


    class EVENT_TYPE:
        ACTION = 1
        BATTLE_QUEST = 2
        TOKEN_QUEST = 3
        HISTORICAL_BATTLES = 4
        FORT_QUEST = 5
        PERSONAL_QUEST = 6
        REF_SYSTEM_QUEST = 7
        POTAPOV_QUEST = 8
        NAME_TO_TYPE = {'battleQuest': BATTLE_QUEST,
         'tokenQuest': TOKEN_QUEST,
         'fortQuest': FORT_QUEST,
         'personalQuest': PERSONAL_QUEST,
         'refSystemQuest': REF_SYSTEM_QUEST,
         'potapovQuest': POTAPOV_QUEST}
        TYPE_TO_NAME = dict(zip(NAME_TO_TYPE.values(), NAME_TO_TYPE.keys()))
        QUEST_RANGE = (BATTLE_QUEST,
         TOKEN_QUEST,
         FORT_QUEST,
         PERSONAL_QUEST,
         REF_SYSTEM_QUEST,
         POTAPOV_QUEST)
        LIKE_BATTLE_QUESTS = (BATTLE_QUEST,
         FORT_QUEST,
         PERSONAL_QUEST,
         POTAPOV_QUEST)
        LIKE_TOKEN_QUESTS = (TOKEN_QUEST, REF_SYSTEM_QUEST)
        ONE_BONUS_QUEST = (TOKEN_QUEST, REF_SYSTEM_QUEST, POTAPOV_QUEST)
        QUEST_WITH_DYNAMIC_CLIENT_DATA = (FORT_QUEST, PERSONAL_QUEST)


    DAMAGE_INFO_INDICES = dict(((x[1], x[0]) for x in enumerate(DAMAGE_INFO_CODES)))
    CLIENT_INACTIVITY_TIMEOUT = 40

    class CHAT_LOG:
        NONE = 0
        MESSAGES = 1
        ACTIONS = 2


    CHAT_MESSAGE_MAX_LENGTH = 1024
    CHAT_MESSAGE_MAX_LENGTH_IN_BATTLE = 140

    class JD_CUTOUT:
        OFF = 0
        ON = 1


    VEHICLE_CLASSES = ('lightTank', 'mediumTank', 'heavyTank', 'SPG', 'AT-SPG')
    VEHICLE_CLASS_INDICES = dict(((x[1], x[0]) for x in enumerate(VEHICLE_CLASSES)))
    MAX_VEHICLE_LEVEL = 10

    class QUEUE_TYPE:
        RANDOMS = 1
        COMPANIES = 2
        VOLUNTEERS = 3
        SANDBOX = 4
        UNITS = 5
        HISTORICAL = 6
        EVENT_BATTLES = 7
        UNIT_ASSEMBLER = 8
        TUTORIAL = 9
        SORTIE = 10
        FORT_BATTLE = 11
        ALL = (RANDOMS,
         COMPANIES,
         VOLUNTEERS,
         SANDBOX,
         UNITS,
         HISTORICAL,
         EVENT_BATTLES,
         UNIT_ASSEMBLER,
         TUTORIAL,
         SORTIE)


    QUEUE_TYPE_NAMES = dict([ (v, k) for k, v in QUEUE_TYPE.__dict__.iteritems() if not k.startswith('_') ])
    USER_ACTIVE_CHANNELS_LIMIT = 100

    class INVOICE_EMITTER:
        PAYMENT_SYSTEM = 1
        BACKYARD = 2
        COMMUNITY = 3
        PORTAL = 4
        DEVELOPMENT = 5
        CN_GIFT = 6
        CN_BUY = 7
        EBANK_WORKER = 8
        ACTION_APPLIER = 9
        WG = 10
        WGCW = 11
        NEGATIVE = (BACKYARD,
         COMMUNITY,
         PORTAL,
         DEVELOPMENT,
         CN_GIFT,
         CN_BUY,
         WG,
         WGCW)
        RANGE = (PAYMENT_SYSTEM,
         BACKYARD,
         COMMUNITY,
         PORTAL,
         DEVELOPMENT,
         CN_GIFT,
         CN_BUY,
         EBANK_WORKER,
         ACTION_APPLIER,
         WG,
         WGCW)


    class INVOICE_ASSET:
        GOLD = 1
        CREDITS = 2
        PREMIUM = 3
        DATA = 4
        FREE_XP = 5


    CHANNEL_SEARCH_RESULTS_LIMIT = 50
    USER_SEARCH_RESULTS_LIMIT = 50

    class USER_SEARCH_MODE:
        ALL = 0
        ONLINE = 1
        OFFLINE = 2


    class AOGAS_TIME:
        REDUCED_GAIN = 10200
        NO_GAIN = 17400
        RESET = 18000


    USE_SERVER_BAD_WORDS_FILTER = IS_CHINA or IS_VIETNAM

    class SERVER_BAD_WORDS_FILTER_MODE:
        ACCOUNT = 1
        CHANNEL = 2


    CURRENT_SERVER_BAD_WORDS_FILTER_MODE = SERVER_BAD_WORDS_FILTER_MODE.CHANNEL

    class CREDENTIALS_RESTRICTION:
        BASIC = 0
        CHINESE = 1
        VIETNAM = 2


    CREDENTIALS_RESTRICTION_SET = (IS_CHINA or IS_KOREA) and CREDENTIALS_RESTRICTION.CHINESE
elif IS_VIETNAM:
    CREDENTIALS_RESTRICTION_SET = CREDENTIALS_RESTRICTION.VIETNAM
else:
    CREDENTIALS_RESTRICTION_SET = CREDENTIALS_RESTRICTION.BASIC

class AUTO_MAINTENANCE_TYPE:
    REPAIR = 1
    LOAD_AMMO = 2
    EQUIP = 3


class AUTO_MAINTENANCE_RESULT:
    OK = 0
    NOT_ENOUGH_ASSETS = 1
    NOT_PERFORMED = 2
    DISABLED_OPTION = 3
    NO_WALLET_SESSION = 4


class REQUEST_COOLDOWN:
    PLAYER_DOSSIER = 1.0
    PLAYER_CLAN_INFO = 1.0
    PLAYER_GLOBAL_RATING = 1.0
    PREBATTLE_CREATION = 4.0
    PREBATTLE_NOT_READY = 2.0
    PREBATTLE_TEAM_NOT_READY = 1.0
    PREBATTLE_JOIN = 1.0
    PREBATTLE_INVITES = 8.0
    STEAM_INIT_TXN = 1.0
    STEAM_FINALIZE_TXN = 1.0
    EBANK_GET_BALANCE = 2.0
    EBANK_BUY_GOLD = 2.0
    REQUEST_CHAT_TOKEN = 10.0
    REQUEST_WEB_TOKEN = 10.0
    REQUEST_TOKEN = 10.0
    UNIT_CHANGE_STATE = 4.0
    UNIT_SET_READY = 4.0
    UNIT_BROWSER_REFRESH = 4.0
    CALL_FORT_METHOD = 0.5
    GET_FORT_SORTIE_DATA = 1.0
    ADD_DEL_BUILDING = 3.0
    FORT_KEEPALIVE = 60.0
    CLIENT_LOG_UX_DATA_COOLDOWN = 2.0
    REQUEST_FORT_PUBLIC_INFO = 10.0
    CLIENT_LOG_XMPP_DATA_COOLDOWN = 10.0


class CAPTCHA_API:
    RE_CAPTCHA = 1
    KONG = 2


CURRENT_CAPTCHA_API = IS_CHINA and CAPTCHA_API.KONG or CAPTCHA_API.RE_CAPTCHA
IS_SHOW_INGAME_HELP_FIRST_TIME = False

class DENUNCIATION:
    OFFEND = 0
    NOT_FAIR_PLAY = 1
    FORBIDDEN_NICK = 2
    BOT = 3
    FLOOD = 4
    SWINDLE = 5
    BLACKMAIL = 6


class VIOLATOR_KIND:
    UNKNOWN = 0
    ENEMY = 1
    ALLY = 2


class GROUND_TYPE:
    NONE = 0
    FIRM = 1
    MEDIUM = 2
    SOFT = 3
    SLOPE = 4
    DEATH_ZONE = 5


class DROWN_WARNING_LEVEL:
    SAFE = 0
    CAUTION = 1
    DANGER = 2


ACCOUNT_MAX_NUM_TRADE_OUT_OFFERS = 20
ACCOUNT_MAX_NUM_TRADE_IN_OFFERS = 20
TREE_TAG = 'tree'
CUSTOM_DESTRUCTIBLE_TAGS = ('monument',)
DESTR_CODES_BY_TAGS = dict(((tag, code) for code, tag in enumerate(CUSTOM_DESTRUCTIBLE_TAGS)))
DESTR_CODES_BY_TAGS[TREE_TAG] = len(CUSTOM_DESTRUCTIBLE_TAGS)
DESTR_TAGS_BY_CODES = dict(((code, tag) for tag, code in DESTR_CODES_BY_TAGS.iteritems()))

class SYS_MESSAGE_CLAN_EVENT:
    LEFT_CLAN = 1


SYS_MESSAGE_CLAN_EVENT_NAMES = dict([ (v, k) for k, v in SYS_MESSAGE_CLAN_EVENT.__dict__.iteritems() if not k.startswith('_') ])

class SYS_MESSAGE_FORT_EVENT:
    FORT_READY = 1
    RESERVE_ACTIVATED = 2
    RESERVE_EXPIRED = 3
    RESERVE_PRODUCED = 4
    STORAGE_OVERFLOW = 5
    ORDER_CANCELED = 6
    REATTACHED_TO_BASE = 7
    DEF_HOUR_ACTIVATED = 8
    OFF_DAY_ACTIVATED = 9
    VACATION_STARTED = 10
    VACATION_FINISHED = 11
    DEF_HOUR_SHUTDOWN = 12
    DEF_HOUR_CHANGED = 13
    PERIPHERY_CHANGED = 14
    BUILDING_DAMAGED = 15
    BASE_DESTROYED = 16
    ORDER_COMPENSATED = 18
    ATTACK_PLANNED = 19
    DEFENCE_PLANNED = 20
    BATTLE_DELETED = 21


SYS_MESSAGE_FORT_EVENT_NAMES = dict([ (v, k) for k, v in SYS_MESSAGE_FORT_EVENT.__dict__.iteritems() if not k.startswith('_') ])
MAX_FORTIFICATION_LEVEL = 10
IS_FORT_TECH_DRAW_PILLAGED = False

class FORT_BUILDING_TYPE:
    MILITARY_BASE = 1
    FINANCIAL_DEPT = 2
    TANKODROME = 3
    TRAINING_DEPT = 4
    MILITARY_ACADEMY = 5
    TRANSPORT_DEPT = 6
    INTENDANT_SERVICE = 7
    TROPHY_BRIGADE = 8
    OFFICE = 9
    MILITARY_SHOP = 10
    _ALL = (MILITARY_BASE,
     FINANCIAL_DEPT,
     TANKODROME,
     TRAINING_DEPT,
     MILITARY_ACADEMY,
     TRANSPORT_DEPT,
     INTENDANT_SERVICE,
     TROPHY_BRIGADE,
     OFFICE,
     MILITARY_SHOP)


FORT_BUILDING_TYPE_NAMES = dict([ (v, k) for k, v in FORT_BUILDING_TYPE.__dict__.iteritems() if not k.startswith('_') ])

class FORT_ORDER_TYPE:
    COMBAT_PAYMENTS = 1
    TACTICAL_TRAINING = 2
    ADDITIONAL_BRIEFING = 3
    MILITARY_EXERCISES = 4
    HEAVY_TRANSPORT = 5
    EVACUATION = 6
    REQUISITION = 7
    SPECIAL_MISSION = 8
    EVACUATION_EXPIRE = 9
    REQUISITION_EXPIRE = 10
    ALL = (COMBAT_PAYMENTS,
     TACTICAL_TRAINING,
     ADDITIONAL_BRIEFING,
     MILITARY_EXERCISES,
     HEAVY_TRANSPORT,
     EVACUATION,
     REQUISITION,
     SPECIAL_MISSION)
    _EXPIRATION_TO_SOURCE = {EVACUATION_EXPIRE: EVACUATION,
     REQUISITION_EXPIRE: REQUISITION}

    @staticmethod
    def isOrderPermanent(orderID):
        if orderID in (FORT_ORDER_TYPE.EVACUATION, FORT_ORDER_TYPE.REQUISITION):
            return True
        return False


FORT_ORDER_TYPE_NAMES = dict([ (v, k) for k, v in FORT_ORDER_TYPE.__dict__.iteritems() if v in FORT_ORDER_TYPE.ALL ])

class USER_SERVER_SETTINGS:
    VERSION = 0
    HIDE_MARKS_ON_GUN = 500


INT_USER_SETTINGS_KEYS = {USER_SERVER_SETTINGS.VERSION: 'Settings version',
 1: 'Game section settings',
 2: 'Graphics section settings',
 3: 'Sound section settings',
 4: 'Controls section settings',
 5: 'Keyboard section settings',
 6: 'Keyboard section settings',
 7: 'Keyboard section settings',
 8: 'Keyboard section settings',
 9: 'Keyboard section settings',
 10: 'Keyboard section settings',
 11: 'Keyboard section settings',
 12: 'Keyboard section settings',
 13: 'Keyboard section settings',
 14: 'Keyboard section settings',
 15: 'Keyboard section settings',
 16: 'Keyboard section settings',
 17: 'Keyboard section settings',
 18: 'Keyboard section settings',
 19: 'Keyboard section settings',
 20: 'Keyboard section settings',
 21: 'Keyboard section settings',
 22: 'Keyboard section settings',
 23: 'Keyboard section settings',
 24: 'Keyboard section settings',
 25: 'Keyboard section settings',
 26: 'Keyboard section settings',
 27: 'Keyboard section settings',
 28: 'Keyboard section settings',
 29: 'Keyboard section settings',
 30: 'Keyboard section settings',
 31: 'Keyboard section settings',
 32: 'Keyboard section settings',
 33: 'Keyboard section settings',
 34: 'Keyboard section settings',
 35: 'Keyboard section settings',
 36: 'Keyboard section settings',
 37: 'Keyboard section settings',
 38: 'Keyboard section settings',
 39: 'Keyboard section settings',
 40: 'Keyboard section settings',
 41: 'Keyboard section settings',
 42: 'Keyboard section settings',
 43: 'Arcade aim setting',
 44: 'Arcade aim setting',
 45: 'Arcade aim setting',
 46: 'Sniper aim setting',
 47: 'Sniper aim setting',
 48: 'Sniper aim setting',
 49: 'Enemy marker setting',
 50: 'Dead marker setting',
 51: 'Ally marker setting',
 52: 'GuiStartBehavior',
 53: 'Carousel filter',
 54: 'EULAVersion',
 55: 'Gameplay settings',
 56: 'Reserved',
 57: 'Reserved',
 58: 'Reserved',
 59: 'Reserved',
 60: 'Reserved',
 USER_SERVER_SETTINGS.HIDE_MARKS_ON_GUN: 'Hide marks on gun'}

class WG_GAMES:
    TANKS = 'wot'
    WARPLANES = 'wowp'
    WARSHIPS = 'wows'
    GENERALS = 'wotg'
    BLITZ = 'wotb'
    WEB = 'web'
    ALL = (TANKS,
     WARPLANES,
     WARSHIPS,
     GENERALS,
     BLITZ,
     WEB)


class TOKEN_TYPE:
    XMPPCS = 1
    WGNI = 2
    WOTG = 3
    WOTB = 4
    SERVICE_NAMES = {XMPPCS: 'xmppcs',
     WGNI: 'wgni',
     WOTG: 'wotg',
     WOTB: 'wotb'}
    COOLDOWNS = {XMPPCS: 'REQUEST_CHAT_TOKEN',
     WGNI: 'REQUEST_WEB_TOKEN',
     WOTG: 'REQUEST_TOKEN',
     WOTB: 'REQUEST_TOKEN'}


class NC_MESSAGE_TYPE:
    INFO = 1
    GOLD = 2
    PREMIUM = 3
    BACKYARD = 4
    POLL = 5
    REFERRAL = 6
    DEFAULT = INFO
    RANGE = (INFO,
     GOLD,
     PREMIUM,
     BACKYARD,
     POLL,
     REFERRAL)


class NC_MESSAGE_PRIORITY:
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    DEFAULT = MEDIUM
    ORDER = (LOW, MEDIUM, HIGH)


class NC_CONTEXT_ITEM_TYPE:
    GOLD = 1
    INTEGRAL = 2
    FRACTIONAL = 3
    NICE_NUMBER = 4
    SHORT_TIME = 5
    LONG_TIME = 6
    SHORT_DATE = 7
    LONG_DATE = 8
    DATETIME = 9
    STRING = 10


class WIN_XP_FACTOR_MODE:
    DAILY = 0
    ALWAYS = 1


OBSERVER_VEH_INVENTORY_ID = -5000

class FORT_SCOUTING_DATA_FILTER:
    DEFAULT = 1
    RECENT = 2
    ELECT = 3
    FILTER = 4
    RANGE = (DEFAULT,
     RECENT,
     ELECT,
     FILTER)


class FORT_SCOUTING_DATA_ERROR:
    DONE = 0
    COOLDOWN = 1
    INVALID_NAME = 2
    DB_ERORR = 3
    NOT_IN_CLAN = 4
    INVALID_PARAMS = 5
    DISCONNECTED_FROM_CENTER = 6


FORT_MAX_ELECTED_CLANS = 60

class PREBATTLE_INVITE_STATUS:
    OK = 0
    WRONG_CLAN = 1
    LEGIONARIES_NOT_ALLOWED = 2


PREBATTLE_INVITE_STATUS_NAMES = dict([ (v, k) for k, v in PREBATTLE_INVITE_STATUS.__dict__.iteritems() if not k.startswith('_') ])
FAIRPLAY_VIOLATIONS_NAMES = ('deserter', 'suicide', 'afk')
FAIRPLAY_VIOLATIONS_MASKS = dict([ (name, 1 << index) for index, name in enumerate(FAIRPLAY_VIOLATIONS_NAMES) ])

class FORT_BATTLE_RESULT:
    WIN = 1
    DRAW = 0
    LOSS = -1


class FORT_COMBAT_RESULT:
    WIN = 1
    DRAW = 0
    LOSS = -1
    TECH_WIN = 10
    TECH_DRAW = -20
    TECH_LOSS = -10

    @staticmethod
    def invert(value):
        if value in (FORT_COMBAT_RESULT.WIN,
         FORT_COMBAT_RESULT.LOSS,
         FORT_COMBAT_RESULT.TECH_WIN,
         FORT_COMBAT_RESULT.TECH_LOSS):
            return -value
        else:
            return value

    @staticmethod
    def invertCombatList(_list):
        return map(lambda combat: (FORT_COMBAT_RESULT.invert(combat[0]),) + combat[1:], _list)


class FORT_BUILDING_STATUS:
    READY_FOR_BATTLE = 0
    LOW_LEVEL = 1
    DESTROYED = 2


FORT_SCHEDULER_DB_PAGE_SIZE = 5000
FORT_SCHEDULER_ROWS_PER_QUERY = 200

class REF_SYSTEM_FLAG:
    REFERRAL_NEW_PLAYER = 1
    REFERRAL_PHOENIX = 2
    CONFIRMED_INVITE = 4
    CONFIRMED_FIRST_BATTLE = 8
    REFERRAL_BOUGHT_10_LVL_VEH = 16
    PREFIX_TO_TYPE = {'invited_by': REFERRAL_NEW_PLAYER,
     'winback_by': REFERRAL_PHOENIX}


class INVALID_CLIENT_STATS:
    OK = 0
    CLIENT_DEATH = 1
    CLIENT_FOCUS_LOST = 2
    CLIENT_STRAIGHT_INTO_BATTLE = 4
    CLIENT_GS_MAJOR_CHANGED = 8
    CLIENT_GS_MINOR_CHANGED = 16
    CLIENT_RESOLUTION_CHANGED = 32
    CLIENT_WM_CHANGED = 64
    CLIENT_DRR_SCALE_CHANGED = 128
