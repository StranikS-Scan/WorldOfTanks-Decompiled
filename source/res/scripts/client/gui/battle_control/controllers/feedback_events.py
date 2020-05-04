# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/feedback_events.py
import logging
from BattleFeedbackCommon import BATTLE_EVENT_TYPE as _BET, NONE_SHELL_TYPE
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _FET
from constants import ATTACK_REASON, ATTACK_REASONS, SHELL_TYPES_LIST
_logger = logging.getLogger(__name__)

def _unpackInteger(packedData):
    return packedData


def _unpackDamage(packedData):
    return _DamageExtra(*_BET.unpackDamage(packedData))


def _unpackCrits(packedData):
    return _CritsExtra(*_BET.unpackCrits(packedData))


def _unpackVisibility(packedData):
    return _VisibilityExtra(*_BET.unpackVisibility(packedData))


def _unpackMultiStun(packedData):
    return _MultiStunExtra(packedData, True)


_BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT = {_BET.KILL: _FET.PLAYER_KILLED_ENEMY,
 _BET.DAMAGE: _FET.PLAYER_DAMAGED_HP_ENEMY,
 _BET.CRIT: _FET.PLAYER_DAMAGED_DEVICE_ENEMY,
 _BET.SPOTTED: _FET.PLAYER_SPOTTED_ENEMY,
 _BET.RADIO_ASSIST: _FET.PLAYER_ASSIST_TO_KILL_ENEMY,
 _BET.TRACK_ASSIST: _FET.PLAYER_ASSIST_TO_KILL_ENEMY,
 _BET.STUN_ASSIST: _FET.PLAYER_ASSIST_TO_STUN_ENEMY,
 _BET.BASE_CAPTURE_POINTS: _FET.PLAYER_CAPTURED_BASE,
 _BET.BASE_CAPTURE_DROPPED: _FET.PLAYER_DROPPED_CAPTURE,
 _BET.BASE_CAPTURE_BLOCKED: _FET.PLAYER_BLOCKED_CAPTURE,
 _BET.TANKING: _FET.PLAYER_USED_ARMOR,
 _BET.RECEIVED_DAMAGE: _FET.ENEMY_DAMAGED_HP_PLAYER,
 _BET.RECEIVED_CRIT: _FET.ENEMY_DAMAGED_DEVICE_PLAYER,
 _BET.TARGET_VISIBILITY: _FET.VEHICLE_VISIBILITY_CHANGED,
 _BET.ENEMY_SECTOR_CAPTURED: _FET.ENEMY_SECTOR_CAPTURED,
 _BET.DESTRUCTIBLE_DAMAGED: _FET.DESTRUCTIBLE_DAMAGED,
 _BET.DESTRUCTIBLE_DESTROYED: _FET.DESTRUCTIBLE_DESTROYED,
 _BET.DESTRUCTIBLES_DEFENDED: _FET.DESTRUCTIBLES_DEFENDED,
 _BET.DEFENDER_BONUS: _FET.DEFENDER_BONUS,
 _BET.SMOKE_ASSIST: _FET.SMOKE_ASSIST,
 _BET.INSPIRE_ASSIST: _FET.INSPIRE_ASSIST,
 _BET.MULTI_STUN: _FET.PLAYER_STUN_ENEMIES}
_PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS = {_FET.PLAYER_DAMAGED_HP_ENEMY: _unpackDamage,
 _FET.PLAYER_ASSIST_TO_KILL_ENEMY: _unpackDamage,
 _FET.PLAYER_CAPTURED_BASE: _unpackInteger,
 _FET.PLAYER_DROPPED_CAPTURE: _unpackInteger,
 _FET.PLAYER_BLOCKED_CAPTURE: _unpackInteger,
 _FET.PLAYER_USED_ARMOR: _unpackDamage,
 _FET.PLAYER_DAMAGED_DEVICE_ENEMY: _unpackCrits,
 _FET.ENEMY_DAMAGED_HP_PLAYER: _unpackDamage,
 _FET.ENEMY_DAMAGED_DEVICE_PLAYER: _unpackCrits,
 _FET.PLAYER_ASSIST_TO_STUN_ENEMY: _unpackDamage,
 _FET.VEHICLE_VISIBILITY_CHANGED: _unpackVisibility,
 _FET.DESTRUCTIBLE_DAMAGED: _unpackInteger,
 _FET.DESTRUCTIBLES_DEFENDED: _unpackInteger,
 _FET.SMOKE_ASSIST: _unpackDamage,
 _FET.INSPIRE_ASSIST: _unpackDamage,
 _FET.PLAYER_SPOTTED_ENEMY: _unpackVisibility,
 _FET.PLAYER_STUN_ENEMIES: _unpackMultiStun}

