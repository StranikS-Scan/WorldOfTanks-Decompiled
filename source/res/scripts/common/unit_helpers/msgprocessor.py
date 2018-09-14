# Embedded file name: scripts/common/unit_helpers/MsgProcessor.py
from debug_utils import LOG_VLK_DEV, LOG_OGNICK_DEV
from ops_pack import OpsPacker, OpsUnpacker, initOpsFormatDef
from FortifiedRegionBase import parseDirPosByte

class FBM_OP:
    SET_ROUND = 0
    SET_BUILDNUM = 1
    SET_RESULTS = 2
    SET_ENEMY_READY = 3
    SET_EQUIPMENTS = 4
    CLEAR_EQUIPMENTS = 5


class FortBattleMgrMsgProcessor(OpsUnpacker):
    _opsFormatDefs = initOpsFormatDef({FBM_OP.SET_ROUND: ('B', '_setRound'),
     FBM_OP.SET_BUILDNUM: ('bi', '_setBuildnum'),
     FBM_OP.SET_RESULTS: ('b', '_setResults'),
     FBM_OP.SET_ENEMY_READY: ('B', '_setEnemyReady'),
     FBM_OP.SET_EQUIPMENTS: ('i',
                             '_setEquipments',
                             'N',
                             [('H', 'qB')]),
     FBM_OP.CLEAR_EQUIPMENTS: ('x', '_clearEquipments')})

    def __init__(self, unit):
        self._unit = unit

    def _clearEquipments(self):
        extras = self._unit._extras
        LOG_OGNICK_DEV('_clearEquipments')
        extras['clanEquipments'] = None
        return

    def _setEquipments(self, rev, clanEquipments):
        extras = self._unit._extras
        LOG_OGNICK_DEV('_setEquipments', clanEquipments)
        extras['lastEquipRev'] = rev
        extras['clanEquipments'] = (rev, clanEquipments)

    def _setRound(self, isBattleRound):
        LOG_VLK_DEV('FortBattleMgrMsgProcessor._setRound: %r' % isBattleRound)
        extras = self._unit._extras
        extras['isBattleRound'] = int(isBattleRound)

    def _setBuildnum(self, packedBuildsNum, roundStart = 0):
        extras = self._unit._extras
        prevBuildNum, currentBuildNum = parseDirPosByte(packedBuildsNum)
        LOG_VLK_DEV('FortBattleMgrMsgProcessor._setBuildnum: prev=%r, cur=%r' % (prevBuildNum, currentBuildNum))
        extras['prevBuildNum'] = prevBuildNum
        extras['currentBuildNum'] = currentBuildNum - 1
        extras['roundStart'] = roundStart

    def _setResults(self, result):
        LOG_VLK_DEV('FortBattleMgrMsgProcessor._setResults: res=%r' % result)
        extras = self._unit._extras
        extras['battleResultList'].append(result)

    def _setEnemyReady(self, enemyReady):
        LOG_VLK_DEV('FortBattleMgrMsgProcessor._setEnemyReady: enemyReady=%r' % enemyReady)
        extras = self._unit._extras
        extras['isEnemyReadyForBattle'] = enemyReady


class FortBattleMgrOpsPacker(OpsPacker, FortBattleMgrMsgProcessor):
    pass
