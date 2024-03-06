# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/rewards_sort.py
import logging
import re
from functools import partial
from enum import Enum, unique
from gui import GUI_NATIONS, GUI_NATIONS_ORDER_INDEX
from gui.impl.gen import R
from gui.impl import backport
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
    FRONTLINE_BATTLE_BOOSTER = 'battleBooster'


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
 _RewardType.MODERNIZED_DEVICE: (_Reward.AIM_DRIVES_AIM_STABILIZER, _Reward.HEALTH_RESERVE_ANTI_FRAGMENTATION, _Reward.TURBOCHARGER_ROT_MECHANISM)}
_BASE_PATTERN = '(basic|enhanced|improved|trophy|modernized)*([a-z]+)'
_REWARD_NAME_EXTRACTOR = re.compile(_BASE_PATTERN + '(_+\\w+\\d*|\\d*)*', re.I)
_REWARD_BATTLE_BOOSTER_EXTRACTOR = re.compile(_BASE_PATTERN + '(battleBooster*)', re.I)
_REWARD_NATION_EXTRACTOR = re.compile('.*({})'.format('|'.join(GUI_NATIONS)), re.I)

def _extractRewardName(rewardRawName, extractor):
    name = extractor.sub('\\2', rewardRawName)
    return name[0].upper() + name[1:]


def _extractRewardNation(rewardRawName):
    return _REWARD_NATION_EXTRACTOR.sub('\\1', rewardRawName)


def _rewardTypeComparator(first, second):
    return cmp(safeIndexOf(_RewardType.makeValue(first[0]), _REWARDS_TYPES_ORDER), safeIndexOf(_RewardType.makeValue(second[0]), _REWARDS_TYPES_ORDER))


def _compareRewardsByNation(first, second):
    return cmp(GUI_NATIONS_ORDER_INDEX.get(_extractRewardNation(first[0]), NONE_INDEX), GUI_NATIONS_ORDER_INDEX.get(_extractRewardNation(second[0]), NONE_INDEX))


def _compareRewardsByType(rewardType, first, second):
    order = _REWARDS_ORDER[rewardType]
    extractor = _REWARD_BATTLE_BOOSTER_EXTRACTOR if rewardType == _RewardType.BATTLE_BOOSTER else _REWARD_NAME_EXTRACTOR
    return cmp(safeIndexOf(_Reward.makeValue(_extractRewardName(first[0], extractor)), order), safeIndexOf(_Reward.makeValue(_extractRewardName(second[0], extractor)), order))


def _compareRewardsByArtifactName(first, second):
    artefacts = R.strings.artefacts

    def _safeExtract(path):
        folder = artefacts.dyn(path)
        return backport.text(folder.name()) if folder else ''

    return cmp(_safeExtract(first[0]), _safeExtract(second[0]))


def _defaultComparator(first, second):
    return cmp(first[0], second[0])


_REWARDS_COMPARATORS = {_RewardType.TROPHY: partial(_compareRewardsByType, _RewardType.TROPHY),
 _RewardType.DEVICE: partial(_compareRewardsByType, _RewardType.DEVICE),
 _RewardType.GUIDE: _compareRewardsByNation,
 _RewardType.BROCHURE: _compareRewardsByNation,
 _RewardType.BLUEPRINT: _compareRewardsByNation,
 _RewardType.BATTLE_BOOSTER: partial(_compareRewardsByType, _RewardType.BATTLE_BOOSTER),
 _RewardType.MODERNIZED_DEVICE: partial(_compareRewardsByType, _RewardType.MODERNIZED_DEVICE),
 _RewardType.FRONTLINE_BATTLE_BOOSTER: _compareRewardsByArtifactName}

def getRewardTypesComparator():
    return _rewardTypeComparator


def getRewardsComparator(rewardTypeName):
    return _REWARDS_COMPARATORS.get(_RewardType.makeValue(rewardTypeName), _defaultComparator)
