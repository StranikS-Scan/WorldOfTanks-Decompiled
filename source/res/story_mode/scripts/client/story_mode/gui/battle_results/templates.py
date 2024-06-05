# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_results/templates.py
from gui.battle_results.components import base
from gui.battle_results.components.common import ArenaDurationItem, ArenaDateTimeItem
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from story_mode.gui.battle_results.components import FinishResultItem, FinishReasonItem, MissionIdItem, VehicleNameItem, VehicleBlock, IsForceOnboardingItem, RewardsBlock, ProgressionInfoItem
_STORY_MODE_VO_META = base.DictMeta({'finishResult': '',
 'finishReason': None,
 'missionId': 1,
 'isForceOnboarding': False,
 'arenaDuration': '',
 'arenaDateTime': '',
 'vehicleName': '',
 'vehicle': {},
 'rewards': {},
 'progressionInfo': {}})
_VEHICLE_VO_META = base.DictMeta({'deathReason': -1,
 'damageDealt': 0,
 'kills': 0,
 'damageAssisted': 0,
 'damageBlockedByArmor': 0})
STORY_MODE_RESULTS_BLOCK = base.StatsBlock(_STORY_MODE_VO_META, '')
STORY_MODE_RESULTS_BLOCK.addNextComponent(FinishResultItem('finishResult', _RECORD.PERSONAL))
STORY_MODE_RESULTS_BLOCK.addNextComponent(FinishReasonItem('finishReason', _RECORD.PERSONAL))
STORY_MODE_RESULTS_BLOCK.addNextComponent(MissionIdItem('missionId', _RECORD.PERSONAL))
STORY_MODE_RESULTS_BLOCK.addNextComponent(IsForceOnboardingItem('isForceOnboarding', _RECORD.PERSONAL))
STORY_MODE_RESULTS_BLOCK.addNextComponent(ArenaDurationItem('arenaDuration', _RECORD.COMMON, 'duration'))
STORY_MODE_RESULTS_BLOCK.addNextComponent(ArenaDateTimeItem('arenaDateTime', _RECORD.COMMON, 'arenaCreateTime'))
STORY_MODE_RESULTS_BLOCK.addNextComponent(VehicleNameItem('vehicleName'))
STORY_MODE_RESULTS_BLOCK.addNextComponent(VehicleBlock(_VEHICLE_VO_META, 'vehicle'))
STORY_MODE_RESULTS_BLOCK.addNextComponent(RewardsBlock(base.ListMeta(), 'rewards'))
STORY_MODE_RESULTS_BLOCK.addNextComponent(ProgressionInfoItem('progressionInfo', _RECORD.PERSONAL))
