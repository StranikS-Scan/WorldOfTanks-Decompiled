# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/unit_helpers/MsgProcessor.py
from debug_utils import LOG_DEBUG_DEV, LOG_DEBUG_DEV
from ops_pack import OpsPacker, OpsUnpacker, initOpsFormatDef
from FortifiedRegionBase import parseDirPosByte

class CBM_OP:
    SET_ROUND = 0
    SET_BUILDNUM = 1
    SET_RESULTS = 2
    SET_ENEMY_READY = 3
    SET_EQUIPMENTS = 4
    CLEAR_EQUIPMENTS = 5


class ClanBattleMgrMsgProcessor(OpsUnpacker):
    _opsFormatDefs = initOpsFormatDef({CBM_OP.SET_ROUND: ('B', '_setRound'),
     CBM_OP.SET_BUILDNUM: ('bi', '_setBuildnum'),
     CBM_OP.SET_RESULTS: ('b', '_setResults'),
     CBM_OP.SET_ENEMY_READY: ('B', '_setEnemyReady'),
     CBM_OP.SET_EQUIPMENTS: ('i',
                             '_setEquipments',
                             'N',
                             [('H', 'qB')]),
     CBM_OP.CLEAR_EQUIPMENTS: ('x', '_clearEquipments')})

    def __init__(self, unit):
        self._unit = unit

    def _clearEquipments(self):
        extras = self._unit._extras
        LOG_DEBUG_DEV('_clearEquipments')
        extras['clanEquipments'] = None
        return

    def _setEquipments(self, rev, clanEquipments):
        extras = self._unit._extras
        LOG_DEBUG_DEV('_setEquipments', clanEquipments)
        extras['lastEquipRev'] = rev
        extras['clanEquipments'] = (rev, clanEquipments)

    def _setRound(self, isBattleRound):
        LOG_DEBUG_DEV('ClanBattleMgrMsgProcessor._setRound: %r' % isBattleRound)
        extras = self._unit._extras
        extras['isBattleRound'] = int(isBattleRound)

    def _setBuildnum(self, packedBuildsNum, roundStart=0):
        extras = self._unit._extras
        prevBuildNum, currentBuildNum = parseDirPosByte(packedBuildsNum)
        LOG_DEBUG_DEV('ClanBattleMgrMsgProcessor._setBuildnum: prev=%r, cur=%r' % (prevBuildNum, currentBuildNum))
        extras['prevBuildNum'] = prevBuildNum
        extras['currentBuildNum'] = currentBuildNum - 1
        extras['roundStart'] = roundStart

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
