# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/server_events/__init__.py
from __future__ import absolute_import

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


def registerWhiteTigerDailyQuestDecorationMap():
    from constants import DailyQuestDecorationMap
    from soft_exception import SoftException
    from white_tiger.gui.white_tiger_gui_constants import WTDailyQuestDecorationMap
    commonKeys = set(DailyQuestDecorationMap) & set(WTDailyQuestDecorationMap)
    if commonKeys:
        raise SoftException('DailyQuestDecorationMap already has keys: {}'.format(commonKeys))
    DailyQuestDecorationMap.update(WTDailyQuestDecorationMap)
