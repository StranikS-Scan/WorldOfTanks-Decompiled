# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/server_events/__init__.py


def registerWhiteTigerBattleResultsKeys():
    from gui.server_events.cond_formatters import BATTLE_RESULTS_KEYS
    from personal_missions_constants import CONDITION_ICON
    BATTLE_RESULTS_KEYS.update({'wtBossVulnerableDamage': CONDITION_ICON.DAMAGE,
     'maxWtPlasmaBonus': CONDITION_ICON.IMPROVE,
     'wtGeneratorsCaptured': CONDITION_ICON.BASE_CAPTURE,
     'wtDeathCount': CONDITION_ICON.SURVIVE,
     'wtMiniBossDestroyed': CONDITION_ICON.DAMAGE,
     'wtKilledByHyperionCount': CONDITION_ICON.SURVIVE,
     'wtBattleVSPriorityBoss': CONDITION_ICON.DAMAGE})
