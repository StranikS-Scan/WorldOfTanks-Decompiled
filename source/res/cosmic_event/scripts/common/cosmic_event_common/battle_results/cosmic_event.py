# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/common/cosmic_event_common/battle_results/cosmic_event.py
from battle_results.battle_results_constants import BATTLE_RESULT_ENTRY_TYPE as ENTRY_TYPE
from cosmic_event_common.cosmic_event_common import ScoreEvents
BATTLE_RESULTS = [('cosmicTotalScore',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('cosmicScore/SHOT',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('cosmicScore/RAMMING',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('cosmicScore/KILL',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('cosmicScore/PICKUP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('cosmicScore/ABILITY_HIT',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('cosmicScore/ARTIFACT_SCAN',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('cosmicBattleEvent/SHOT',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('cosmicBattleEvent/RAMMING',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('cosmicBattleEvent/KILL',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('cosmicBattleEvent/PICKUP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('cosmicBattleEvent/ABILITY_HIT',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('cosmicBattleEvent/ARTIFACT_SCAN',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('cosmicEquipment/2458107',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('cosmicEquipment/2458619',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('cosmicEquipment/2459899',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('cosmicAbilitiesImpacts/BLACK_HOLE',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('cosmicAbilitiesImpacts/GRAVITY_FIELD',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('cosmicAbilitiesImpacts/SNIPER_SHOT',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('cosmicAbilitiesImpacts/POWER_SHOT',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF)]
BATTLE_RESULTS_NAMES = set([ i[0] for i in BATTLE_RESULTS ])
SCORE_EVENT_NAMES = set([ 'cosmicScore/' + i.name for i in ScoreEvents ])
BATTLE_EVENT_NAMES = set([ 'cosmicBattleEvent/' + i.name for i in ScoreEvents ])