def _getShellType(shellTypeID):
    return None if shellTypeID == NONE_SHELL_TYPE else SHELL_TYPES_LIST[shellTypeID]


class _DamageExtra(object):
    __slots__ = ('__damage', '__attackReasonID', '__isBurst', '__shellType', '__isShellGold', '__secondaryAttackReasonID', '__isRoleAction')

    def __init__(self, damage=0, attackReasonID=0, isBurst=False, shellTypeID=NONE_SHELL_TYPE, shellIsGold=False, secondaryAttackReasonID=0, isRoleAction=False):
        super(_DamageExtra, self).__init__()
        self.__damage = damage
        self.__attackReasonID = attackReasonID
        self.__isBurst = bool(isBurst)
        self.__shellType = _getShellType(shellTypeID)
        self.__isShellGold = bool(shellIsGold)
        self.__secondaryAttackReasonID = secondaryAttackReasonID
        self.__isRoleAction = bool(isRoleAction)
        _logger.debug('_DamageExtra isRoleAction = %s', isRoleAction)

    def getDamage(self):
        return self.__damage

    def getAttackReasonID(self):
        return self.__attackReasonID

    def getShellType(self):
        return self.__shellType

    def isBurst(self):
        return self.__isBurst

    def isShellGold(self):
        return self.__isShellGold

    def isFire(self):
        return self.isAttackReason(ATTACK_REASON.FIRE)

    def isRam(self):
        return self.isAttackReason(ATTACK_REASON.RAM)

    def isShot(self):
        return self.isAttackReason(ATTACK_REASON.SHOT)

    def isWorldCollision(self):
        return self.isAttackReason(ATTACK_REASON.WORLD_COLLISION)

    def isProtectionZone(self, primary=True):
        return self.isAttackReason(ATTACK_REASON.ARTILLERY_PROTECTION) or self.isAttackReason(ATTACK_REASON.ARTILLERY_SECTOR) if primary else self.isSecondaryAttackReason(ATTACK_REASON.ARTILLERY_PROTECTION) or self.isSecondaryAttackReason(ATTACK_REASON.ARTILLERY_SECTOR)

    def isArtilleryEq(self, primary=True):
        return self.isAttackReason(ATTACK_REASON.ARTILLERY_EQ) if primary else self.isSecondaryAttackReason(ATTACK_REASON.ARTILLERY_EQ)

    def isBomberEq(self, primary=True):
        return self.isAttackReason(ATTACK_REASON.BOMBER_EQ) if primary else self.isSecondaryAttackReason(ATTACK_REASON.BOMBER_EQ)

    def isEventPhaseChange(self, primary=True):
        return self.isAttackReason(ATTACK_REASON.EVENT_DEATH_ON_PHASE_CHANGE) or self.isAttackReason(ATTACK_REASON.EVENT_DEATH_ON_PHASE_CHANGE_FULL_SC) if primary else self.isSecondaryAttackReason(ATTACK_REASON.EVENT_DEATH_ON_PHASE_CHANGE) or self.isSecondaryAttackReason(ATTACK_REASON.EVENT_DEATH_ON_PHASE_CHANGE_FULL_SC)

    def isBombers(self, primary=True):
        return self.isAttackReason(ATTACK_REASON.BOMBERS) if primary else self.isSecondaryAttackReason(ATTACK_REASON.BOMBERS)

    def isDeathZone(self, primary=True):
        return self.isAttackReason(ATTACK_REASON.PERSONAL_DEATH_ZONE) or self.isAttackReason(ATTACK_REASON.DEATH_ZONE) if primary else self.isSecondaryAttackReason(ATTACK_REASON.PERSONAL_DEATH_ZONE) or self.isSecondaryAttackReason(ATTACK_REASON.DEATH_ZONE)

    def isMinefield(self, primary=True):
        return self.isAttackReason(ATTACK_REASON.MINEFIELD_EQ) if primary else self.isSecondaryAttackReason(ATTACK_REASON.MINEFIELD_EQ)

    def isAttackReason(self, attackReason):
        return ATTACK_REASONS[self.__attackReasonID] == attackReason

    def isSecondaryAttackReason(self, attackReason):
        return ATTACK_REASONS[self.__secondaryAttackReasonID] == attackReason

    def isRoleAction(self):
        return self.__isRoleAction


