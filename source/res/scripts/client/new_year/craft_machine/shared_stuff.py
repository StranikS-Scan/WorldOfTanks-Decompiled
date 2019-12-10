# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine/shared_stuff.py
from items.components.ny_constants import RANDOM_VALUE, TOY_TYPE_IDS_BY_NAME, ToySettings, YEARS_INFO, MIN_TOY_RANK, MAX_TOY_RANK
from new_year.ny_constants import TOY_TYPES_FOR_OBJECTS_WITHOUT_MEGA

class AntiduplicatorState(object):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    ERROR = 'error'
    ALL = (ACTIVE, INACTIVE, ERROR)


class MegaDeviceState(object):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    ALL_MEGA_TOYS_COLLECTED_ERROR = 'all_mega_toys_collected_error'
    ERRORS = (ALL_MEGA_TOYS_COLLECTED_ERROR,)
    ACTIVATED = (ACTIVE, ALL_MEGA_TOYS_COLLECTED_ERROR)
    ALL = (ACTIVE, INACTIVE, ALL_MEGA_TOYS_COLLECTED_ERROR)


RANDOM_TOY_CONFIG_INDEX = 0
_TOY_TYPE_MAPPING = (RANDOM_VALUE,) + tuple((TOY_TYPE_IDS_BY_NAME[toyType] for toyType in TOY_TYPES_FOR_OBJECTS_WITHOUT_MEGA))
_TOY_SETTING_MAPPING = (RANDOM_VALUE,) + tuple((YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME[toySetting] for toySetting in ToySettings.NEW))
_TOY_RANK_MAPPING = (RANDOM_VALUE,) + tuple((i for i in xrange(MIN_TOY_RANK, MAX_TOY_RANK + 1)))
_TOY_TYPE_INV_MAPPING = {v:i for i, v in enumerate(_TOY_TYPE_MAPPING)}
_TOY_SETTING_INV_MAPPING = {v:i for i, v in enumerate(_TOY_SETTING_MAPPING)}
_TOY_RANK_INV_MAPPING = {v:i for i, v in enumerate(_TOY_RANK_MAPPING)}

def mapToyParamsFromCraftUiToSrv(toyTypeIdx=0, settingIdx=0, rankIdx=0):
    return (_TOY_TYPE_MAPPING[toyTypeIdx], _TOY_SETTING_MAPPING[settingIdx], _TOY_RANK_MAPPING[rankIdx])


def mapToyParamsFromSrvToCraftUi(toyType, setting, rank):
    return (_TOY_TYPE_INV_MAPPING[toyType], _TOY_SETTING_INV_MAPPING[setting], _TOY_RANK_INV_MAPPING[rank])


class CraftSettingsNames(object):
    ANTIDUPLICATOR_TURNED_ON = 'isAntiduplicatorTurnedOn'
    MEGA_DEVICE_TURNED_ON = 'isMegaDeviceTurnedOn'
    TOY_TYPE_ID = 'toyTypeIdx'
    TOY_SETTING_ID = 'toySettingIdx'
    TOY_RANK_ID = 'toyRankIdx'
    CRAFT_COST = 'craftCost'
