# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/bootcamp.py
from gui.battle_results.components import base, bootcamp
_BOOTCAMP_VO_META = base.DictMeta({'background': '',
 'unlocksAndMedals': [],
 'hasUnlocks': False,
 'stats': [],
 'resultTypeStr': '',
 'finishReasonStr': '',
 'showRewards': False,
 'playerVehicle': {'name': '',
                   'typeIcon': ''},
 'credits': {'value': 0,
             'str': '0'},
 'xp': {'value': 0,
        'str': '0'}})
_BOOTCAMP_PLAYERVEHICLE_VO_META = base.DictMeta({'name': '',
 'typeIcon': ''})
_BOOTCAMP_STATVALUE_VO_META = base.DictMeta({'value': 0,
 'str': '0'})
BOOTCAMP_RESULTS_BLOCK = base.StatsBlock(_BOOTCAMP_VO_META, '')
BOOTCAMP_RESULTS_BLOCK.addComponent(0, bootcamp.BackgroundItem('background'))
BOOTCAMP_RESULTS_BLOCK.addComponent(1, bootcamp.UnlocksAndMedalsBlock(base.ListMeta(), 'unlocksAndMedals'))
BOOTCAMP_RESULTS_BLOCK.addComponent(2, bootcamp.HasUnlocksFlag('hasUnlocks'))
BOOTCAMP_RESULTS_BLOCK.addComponent(3, bootcamp.StatsBlock(base.ListMeta(), 'stats'))
BOOTCAMP_RESULTS_BLOCK.addComponent(4, bootcamp.ResultTypeStrItem('resultTypeStr'))
BOOTCAMP_RESULTS_BLOCK.addComponent(5, bootcamp.FinishReasonItem('finishReasonStr'))
BOOTCAMP_RESULTS_BLOCK.addComponent(6, bootcamp.ShowRewardsFlag('showRewards'))
BOOTCAMP_RESULTS_BLOCK.addComponent(7, bootcamp.PlayerVehicleBlock(_BOOTCAMP_PLAYERVEHICLE_VO_META, 'playerVehicle'))
BOOTCAMP_RESULTS_BLOCK.addComponent(8, bootcamp.CreditsBlock(_BOOTCAMP_STATVALUE_VO_META, 'credits'))
BOOTCAMP_RESULTS_BLOCK.addComponent(9, bootcamp.XPBlock(_BOOTCAMP_STATVALUE_VO_META, 'xp'))
