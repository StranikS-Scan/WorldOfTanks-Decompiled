# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/register_aditional_params.py
from __future__ import absolute_import

class FortRushConditionIcons(object):
    SCORE_POINTS = 'scorePoints'
    PROGRESSION_POINTS = 'progressionPoints'
    CAPTURES = 'captures'
    ZONE_DAMAGE_DEALT = 'zoneDamageDealt'
    RAMMING = 'ramming'


def registerConditionFormatterIcons():
    from personal_missions_constants import CONDITION_ICON
    from gui.server_events.cond_formatters import BATTLE_RESULTS_KEYS
    BATTLE_RESULTS_KEYS.update({'fortRush/scorePoints': FortRushConditionIcons.SCORE_POINTS,
     'fortRush/progressionPoints': FortRushConditionIcons.SCORE_POINTS,
     'fortRush/captures': FortRushConditionIcons.CAPTURES,
     'fortRush/neutralizes': FortRushConditionIcons.CAPTURES,
     'fortRush/firstCaptures': FortRushConditionIcons.CAPTURES,
     'fortRush/captorKills': CONDITION_ICON.KILL_VEHICLES,
     'fortRush/zoneDamageDealt': CONDITION_ICON.DAMAGE,
     'fortRush/LTNeutralizes': FortRushConditionIcons.CAPTURES,
     'fortRush/HTDamage': CONDITION_ICON.DAMAGE,
     'fortRush/ATSPGDamage': CONDITION_ICON.DAMAGE,
     'fortRush/ramming': FortRushConditionIcons.RAMMING,
     'fortRush/sameLife/captures': FortRushConditionIcons.CAPTURES,
     'deathCount': CONDITION_ICON.FOLDER})
