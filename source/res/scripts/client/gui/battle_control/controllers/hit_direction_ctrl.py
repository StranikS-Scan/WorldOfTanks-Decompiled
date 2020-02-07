# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/hit_direction_ctrl.py
from functools import partial
import weakref
import BigWorld
from account_helpers.settings_core.settings_constants import DAMAGE_INDICATOR, GRAPHICS
from gui.battle_control.battle_constants import HIT_INDICATOR_MAX_ON_SCREEN, BATTLE_CTRL_ID
from gui.battle_control.view_components import IViewComponentsController
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.battle_control.battle_constants import HIT_FLAGS
from gui.battle_control import avatar_getter
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from gui.battle_control.hit_data import HitData
_AGGREGATED_HIT_BITS = HIT_FLAGS.IS_BLOCKED | HIT_FLAGS.HP_DAMAGE | HIT_FLAGS.IS_CRITICAL
_VISUAL_DAMAGE_INDICATOR_SETTINGS = (DAMAGE_INDICATOR.TYPE,
 DAMAGE_INDICATOR.VEHICLE_INFO,
 DAMAGE_INDICATOR.DAMAGE_VALUE,
 DAMAGE_INDICATOR.ANIMATION,
 GRAPHICS.COLOR_BLIND,
 DAMAGE_INDICATOR.DYNAMIC_INDICATOR,
 DAMAGE_INDICATOR.PRESET_CRITS,
 DAMAGE_INDICATOR.PRESET_ALLIES)

class IHitIndicator(object):

    def destroy(self):
        raise NotImplementedError

    def getDuration(self):
        raise NotImplementedError

    def getBeginAnimationDuration(self):
        raise NotImplementedError

    def setVisible(self, flag):
        raise NotImplementedError

    def showHitDirection(self, idx, hitData, timeLeft):
        raise NotImplementedError

    def hideHitDirection(self, idx):
        raise NotImplementedError


class _HitDirection(object):
    __slots__ = ('__idx', '__hitData', '__isDamage', '__startTime', '__isShown', '__isVisible', '__offset', '__indicator')

    def __init__(self, idx):
        super(_HitDirection, self).__init__()
        self.__idx = idx
        self.__hitData = None
        self.__startTime = 0
        self.__isShown = False
        self.__indicator = None
        return

    def __repr__(self):
        return '_HitDirection(idx={0}, hitData={1}, startTime={2}, isShown={3}, hasUI={4})'.format(self.__idx, self.__hitData, self.__startTime, self.__isShown, self.__indicator is not None)

    def clear(self):
        self.__hitData = None
        self.__startTime = 0
        self.__isShown = False
        self.__indicator = None
        return

    def getIndex(self):
        return self.__idx

    def getHitData(self):
        return self.__hitData

    def isShown(self):
        return self.__isShown

    def getIndicator(self):
        return self.__indicator

    def getTimeLeft(self):
        if self.__isShown:
            timeLeft = BigWorld.time() - self.__startTime
        else:
            timeLeft = 0
        return timeLeft

    def getStartTime(self):
        return self.__startTime

    def setIndicator(self, indicator):
        self.__indicator = indicator
        return self.redraw()

    def redraw(self):
        duration = 0
        if self.__isShown and self.__hitData is not None and self.__indicator is not None:
            timeLeft = BigWorld.time() - self.__startTime
            duration = self.__indicator.getDuration()
            if timeLeft < duration:
                self.__indicator.showHitDirection(self.__idx, self.__hitData, timeLeft)
            else:
                duration = 0
        return duration

    def show(self, hitData, extend=False):
        self.__isShown = True
        self.__startTime = BigWorld.time()
        extend = extend and self.__hitData is not None
        if extend:
            self.__hitData.extend(hitData)
        else:
            self.__hitData = hitData
        if self.__indicator:
            duration = self.__indicator.getDuration()
            timeLeft = self.__indicator.getBeginAnimationDuration() if extend else 0
            self.__indicator.showHitDirection(self.__idx, self.__hitData, timeLeft)
        else:
            duration = 0
        return duration

    def hide(self):
        if not self.__isShown:
            return
        self.__isShown = False
        if self.__indicator:
            self.__indicator.hideHitDirection(self.__idx)


