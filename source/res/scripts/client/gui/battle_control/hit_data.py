# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/hit_data.py
from gui.battle_control.battle_constants import HIT_FLAGS
from constants import ATTACK_REASON_INDICES, ATTACK_REASON
from shared_utils import BitmaskHelper
from helpers import i18n
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
_NONE_PLAYER_ATTACK_REASON_TAG = {ATTACK_REASON_INDICES['artillery_protection']: (INGAME_GUI.ATTACKREASON_ARTILLERYPROTECTION, 'artillery'),
 ATTACK_REASON_INDICES['artillery_sector']: (INGAME_GUI.ATTACKREASON_ARTILLERY_SECTOR, 'artillery'),
 ATTACK_REASON_INDICES['bombers']: (INGAME_GUI.ATTACKREASON_BOMBERS, 'bomber')}

class HitData(object):
    __slots__ = ('__yaw', '__attackerID', '__damage', '__attackerVehName', '__attackerVehClassTag', '__playerVehMaxHP', '__hitFlags', '__critFlags', '__critsCount', '__attackReasonID')

    def __init__(self, yaw=0, attackerID=0, attackerVehName='', attackerVehClassTag=None, playerVehMaxHP=0, damage=0, critFlags=0, isAlly=False, isBlocked=False, isHighExplosive=False, attackReasonID=0):
        super(HitData, self).__init__()
        self.__yaw = yaw
        self.__attackerID = attackerID
        self.__damage = damage
        self.__attackerVehName = attackerVehName
        self.__attackerVehClassTag = attackerVehClassTag or ''
        self.__playerVehMaxHP = playerVehMaxHP
        self.__attackReasonID = attackReasonID
        self.__critFlags = critFlags
        self.__critsCount = BitmaskHelper.getSetBitsCount(self.__critFlags)
        self.__hitFlags = self.__buildFlags(attackerID=attackerID, damage=damage, isAlly=isAlly, isBlocked=isBlocked, critFlags=critFlags, isHighExplosive=isHighExplosive, attackReasonID=attackReasonID)
        if self.isNonPlayerAttackReason():
            attackReasonSettings = _NONE_PLAYER_ATTACK_REASON_TAG[attackReasonID]
            self.__attackerVehName = i18n.makeString(attackReasonSettings[0])
            self.__attackerVehClassTag = attackReasonSettings[1]

    def __repr__(self):
        return 'HitData: attackerID={}, yaw={}, damage={}, attacker vehicle=[name={}, class={}], player vehicle=[hp={}], hitFlags={}, critFlags={}[count={}]'.format(self.__attackerID, self.__yaw, self.__damage, self.__attackerVehName, self.__attackerVehClassTag, self.__playerVehMaxHP, self.__hitFlags, self.__critFlags, self.__critsCount)

    def getYaw(self):
        return self.__yaw

    def getAttackerID(self):
        return self.__attackerID

    def getAttackerVehicleClassTag(self):
        return self.__attackerVehClassTag

    def getPlayerVehicleMaxHP(self):
        return self.__playerVehMaxHP

    def getAttackerVehicleName(self):
        return self.__attackerVehName

    def getDamage(self):
        return self.__damage

    def getHitFlags(self):
        return self.__hitFlags

    def getCriticalFlags(self):
        return self.__critFlags

    def getCritsCount(self):
        return self.__critsCount

    def isAttackerAlly(self):
        return BitmaskHelper.hasAnyBitSet(self.__hitFlags, HIT_FLAGS.IS_ALLAY)

    def isBlocked(self):
        return BitmaskHelper.hasAnyBitSet(self.__hitFlags, HIT_FLAGS.IS_BLOCKED)

    def isCritical(self):
        return BitmaskHelper.hasAnyBitSet(self.__hitFlags, HIT_FLAGS.IS_CRITICAL)

    def isHighExplosive(self):
        return BitmaskHelper.hasAnyBitSet(self.__hitFlags, HIT_FLAGS.IS_HIGH_EXPLOSIVE)

    def isBattleConsumables(self):
        return BitmaskHelper.hasAnyBitSet(self.__hitFlags, HIT_FLAGS.IS_BATTLE_CONSUMABLES)

    def isNonPlayerAttackReason(self):
        return BitmaskHelper.hasAnyBitSet(self.__hitFlags, HIT_FLAGS.IS_NON_PLAYER_ATTACK_REASON)

    def isBattleAbilityConsumable(self):
        return self.__attackReasonID in (ATTACK_REASON.getIndex(ATTACK_REASON.ARTILLERY_EQ), ATTACK_REASON.getIndex(ATTACK_REASON.BOMBER_EQ))

    def isDamage(self):
        return self.isCritical() or not self.isBlocked() and self.__damage > 0

    def extend(self, hitData):
        self.__yaw = hitData.getYaw()
        self.__hitFlags |= hitData.getHitFlags()
        self.__critFlags |= hitData.getCriticalFlags()
        self.__critsCount = BitmaskHelper.getSetBitsCount(self.__critFlags)
        self.__damage += hitData.getDamage()

    @staticmethod
    def __buildFlags(attackerID, damage, isAlly, isBlocked, critFlags, isHighExplosive, attackReasonID):
        flags = 0
        if damage > 0:
            flags |= HIT_FLAGS.HP_DAMAGE
        if isAlly:
            flags |= HIT_FLAGS.IS_ALLAY
        if isBlocked:
            flags |= HIT_FLAGS.IS_BLOCKED
        if critFlags > 0:
            flags |= HIT_FLAGS.IS_CRITICAL
        if isHighExplosive:
            flags |= HIT_FLAGS.IS_HIGH_EXPLOSIVE
        if attackerID == 0:
            flags |= HIT_FLAGS.IS_BATTLE_CONSUMABLES
        if attackReasonID in _NONE_PLAYER_ATTACK_REASON_TAG:
            flags |= HIT_FLAGS.IS_NON_PLAYER_ATTACK_REASON
        return flags
