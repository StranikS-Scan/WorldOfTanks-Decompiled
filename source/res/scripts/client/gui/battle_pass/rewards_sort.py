# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/rewards_sort.py
from __future__ import absolute_import
import logging
import re
from enum import Enum, unique
from functools import partial
from gui import GUI_NATIONS, GUI_NATIONS_ORDER_INDEX
from nations import NONE_INDEX
from shared_utils import safeIndexOf
_logger = logging.getLogger(__name__)

class _Enum(Enum):

    @classmethod
    def makeValue(cls, value):
        if value in cls._value2member_map_:
            return cls(value)
        else:
            _logger.error('%s is not a valid init value for %s', value, cls.__name__)
            return None


@unique
class _RewardType(_Enum):
    BATTLE_BOOSTER = 'battle_booster'
    BLUEPRINT = 'blueprint'
    BROCHURE = 'brochure'
    DEVICE = 'new_device'
    GUIDE = 'guide'
    MODERNIZED_DEVICE = 'modernized_device'
    TROPHY = 'trophy'
    CREW_BOOK = 'crewbook'


@unique
class _Reward(_Enum):
    ADDIT_INVISIBILITY_DEVICE = 'AdditInvisibilityDevice'
    ADDITIONAL_INVISIBILITY_DEVICE = 'AdditionalInvisibilityDevice'
    AIM_DRIVES = 'AimDrives'
    AIM_STABILIZER = 'AimingStabilizer'
    AIM_DRIVES_AIM_STABILIZER = 'AimDrivesAimingStabilizer'
    ANTI_FRAGMENTATION = 'AntifragmentationLining'
    BLUEPRINT = 'Blueprint'
    BROCHURE = 'Brochure'
    CAMOUFLAGE = 'CamouflageNet'
    COMM_VIEW = 'CommandersView'
    CONFIGURATION = 'Configuration'
    GROUSERS = 'Grousers'
    GUIDE = 'Guide'
    HEALTH_RESERVE = 'ExtraHealthReserve'
    HEALTH_RESERVE_ANTI_FRAGMENTATION = 'ExtraHealthReserveAntifragmentationLining'
    OPTICS = 'CoatedOptics'
    RADIO = 'RadioCommunication'
    ROT_MECHANISM = 'RotationMechanism'
    SIGHTS = 'Sights'
    SIGHTS_ENHANCED_AIM_DRIVES = 'SightsEnhancedAimDrives'
    STEREOSCOPE = 'Stereoscope'
    TANK_RAMMER = 'TankRammer'
    TURBOCHARGER = 'Turbocharger'
    TURBOCHARGER_ROT_MECHANISM = 'TurbochargerRotationMechanism'
    RAMMER = 'Rammer'
    VENTILATION = 'Ventilation'


_REWARDS_TYPES_ORDER = (_RewardType.TROPHY,
 _RewardType.MODERNIZED_DEVICE,
 _RewardType.DEVICE,
 _RewardType.BLUEPRINT,
 _RewardType.BATTLE_BOOSTER,
 _RewardType.CREW_BOOK,
 _RewardType.GUIDE,
 _RewardType.BROCHURE)
