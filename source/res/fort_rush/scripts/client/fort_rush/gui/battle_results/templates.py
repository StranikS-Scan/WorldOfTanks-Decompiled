# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/battle_results/templates.py
from __future__ import absolute_import
from gui.battle_results.components import base
from fort_rush.gui.battle_results import components as ex
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
EXAMPLE_TOTAL_VO_META = base.DictMeta({'eventPoints': 0,
 'vehicleCommanderID': 0,
 'doubleTotalDamage': 0})
HB_TOTAL_RESULTS_BLOCK = base.StatsBlock(EXAMPLE_TOTAL_VO_META, 'victoryData')
HB_TOTAL_RESULTS_BLOCK.addNextComponent(ex.EventPointsItem('eventPoints', _RECORD.PERSONAL))
HB_TOTAL_RESULTS_BLOCK.addNextComponent(ex.VehicleCommanderIDItem('vehicleCommanderID', _RECORD.PERSONAL))
HB_TOTAL_RESULTS_BLOCK.addNextComponent(ex.VehicleDoubleDamage('doubleTotalDamage', _RECORD.PERSONAL))
