# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/maps_training.py
from gui.battle_results.components import base, maps_training
_MAPS_TRAINING_VO_META = base.DictMeta({'result': {},
 'goal': {},
 'duration': 0,
 'stats': [],
 'geometryId': 0,
 'team': 0,
 'vehicle': {},
 'doneValue': -1,
 'wasDone': False,
 'scenarioProgress': [],
 'rewards': [],
 'accountProgress': {}})
_MAPS_TRAINING_RESULT_VO_META = base.DictMeta({'str': '',
 'value': '',
 'win': False})
_MAPS_TRAINING_BATTLE_GOAL_VO_META = base.DictMeta({'heavyTank': [0, 0],
 'mediumTank': [0, 0],
 'lightTank': [0, 0],
 'SPG': [0, 0],
 'AT-SPG': [0, 0]})
_MAPS_TRAINING_VEHICLE_VO_META = base.DictMeta({'type': '',
 'name': ''})
_MAPS_TRAINING_ACC_PROGRESS_VO_META = base.DictMeta({'hasImproved': False})
_components = (maps_training.BattleResultBlock(_MAPS_TRAINING_RESULT_VO_META, 'result'),
 maps_training.BattleGoalsBlock(_MAPS_TRAINING_BATTLE_GOAL_VO_META, 'goal'),
 maps_training.BattleDurationItem('duration'),
 maps_training.StatsBlock(base.ListMeta(), 'stats'),
 maps_training.GeometryIdItem('geometryId'),
 maps_training.TeamItem('team'),
 maps_training.VehicleBlock(_MAPS_TRAINING_VEHICLE_VO_META, 'vehicle'),
 maps_training.DoneValueItem('doneValue'),
 maps_training.WasDoneItem('wasDone'),
 maps_training.ScenarioProgressBlock(base.ListMeta(), 'scenarioProgress'),
 maps_training.RewardsBlock(base.ListMeta(), 'rewards'),
 maps_training.AccountProgressBlock(_MAPS_TRAINING_ACC_PROGRESS_VO_META, 'accountProgress'))
MAPS_TRAINING_RESULTS_BLOCK = base.StatsBlock(_MAPS_TRAINING_VO_META, '')
for i, component in enumerate(_components):
    MAPS_TRAINING_RESULTS_BLOCK.addComponent(i, component)