_REWARDS_ORDER = {_RewardType.TROPHY: (_Reward.TURBOCHARGER,
                      _Reward.HEALTH_RESERVE,
                      _Reward.AIM_DRIVES,
                      _Reward.TANK_RAMMER,
                      _Reward.VENTILATION,
                      _Reward.OPTICS,
                      _Reward.AIM_STABILIZER,
                      _Reward.CONFIGURATION,
                      _Reward.ROT_MECHANISM,
                      _Reward.SIGHTS,
                      _Reward.ADDITIONAL_INVISIBILITY_DEVICE),
 _RewardType.DEVICE: (_Reward.VENTILATION,
                      _Reward.TANK_RAMMER,
                      _Reward.AIM_DRIVES,
                      _Reward.AIM_STABILIZER,
                      _Reward.SIGHTS,
                      _Reward.ROT_MECHANISM,
                      _Reward.ANTI_FRAGMENTATION,
                      _Reward.HEALTH_RESERVE,
                      _Reward.CONFIGURATION,
                      _Reward.VENTILATION,
                      _Reward.GROUSERS,
                      _Reward.TURBOCHARGER,
                      _Reward.STEREOSCOPE,
                      _Reward.CAMOUFLAGE,
                      _Reward.ADDITIONAL_INVISIBILITY_DEVICE,
                      _Reward.OPTICS,
                      _Reward.RADIO,
                      _Reward.COMM_VIEW),
 _RewardType.BATTLE_BOOSTER: (_Reward.AIM_DRIVES,
                              _Reward.RAMMER,
                              _Reward.AIM_STABILIZER,
                              _Reward.OPTICS,
                              _Reward.VENTILATION,
                              _Reward.CONFIGURATION,
                              _Reward.TURBOCHARGER,
                              _Reward.SIGHTS,
                              _Reward.ADDIT_INVISIBILITY_DEVICE),
 _RewardType.MODERNIZED_DEVICE: (_Reward.AIM_DRIVES_AIM_STABILIZER,
                                 _Reward.HEALTH_RESERVE_ANTI_FRAGMENTATION,
                                 _Reward.TURBOCHARGER_ROT_MECHANISM,
                                 _Reward.SIGHTS_ENHANCED_AIM_DRIVES)}
_BASE_PATTERN = '(basic|enhanced|improved|trophy|modernized)*([a-z]+)'
_REWARD_NAME_EXTRACTOR = re.compile(_BASE_PATTERN + '(_+\\w+\\d*|\\d*)*', re.I)
_REWARD_BATTLE_BOOSTER_EXTRACTOR = re.compile(_BASE_PATTERN + '(battleBooster*)', re.I)
_REWARD_NATION_EXTRACTOR = re.compile('.*({})'.format('|'.join(GUI_NATIONS)), re.I)

def _extractRewardName(rewardRawName, extractor):
    name = extractor.sub('\\2', rewardRawName)
    return name[0].upper() + name[1:]


def _extractRewardNation(rewardRawName):
    return _REWARD_NATION_EXTRACTOR.sub('\\1', rewardRawName)


def _rewardTypeSortKey(item):
    return safeIndexOf(_RewardType.makeValue(item[0]), _REWARDS_TYPES_ORDER)


def _rewardSortByNation(item):
    return GUI_NATIONS_ORDER_INDEX.get(_extractRewardNation(item[0]), NONE_INDEX)


def _rewardSortByType(rewardType, item):
    order = _REWARDS_ORDER[rewardType]
    extractor = _REWARD_BATTLE_BOOSTER_EXTRACTOR if rewardType == _RewardType.BATTLE_BOOSTER else _REWARD_NAME_EXTRACTOR
    return safeIndexOf(_Reward.makeValue(_extractRewardName(item[0], extractor)), order)


def _defaultItemSort(item):
    return item[0]


_REWARDS_SORT_KEYS = {_RewardType.TROPHY: partial(_rewardSortByType, _RewardType.TROPHY),
 _RewardType.DEVICE: partial(_rewardSortByType, _RewardType.DEVICE),
 _RewardType.CREW_BOOK: _rewardSortByNation,
 _RewardType.GUIDE: _rewardSortByNation,
 _RewardType.BROCHURE: _rewardSortByNation,
 _RewardType.BLUEPRINT: _rewardSortByNation,
 _RewardType.BATTLE_BOOSTER: partial(_rewardSortByType, _RewardType.BATTLE_BOOSTER),
 _RewardType.MODERNIZED_DEVICE: partial(_rewardSortByType, _RewardType.MODERNIZED_DEVICE)}

def getTypesSortKey():
    return _rewardTypeSortKey


def getItemsSortKey(rewardTypeName):
    return _REWARDS_SORT_KEYS.get(_RewardType.makeValue(rewardTypeName), _defaultItemSort)
