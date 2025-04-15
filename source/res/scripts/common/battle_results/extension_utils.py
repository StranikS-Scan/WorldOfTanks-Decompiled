# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_results/extension_utils.py
import types
from debug_utils import LOG_DEBUG

def initBattleResultsConfigFromExtension(arenaBonusType, config):
    if config is None:
        LOG_DEBUG('initBattleResultsConfigFromExtension: config is None')
        return
    else:
        from battle_results import battle_results_constants
        module = config.__name__
        battle_results_constants.PATH_TO_CONFIG.update({arenaBonusType: module})
        return


def initBattleResultsFromExtension(arenaBonusType, config=None):
    initBattleResultsConfigFromExtension(arenaBonusType, config)
