# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/pet_system/constants.py
PET_NAME_FORMAT = 'petName_{0:d}'
EVENT_NAME_FORMAT = 'event_{0:d}'

class PS_PDATA_KEYS(object):
    ACTIVE_PETID = 'activePetID'
    ACTIVE_STATE_BEHAVIOR = 'activeStateBehavior'
    BONUS = 'bonus'
    EVENTS_DATA = 'eventsData'
    STORAGE = 'storage'
    UNLOCKED_PETS_IDS = 'unlockedPetsIds'
    ACTIVE_BONUS = 'activeBonus'
    APPLIED_BONUSES = 'applied'
    ACTIVE_EVENT = 'activeEvent'
    SELECTED_NAME = 'sSelectedName'
    SYNERGY_STORAGE = 'synergy'
    SYNERGY_POINTS = 'points'
    SYNERGY_LEVEL = 'level'
    SYNERGY_FIRST_CLICK = 'fClick'


class PetPlaceName(object):
    DEFAULT = 'default'
    STORAGE = 'storage'
    ALL = (DEFAULT, STORAGE)


class StorageStateKey(object):
    ACTIVE = 'active'
    LOCKED = 'locked'
    ALL = (ACTIVE, LOCKED)
