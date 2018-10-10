# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/unit_helpers/MsgProcessor.py
from debug_utils import LOG_DEBUG_DEV, LOG_DEBUG_DEV
from ops_pack import OpsPacker, OpsUnpacker, initOpsFormatDef

class CBM_OP:
    SET_ROUND = 0
    SET_RESULTS = 2
    SET_ENEMY_READY = 3


class ClanBattleMgrMsgProcessor(OpsUnpacker):
    _opsFormatDefs = initOpsFormatDef({CBM_OP.SET_ROUND: ('B', '_setRound'),
     CBM_OP.SET_RESULTS: ('b', '_setResults'),
     CBM_OP.SET_ENEMY_READY: ('B', '_setEnemyReady')})

    def __init__(self, unit):
        self._unit = unit

    def _setRound(self, isBattleRound):
        LOG_DEBUG_DEV('ClanBattleMgrMsgProcessor._setRound: %r' % isBattleRound)
        extras = self._unit._extras
        extras['isBattleRound'] = int(isBattleRound)

    def _setResults(self, result):
        LOG_DEBUG_DEV('ClanBattleMgrMsgProcessor._setResults: res=%r' % result)
        extras = self._unit._extras
        extras['battleResultList'].append(result)

    def _setEnemyReady(self, enemyReady):
        LOG_DEBUG_DEV('ClanBattleMgrMsgProcessor._setEnemyReady: enemyReady=%r' % enemyReady)
        extras = self._unit._extras
        extras['isEnemyReadyForBattle'] = enemyReady


class ClanBattleMgrOpsPacker(OpsPacker, ClanBattleMgrMsgProcessor):
    pass
