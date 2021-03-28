# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/hit_direction_ctrl/pulls.py
import math
from functools import partial
import BigWorld
from account_helpers.settings_core.settings_constants import DAMAGE_INDICATOR
from gui import GUI_SETTINGS
from gui.battle_control.battle_constants import HIT_FLAGS, HIT_INDICATOR_MAX_ON_SCREEN
from gui.battle_control.battle_constants import PREDICTION_INDICATOR_MAX_ON_SCREEN
from gui.battle_control.controllers.hit_direction_ctrl.base import HitDirection
from helpers import dependency
from math_utils import almostZero
from skeletons.account_helpers.settings_core import ISettingsCore
_AGGREGATED_HIT_BITS = HIT_FLAGS.IS_BLOCKED | HIT_FLAGS.HP_DAMAGE | HIT_FLAGS.IS_CRITICAL

class BaseHitPull(object):
    __slots__ = ('_pull', '__callbackIDs', '__postponedHits')

    def __init__(self):
        self._pull = self._createPull()
        self.__callbackIDs = {}
        self.__postponedHits = []

    def getHit(self, idx):
        if idx < len(self._pull):
            hit = self._pull[idx]
        else:
            hit = None
        return hit

    def addHit(self, hitData):
        if not self.isValidHit(hitData):
            return
        else:
            hit = self.findHit(hitData)
            if hit is None:
                extendHitData = False
                hit = self.getNextHit()
            else:
                extendHitData = hit.isShown()
            idx = hit.getIndex()
            self.clearHideCallback(idx)
            duration = hit.show(hitData, extend=extendHitData)
            if duration:
                self.__callbackIDs[idx] = BigWorld.callback(duration, partial(self._tickToHideHit, idx))
            return hit

    def setIndicator(self, indicatorProxy):
        for hit in self._pull:
            idx = hit.getIndex()
            duration = hit.setIndicator(indicatorProxy)
            if duration:
                self.__callbackIDs[idx] = BigWorld.callback(duration, partial(self._tickToHideHit, idx))

    def clear(self):
        for hit in self._pull:
            hit.clear()

    def isValidHit(self, hitData):
        return True

    def hideAllHits(self):
        for hit in self._pull:
            hit.hide()

        self.__postponedHits = []

    def getNextHit(self):
        find = self._pull[0]
        for hit in self._pull:
            if not hit.isShown():
                return hit
            if hit.getStartTime() < find.getStartTime():
                find = hit

        return find

    def findHit(self, hitData):
        for hit in self._pull:
            data = hit.getHitData()
            if data is not None and self._compareHits(data, hitData):
                return hit

        return

    def hideHit(self, idx):
        self.clearHideCallback(idx)
        self._tickToHideHit(idx)

    def clearHideCallback(self, idx):
        callbackID = self.__callbackIDs.pop(idx, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        return

    def clearHideCallbacks(self):
        for _, callbackID in self.__callbackIDs.items():
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        self.__callbackIDs.clear()
        return

    def invalidateSettings(self, diff):
        pass

    def redraw(self):
        for hit in self._pull:
            hit.redraw()

    def postponedHit(self, hitData):
        data = self.findPostponedHit(hitData)
        if data is None:
            self.__postponedHits.append(hitData)
        return

    def removePostponedHit(self, hitData):
        data = self.findPostponedHit(hitData)
        if data is not None:
            self.__postponedHits.pop(data[1])
        return

    def hitNeedPostponed(self, hitData):
        return False

    def findPostponedHit(self, hitData):
        for idx, hit in enumerate(self.__postponedHits):
            if self._compareHits(hit, hitData):
                return (hit, idx)

        return None

    def _tickToHideHit(self, idx):
        self.__callbackIDs.pop(idx, None)
        self._pull[idx].hide()
        self.__tryShowPostponedHit()
        return

    def _compareHits(self, hitData, newHitData):
        return False

    def _createPull(self):
        raise NotImplementedError

    def __tryShowPostponedHit(self):
        newQueue = []
        for hit in self.__postponedHits:
            if self.hitNeedPostponed(hit):
                newQueue.append(hit)
            self.addHit(hit)

        self.__postponedHits = newQueue


class HitDamagePull(BaseHitPull):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(HitDamagePull, self).__init__()
        self.__damageIndicatorExtType = False
        self.__damageIndicatorCrits = False
        self.__damageIndicatorAllies = False

    def setIndicator(self, indicatorProxy):
        self.__damageIndicatorExtType = bool(self.settingsCore.getSetting(DAMAGE_INDICATOR.TYPE))
        self.__damageIndicatorCrits = bool(self.settingsCore.getSetting(DAMAGE_INDICATOR.PRESET_CRITS))
        self.__damageIndicatorAllies = bool(self.settingsCore.getSetting(DAMAGE_INDICATOR.PRESET_ALLIES))
        super(HitDamagePull, self).setIndicator(indicatorProxy)

    def isValidHit(self, hitData):
        if hitData.isNonPlayerAttackReason() or hitData.isBattleAbilityConsumable() or hitData.isBattleConsumables():
            return False
        isCriticalNoDamage = hitData.isCritical() and hitData.getDamage() == 0
        if self.__damageIndicatorExtType and not self.__damageIndicatorCrits and isCriticalNoDamage:
            return False
        return False if self.__damageIndicatorExtType and not self.__damageIndicatorAllies and hitData.isFriendlyFire() else True

    def _compareHits(self, hitData, newHitData):
        if newHitData.getAttackerID() == hitData.getAttackerID():
            currentMask = hitData.getHitFlags() & _AGGREGATED_HIT_BITS
            newMask = newHitData.getHitFlags() & _AGGREGATED_HIT_BITS
            if currentMask > 0:
                if currentMask == newMask:
                    return True
                if currentMask == HIT_FLAGS.HP_DAMAGE and newMask == HIT_FLAGS.HP_DAMAGE | HIT_FLAGS.IS_CRITICAL:
                    return True
                if currentMask == HIT_FLAGS.HP_DAMAGE | HIT_FLAGS.IS_CRITICAL and newMask == HIT_FLAGS.HP_DAMAGE:
                    return True
        return False

    def invalidateSettings(self, diff):
        if DAMAGE_INDICATOR.TYPE in diff:
            self.__damageIndicatorExtType = bool(diff[DAMAGE_INDICATOR.TYPE])
        if DAMAGE_INDICATOR.PRESET_CRITS in diff:
            self.__damageIndicatorCrits = bool(diff[DAMAGE_INDICATOR.PRESET_CRITS])
        if DAMAGE_INDICATOR.PRESET_ALLIES in diff:
            self.__damageIndicatorAllies = bool(diff[DAMAGE_INDICATOR.PRESET_ALLIES])

    def _createPull(self):
        return [ HitDirection(idx_) for idx_ in xrange(HIT_INDICATOR_MAX_ON_SCREEN) ]


class ArtyHitPredictionPull(BaseHitPull):
    __slots__ = ('__angleDelta',)

    def __init__(self):
        super(ArtyHitPredictionPull, self).__init__()
        self.__angleDelta = math.radians(GUI_SETTINGS.spgHitDirectionDelta)

    def _compareHits(self, hitData, newHitData):
        return almostZero(hitData.getYaw() - newHitData.getYaw(), epsilon=0.0001)

    def hitNeedPostponed(self, hitData):
        return any((abs(hitData.getYaw() - hit.getHitData().getYaw()) <= self.__angleDelta for hit in self._pull if hit.getHitData() is not None and hit.isShown()))

    def _createPull(self):
        return [ HitDirection(idx_) for idx_ in xrange(PREDICTION_INDICATOR_MAX_ON_SCREEN) ]