class _VisibilityExtra(object):
    __slots__ = ('__isVisible', '__isDirect', '__isRoleAction')

    def __init__(self, isVisible, isDirect, isRoleAction):
        super(_VisibilityExtra, self).__init__()
        self.__isVisible = isVisible
        self.__isDirect = isDirect
        self.__isRoleAction = bool(isRoleAction)
        _logger.debug('_VisibilityExtra isRoleAction = %s', isRoleAction)

    def isVisible(self):
        return self.__isVisible

    def isDirect(self):
        return self.__isDirect

    def isRoleAction(self):
        return self.__isRoleAction


class _MultiStunExtra(object):
    __slots__ = ('__targetsAmount', '__isRoleAction')

    def __init__(self, targetsAmount, isRoleAction):
        super(_MultiStunExtra, self).__init__()
        self.__targetsAmount = targetsAmount
        self.__isRoleAction = bool(isRoleAction)
        _logger.debug('_StunExtra isRoleAction = %s', isRoleAction)

    def getTargetsAmount(self):
        return self.__targetsAmount

    def isRoleAction(self):
        return self.__isRoleAction


class _CritsExtra(object):
    __slots__ = ('__critsCount', '__shellType', '__isShellGold', '__attackReasonID', '__secondaryAttackReasonID')

    def __init__(self, critsCount=0, attackReasonID=0, shellTypeID=NONE_SHELL_TYPE, shellIsGold=False, secondaryAttackReasonID=0):
        super(_CritsExtra, self).__init__()
        self.__critsCount = critsCount
        self.__attackReasonID = attackReasonID
        self.__shellType = _getShellType(shellTypeID)
        self.__isShellGold = bool(shellIsGold)
        self.__secondaryAttackReasonID = secondaryAttackReasonID

    def getCritsCount(self):
        return self.__critsCount

    def getShellType(self):
        return self.__shellType

    def isShellGold(self):
        return self.__isShellGold

    def isFire(self):
        return self.isAttackReason(ATTACK_REASON.FIRE)

    def isRam(self):
        return self.isAttackReason(ATTACK_REASON.RAM)

    def isShot(self):
        return self.isAttackReason(ATTACK_REASON.SHOT)

    def isWorldCollision(self):
        return self.isAttackReason(ATTACK_REASON.WORLD_COLLISION)

    def isProtectionZone(self, primary=True):
        return self.isAttackReason(ATTACK_REASON.ARTILLERY_PROTECTION) or self.isAttackReason(ATTACK_REASON.ARTILLERY_SECTOR) if primary else self.isSecondaryAttackReason(ATTACK_REASON.ARTILLERY_PROTECTION) or self.isSecondaryAttackReason(ATTACK_REASON.ARTILLERY_SECTOR)

    def isArtilleryEq(self, primary=True):
        return self.isAttackReason(ATTACK_REASON.ARTILLERY_EQ) if primary else self.isSecondaryAttackReason(ATTACK_REASON.ARTILLERY_EQ)

    def isBomberEq(self, primary=True):
        return self.isAttackReason(ATTACK_REASON.BOMBER_EQ) if primary else self.isSecondaryAttackReason(ATTACK_REASON.BOMBER_EQ)

    def isBombers(self, primary=True):
        return self.isAttackReason(ATTACK_REASON.BOMBERS) if primary else self.isSecondaryAttackReason(ATTACK_REASON.BOMBERS)

    def isEventPhaseChange(self, primary=True):
        return self.isAttackReason(ATTACK_REASON.EVENT_DEATH_ON_PHASE_CHANGE) or self.isAttackReason(ATTACK_REASON.EVENT_DEATH_ON_PHASE_CHANGE_FULL_SC) if primary else self.isSecondaryAttackReason(ATTACK_REASON.EVENT_DEATH_ON_PHASE_CHANGE) or self.isSecondaryAttackReason(ATTACK_REASON.EVENT_DEATH_ON_PHASE_CHANGE_FULL_SC)

    def isDeathZone(self, primary=True):
        return self.isAttackReason(ATTACK_REASON.PERSONAL_DEATH_ZONE) or self.isAttackReason(ATTACK_REASON.DEATH_ZONE) if primary else self.isSecondaryAttackReason(ATTACK_REASON.PERSONAL_DEATH_ZONE) or self.isSecondaryAttackReason(ATTACK_REASON.DEATH_ZONE)

    def isMinefield(self, primary=True):
        return self.isAttackReason(ATTACK_REASON.MINEFIELD_EQ) if primary else self.isSecondaryAttackReason(ATTACK_REASON.MINEFIELD_EQ)

    def isSecondaryAttackReason(self, attackReason):
        return ATTACK_REASONS[self.__secondaryAttackReasonID] == attackReason

    def isAttackReason(self, attackReason):
        return ATTACK_REASONS[self.__attackReasonID] == attackReason