class HitDirectionController(IViewComponentsController):
    __slots__ = ('__pull', '__ui', '__isVisible', '__callbackIDs', '__damageIndicatorCrits', '__damageIndicatorAllies', '__damageIndicatorExtType', '__arenaDP', '__weakref__')
    settingsCore = dependency.descriptor(ISettingsCore)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, setup):
        super(HitDirectionController, self).__init__()
        self.__pull = [ _HitDirection(idx_) for idx_ in xrange(HIT_INDICATOR_MAX_ON_SCREEN) ]
        self.__ui = None
        self.__isVisible = False
        self.__callbackIDs = {}
        self.__damageIndicatorExtType = False
        self.__damageIndicatorCrits = False
        self.__damageIndicatorAllies = False
        self.__arenaDP = weakref.proxy(setup.arenaDP)
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.HIT_DIRECTION

    def startControl(self):
        g_eventBus.addListener(GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__damageIndicatorExtType = bool(self.settingsCore.getSetting(DAMAGE_INDICATOR.TYPE))
        self.__damageIndicatorCrits = bool(self.settingsCore.getSetting(DAMAGE_INDICATOR.PRESET_CRITS))
        self.__damageIndicatorAllies = bool(self.settingsCore.getSetting(DAMAGE_INDICATOR.PRESET_ALLIES))
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged

    def stopControl(self):
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            from AvatarInputHandler import AvatarInputHandler
            if isinstance(handler, AvatarInputHandler):
                handler.onPostmortemKillerVisionEnter -= self.__onPostmortemKillerVision
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling -= self.__onVehicleControlling
        g_eventBus.removeListener(GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__clearHideCallbacks()
        self.__arenaDP = None
        return

    def getContainer(self):
        return self.__ui

    def getHit(self, idx):
        if idx < len(self.__pull):
            hit = self.__pull[idx]
        else:
            hit = None
        return hit

    def isVisible(self):
        return self.__isVisible

    def setVisible(self, flag):
        self.__isVisible = flag
        if self.__ui:
            self.__ui.setVisible(flag)

    def setViewComponents(self, component):
        self.__ui = component
        self.__ui.invalidateSettings()
        self.__ui.setVisible(self.__isVisible)
        proxy = weakref.proxy(self.__ui)
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            from AvatarInputHandler import AvatarInputHandler
            if isinstance(handler, AvatarInputHandler):
                handler.onPostmortemKillerVisionEnter += self.__onPostmortemKillerVision
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling += self.__onVehicleControlling
        for hit in self.__pull:
            idx = hit.getIndex()
            duration = hit.setIndicator(proxy)
            if duration:
                self.__callbackIDs[idx] = BigWorld.callback(duration, partial(self.__tickToHideHit, idx))

        return

    def clearViewComponents(self):
        for hit in self.__pull:
            hit.clear()

        if self.__ui:
            self.__ui.destroy()
        self.__ui = None
        return

    def addHit(self, hitDirYaw, attackerID, damage, isBlocked, critFlags, isHighExplosive, damagedID, attackReasonID):
        atackerVehInfo = self.__arenaDP.getVehicleInfo(attackerID)
        atackerVehType = atackerVehInfo.vehicleType
        isAlly = self.__arenaDP.isAllyTeam(atackerVehInfo.team)
        playerVehType = self.__arenaDP.getVehicleInfo(damagedID).vehicleType
        hitData = HitData(yaw=hitDirYaw, attackerID=attackerID, isAlly=isAlly, damage=damage, attackerVehName=atackerVehType.shortNameWithPrefix, isBlocked=isBlocked, attackerVehClassTag=atackerVehType.classTag, critFlags=critFlags, playerVehMaxHP=playerVehType.maxHealth, isHighExplosive=isHighExplosive, attackReasonID=attackReasonID, friendlyFireMode=self.__isFriendlyFireMode())
        if not self._isValidHit(hitData):
            return
        else:
            hit = self.__findHit(hitData)
            if hit is None:
                extendHitData = False
                hit = self.__getNextHit()
            else:
                extendHitData = hit.isShown()
            idx = hit.getIndex()
            self.__clearHideCallback(idx)
            duration = hit.show(hitData, extend=extendHitData)
            if duration:
                self.__callbackIDs[idx] = BigWorld.callback(duration, partial(self.__tickToHideHit, idx))
            return hit

    def _isValidHit(self, hitData):
        if hitData.isNonPlayerAttackReason() or hitData.isBattleAbilityConsumable() or hitData.isBattleConsumables():
            return False
        isCriticalNoDamage = hitData.isCritical() and hitData.getDamage() == 0
        if self.__damageIndicatorExtType and not self.__damageIndicatorCrits and isCriticalNoDamage:
            return False
        return False if self.__damageIndicatorExtType and not self.__damageIndicatorAllies and hitData.isFriendlyFire() else True

    def _hideAllHits(self):
        for hit in self.__pull:
            hit.hide()

    def __getNextHit(self):
        find = self.__pull[0]
        for hit in self.__pull:
            if not hit.isShown():
                return hit
            if hit.getStartTime() < find.getStartTime():
                find = hit

        return find

    def __isFriendlyFireMode(self):
        friendlyFireBonusTypes = self.lobbyContext.getServerSettings().getFriendlyFireBonusTypes()
        isFriendlyFireMode = self.sessionProvider.arenaVisitor.bonus.isFriendlyFireMode(friendlyFireBonusTypes)
        isCustomAllyDamageEffect = self.sessionProvider.arenaVisitor.bonus.hasCustomAllyDamageEffect()
        return isFriendlyFireMode and isCustomAllyDamageEffect

    def __findHit(self, hitData):
        for hit in self.__pull:
            data = hit.getHitData()
            if data is not None:
                if hitData.getAttackerID() == data.getAttackerID():
                    currentMask = data.getHitFlags() & _AGGREGATED_HIT_BITS
                    newMask = hitData.getHitFlags() & _AGGREGATED_HIT_BITS
                    if currentMask > 0:
                        if currentMask == newMask:
                            return hit
                        if currentMask == HIT_FLAGS.HP_DAMAGE and newMask == HIT_FLAGS.HP_DAMAGE | HIT_FLAGS.IS_CRITICAL:
                            return hit
                        if currentMask == HIT_FLAGS.HP_DAMAGE | HIT_FLAGS.IS_CRITICAL and newMask == HIT_FLAGS.HP_DAMAGE:
                            return hit

        return

    def __tickToHideHit(self, idx):
        self.__callbackIDs.pop(idx, None)
        self.__pull[idx].hide()
        return

    def __clearHideCallback(self, idx):
        callbackID = self.__callbackIDs.pop(idx, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        return

    def __clearHideCallbacks(self):
        for _, callbackID in self.__callbackIDs.items():
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        self.__callbackIDs.clear()
        return

    def __handleGUIVisibility(self, event):
        self.setVisible(event.ctx['visible'])

    def __onSettingsChanged(self, diff):
        if DAMAGE_INDICATOR.TYPE in diff:
            self.__damageIndicatorExtType = bool(diff[DAMAGE_INDICATOR.TYPE])
        if DAMAGE_INDICATOR.PRESET_CRITS in diff:
            self.__damageIndicatorCrits = bool(diff[DAMAGE_INDICATOR.PRESET_CRITS])
        if DAMAGE_INDICATOR.PRESET_ALLIES in diff:
            self.__damageIndicatorAllies = bool(diff[DAMAGE_INDICATOR.PRESET_ALLIES])
        if self.__ui is not None:
            for key in _VISUAL_DAMAGE_INDICATOR_SETTINGS:
                if key in diff:
                    self.__ui.invalidateSettings()
                    for hit in self.__pull:
                        hit.redraw()

                    break

        return

    def __onPostmortemKillerVision(self, killerVehicleID):
        if killerVehicleID != self.__arenaDP.getPlayerVehicleID():
            self._hideAllHits()

    def __onVehicleControlling(self, vehicle):
        if not vehicle.isPlayerVehicle:
            self._hideAllHits()


class HitDirectionControllerPlayer(HitDirectionController):

    def stopControl(self):
        self._hideAllHits()
        super(HitDirectionControllerPlayer, self).stopControl()


def createHitDirectionController(setup):
    return HitDirectionControllerPlayer(setup) if setup.isReplayPlaying else HitDirectionController(setup)
