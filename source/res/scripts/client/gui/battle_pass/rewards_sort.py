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
    BLUEPRINT = 'blueprint'
    BROCHURE = 'brochure'
    DEVICE_FV = 'new_device_fv'
    DEVICE_MI = 'new_device_mi'
    GUIDE = 'guide'
    TROPHY = 'trophy'
    BOOK = 'book'
    BATTLE_BOOSTER = 'battleBooster'
    EXP_EQUIPMENTS = 'expequipments'


@unique
class _Reward(_Enum):
    AIM_DRIVES = 'AimDrives'
    AIM_STABILIZER = 'AimingStabilizer'
    ANTI_FRAGMENTATION = 'AntifragmentationLining'
    BLUEPRINT = 'Blueprint'
    BROCHURE = 'Brochure'
    CAMOUFLAGE = 'CamouflageNet'
    COMM_VIEW = 'CommandersView'
    CONFIGURATION = 'Configuration'
    GROUSERS = 'Grousers'
    GUIDE = 'Guide'
    HEALTH_RESERVE = 'ExtraHealthReserve'
    INVIS_DEVICE = 'AdditionalInvisibilityDevice'
    OPTICS = 'CoatedOptics'
    RADIO = 'RadioCommunication'
    ROT_MECHANISM = 'RotationMechanism'
    SIGHTS = 'Sights'
    STEREOSCOPE = 'Stereoscope'
    TANK_RAMMER = 'TankRammer'
    TURBOCHARGER = 'Turbocharger'
    VENTILATION = 'Ventilation'
    MODERNIZED_AIM_STABILIZER = 'ModernizedAimDrivesAimingStabilizer1'
    MODERNIZED_TURBO_CHARGER_ROTATION = 'ModernizedTurbochargerRotationMechanism1'
    MODERNIZED_EXTRA_HEALTH_RESERVE = 'ModernizedExtraHealthReserveAntifragmentationLining1'


_REWARDS_TYPES_ORDER = (_RewardType.TROPHY,
 _RewardType.EXP_EQUIPMENTS,
 _RewardType.DEVICE_FV,
 _RewardType.DEVICE_MI,
 _RewardType.BOOK,
 _RewardType.GUIDE,
 _RewardType.BROCHURE,
 _RewardType.BLUEPRINT)
_REWARDS_ORDER = {_RewardType.TROPHY: (_Reward.AIM_DRIVES,
                      _Reward.TANK_RAMMER,
                      _Reward.VENTILATION,
                      _Reward.OPTICS,
                      _Reward.AIM_STABILIZER,
                      _Reward.CONFIGURATION,
                      _Reward.ROT_MECHANISM,
                      _Reward.SIGHTS,
                      _Reward.INVIS_DEVICE),
 _RewardType.DEVICE_FV: (_Reward.VENTILATION,
                         _Reward.TANK_RAMMER,
                         _Reward.AIM_DRIVES,
                         _Reward.AIM_STABILIZER,
                         _Reward.SIGHTS,
                         _Reward.ROT_MECHANISM,
                         _Reward.ANTI_FRAGMENTATION,
                         _Reward.HEALTH_RESERVE,
                         _Reward.CONFIGURATION),
 _RewardType.DEVICE_MI: (_Reward.VENTILATION,
                         _Reward.GROUSERS,
                         _Reward.ROT_MECHANISM,
                         _Reward.TURBOCHARGER,
                         _Reward.STEREOSCOPE,
                         _Reward.CAMOUFLAGE,
                         _Reward.INVIS_DEVICE,
                         _Reward.OPTICS,
                         _Reward.RADIO,
                         _Reward.COMM_VIEW),
 _RewardType.BATTLE_BOOSTER: (_Reward.VENTILATION,
                              _Reward.TANK_RAMMER,
                              _Reward.AIM_DRIVES,
                              _Reward.AIM_STABILIZER,
                              _Reward.SIGHTS,
                              _Reward.ROT_MECHANISM,
                              _Reward.ANTI_FRAGMENTATION,
                              _Reward.HEALTH_RESERVE,
                              _Reward.CONFIGURATION),
 _RewardType.EXP_EQUIPMENTS: (_Reward.MODERNIZED_AIM_STABILIZER, _Reward.MODERNIZED_TURBO_CHARGER_ROTATION, _Reward.MODERNIZED_EXTRA_HEALTH_RESERVE)}
_REWARD_NAME_EXTRACTOR = re.compile('(basic|enhanced|improved|trophy)*([a-z]+)(_(\\w+\\d*))*', re.I)
_REWARD_NATION_EXTRACTOR = re.compile('.*({})'.format('|'.join(GUI_NATIONS)), re.I)

def _extractRewardName(rewardRawName):
    name = _REWARD_NAME_EXTRACTOR.sub('\\2', rewardRawName)
    return name[0].upper() + name[1:]


def _extractRewardNation(rewardRawName):
    return _REWARD_NATION_EXTRACTOR.sub('\\1', rewardRawName)


def _rewardTypeComparator(first, second):
    return cmp(safeIndexOf(_RewardType.makeValue(first[0]), _REWARDS_TYPES_ORDER), safeIndexOf(_RewardType.makeValue(second[0]), _REWARDS_TYPES_ORDER))


def _compareRewardsByNation(first, second):
    return cmp(GUI_NATIONS_ORDER_INDEX.get(_extractRewardNation(first[0]), NONE_INDEX), GUI_NATIONS_ORDER_INDEX.get(_extractRewardNation(second[0]), NONE_INDEX))


def _compareRewardsByType(rewardType, first, second):
    order = _REWARDS_ORDER[rewardType]
    return cmp(safeIndexOf(_Reward.makeValue(_extractRewardName(first[0])), order), safeIndexOf(_Reward.makeValue(_extractRewardName(second[0])), order))


def _compareRewardsByArtifactName(first, second):
    artefacts = R.strings.artefacts

    def _safeExtract(path):
        folder = artefacts.dyn(path)
        return backport.text(folder.name()) if folder else ''

    return cmp(_safeExtract(first[0]), _safeExtract(second[0]))


def _defaultComparator(first, second):
    return cmp(first[0], second[0])


_REWARDS_COMPARATORS = {_RewardType.TROPHY: partial(_compareRewardsByType, _RewardType.TROPHY),
 _RewardType.DEVICE_FV: partial(_compareRewardsByType, _RewardType.DEVICE_FV),
 _RewardType.DEVICE_MI: partial(_compareRewardsByType, _RewardType.DEVICE_MI),
 _RewardType.GUIDE: _compareRewardsByNation,
 _RewardType.BROCHURE: _compareRewardsByNation,
 _RewardType.BOOK: _compareRewardsByNation,
 _RewardType.BLUEPRINT: _compareRewardsByNation,
 _RewardType.BATTLE_BOOSTER: _compareRewardsByArtifactName,
 _RewardType.EXP_EQUIPMENTS: partial(_compareRewardsByType, _RewardType.EXP_EQUIPMENTS)}

def getRewardTypesComparator():
    return _rewardTypeComparator


def getRewardsComparator(rewardTypeName):
    return _REWARDS_COMPARATORS.get(_RewardType.makeValue(rewardTypeName), _defaultComparator)