class _FeedbackEvent(object):
    __slots__ = ('__eventType',)

    def __init__(self, feedbackEventType):
        super(_FeedbackEvent, self).__init__()
        self.__eventType = feedbackEventType

    def getType(self):
        return self.__eventType

    @staticmethod
    def fromDict(summaryData):
        raise NotImplementedError


class PlayerFeedbackEvent(_FeedbackEvent):
    __slots__ = ('__battleEventType', '__targetID', '__count', '__extra', '__attackReasonID', '__isBurst')

    def __init__(self, feedbackEventType, eventType, targetID, extra, count):
        super(PlayerFeedbackEvent, self).__init__(feedbackEventType)
        self.__battleEventType = eventType
        self.__targetID = targetID
        self.__count = count
        self.__extra = extra

    @staticmethod
    def fromDict(battleEventData):
        battleEventType = battleEventData['eventType']
        if battleEventType in _BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT:
            feedbackEventType = _BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT[battleEventType]
            if feedbackEventType in _PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS:
                converter = _PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS[feedbackEventType]
                extra = converter(battleEventData['details'])
            else:
                extra = None
            return PlayerFeedbackEvent(feedbackEventType, battleEventData['eventType'], battleEventData['targetID'], extra, battleEventData['count'])
        else:
            return

    def getBattleEventType(self):
        return self.__battleEventType

    def getTargetID(self):
        return self.__targetID

    def getExtra(self):
        return self.__extra

    def getCount(self):
        return self.__count


class BattleSummaryFeedbackEvent(_FeedbackEvent):
    __slots__ = ('__damage', '__trackAssistDamage', '__radioAssistDamage', '__blockedDamage', '__stunAssist')

    def __init__(self, damage, trackAssist, radioAssist, tankings, stunAssist):
        super(BattleSummaryFeedbackEvent, self).__init__(_FET.DAMAGE_LOG_SUMMARY)
        self.__damage = damage
        self.__trackAssistDamage = trackAssist
        self.__radioAssistDamage = radioAssist
        self.__blockedDamage = tankings
        self.__stunAssist = stunAssist

    @staticmethod
    def fromDict(summaryData):
        return BattleSummaryFeedbackEvent(damage=summaryData['damage'], trackAssist=summaryData['trackAssist'], radioAssist=summaryData['radioAssist'], tankings=summaryData['tankings'], stunAssist=summaryData['stunAssist'])

    def getTotalDamage(self):
        return self.__damage

    def getTotalAssistDamage(self):
        return self.__trackAssistDamage + self.__radioAssistDamage

    def getTotalBlockedDamage(self):
        return self.__blockedDamage

    def getTotalStunDamage(self):
        return self.__stunAssist


class PostmortemSummaryEvent(_FeedbackEvent):
    __slots__ = ('__killerID', '__deathReasonID')

    def __init__(self, lastKillerID, lastDeathReasonID):
        super(PostmortemSummaryEvent, self).__init__(_FET.POSTMORTEM_SUMMARY)
        self.__killerID = lastKillerID
        self.__deathReasonID = lastDeathReasonID

    @staticmethod
    def fromDict(summaryData):
        return PostmortemSummaryEvent(lastKillerID=summaryData['lastKillerID'], lastDeathReasonID=summaryData['lastDeathReasonID'])

    def getKillerID(self):
        return self.__killerID

    def getDeathReasonID(self):
        return self.__deathReasonID
