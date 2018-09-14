# Embedded file name: scripts/client/gui/shared/fortifications/settings.py
from gui.shared.utils import CONST_CONTAINER

class CLIENT_FORT_STATE(CONST_CONTAINER):
    UNKNOWN = 0
    ROAMING = 1
    NO_CLAN = 2
    CENTER_UNAVAILABLE = 3
    UNSUBSCRIBED = 4
    NO_FORT = 5
    WIZARD = 6
    HAS_FORT = 7
    NEED_SUBSCRIPTION = (UNSUBSCRIBED,
     NO_FORT,
     WIZARD,
     HAS_FORT)
    KEEP_ALIVE = (WIZARD, HAS_FORT)


class FORT_PROVIDER_INITIAL_FLAGS(CONST_CONTAINER):
    STARTED = 1
    SUBSCRIBED = 2
    READY = STARTED | SUBSCRIBED


class FORT_REQUEST_TYPE(CONST_CONTAINER):
    CREATE_FORT = 1
    DELETE_FORT = 2
    OPEN_DIRECTION = 3
    CLOSE_DIRECTION = 4
    ADD_BUILDING = 5
    DELETE_BUILDING = 6
    TRANSPORTATION = 7
    ADD_ORDER = 8
    ACTIVATE_ORDER = 9
    ATTACH = 10
    UPGRADE = 11
    CREATE_SORTIE = 12
    REQUEST_SORTIE_UNIT = 13
    SUBSCRIBE = 14
    CHANGE_DEF_HOUR = 15
    CHANGE_OFF_DAY = 16
    CHANGE_PERIPHERY = 17
    CHANGE_VACATION = 18
    CHANGE_SETTINGS = 19
    SHUTDOWN_DEF_HOUR = 20
    CANCEL_SHUTDOWN_DEF_HOUR = 21
    REQUEST_PUBLIC_INFO = 22
    REQUEST_CLAN_CARD = 23
    ADD_FAVORITE = 24
    REMOVE_FAVORITE = 25
    PLAN_ATTACK = 26
    CREATE_OR_JOIN_FORT_BATTLE = 27
    ATTACK_AND_REQUEST_CARD = 28


FORT_REQUEST_TYPE_NAMES = dict([ (v, k) for k, v in FORT_REQUEST_TYPE.__dict__.iteritems() ])

class FORT_RESTRICTION(CONST_CONTAINER):
    UNKNOWN = 'unknown'
    NOT_AVAILABLE = 'notAvailable'
    CREATION_MIN_COUNT = 'creation/minCount'
    DIRECTION_MIN_COUNT = 'direction/minCount'
    DIRECTION_MAX_COUNT = 'direction/maxCount'
    DIRECTION_NOT_ENOUGH_MEMBERS = 'direction/notEnoughMembers'
    ORDER_MAX_COUNT = 'order/maxCount'
    BUILDING_CANT_UPGRADE = 'building/cantUpgrade'
    BUILDING_FORT_LEVEL_TOO_LOW = 'building/fortLevelToLow'
    BUILDING_NOT_ENOUGH_RESOURCE = 'building/notEnoughResource'
    BUILDING_NOT_ENOUGH_RESOURCE_AND_LOW_LEVEL = 'building/notEnoughResourceAndLowLevel'
    SORTIE_LEVEL_INVALID = 'sortie/levelInvalid'
    SORTIE_MAX_COUNT = 'sortie/maxCount'
    SORTIE_HAS_MODAL_ENTITY = 'sortie/hasModalEntity'
    STARTING_SCRIPT_NOT_DONE = 'startingScript/notDone'


class FORT_REQUEST_VALIDATION(CONST_CONTAINER):

    class REQUEST_PUBLIC_INFO(CONST_CONTAINER):
        ABBREV_IS_INVALID = 'publicInfo/abbrev/invalid'
        ABBREV_IS_INVALID_KR_CN = 'publicInfo/abbrev/invalid/KR_CN'
        ABBREV_IS_OURS = 'publicInfo/abbrev/ours'
