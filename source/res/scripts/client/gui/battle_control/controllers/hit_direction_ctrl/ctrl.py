# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/hit_direction_ctrl/ctrl.py
import logging
import weakref
import typing
from account_helpers.settings_core import settings_constants
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import HIT_INDICATOR_MAX_ON_SCREEN, BATTLE_CTRL_ID
from gui.battle_control.controllers.hit_direction_ctrl.base import HitType
from gui.battle_control.controllers.hit_direction_ctrl.components import BaseHitComponent, HitDamageComponent
from gui.battle_control.controllers.hit_direction_ctrl.pulls import HitDamagePull, ArtyHitPredictionPull
from gui.battle_control.controllers.hit_direction_ctrl.hit_data import HitData, SimpleHitData
from gui.battle_control.view_components import IViewComponentsController
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class HitDirectionController(IViewComponentsController):
    __slots__ = ('__uiHitComponents', '__isVisible', '__callbackIDs', '__damageIndicatorCrits', '__damageIndicatorAllies', '__damageIndicatorExtType', '__arenaDP', '__weakref__')
    settingsCore = dependency.descriptor(ISettingsCore)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, setup):
        super(HitDirectionController, self).__init__()
        self.__uiHitComponents = {HitType.HIT_DAMAGE: HitDamageComponent(HitDamagePull()),
         HitType.ARTY_HIT_PREDICTION: BaseHitComponent(ArtyHitPredictionPull())}
        self.__isVisible = False
        self.__arenaDP = weakref.proxy(setup.arenaDP)

    def getControllerID(self):
        return BATTLE_CTRL_ID.HIT_DIRECTION

    def startControl(self):
        g_eventBus.addListener(GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
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

    def getHit(self, idx, hitType=HitType.HIT_DAMAGE):
        return self.__uiHitComponents[hitType].pull.getHit(idx)

    def isVisible(self):
        return self.__isVisible

    def setVisible(self, flag):
        self.__isVisible = flag
        for uiComponent in self.__uiHitComponents.itervalues():
            uiComponent.setVisible(self.__isVisible)

    def setViewComponents(self, *components):
        for component in components:
            hitType = component.getHitType()
            if hitType not in self.__uiHitComponents:
                _logger.error('Controller doesnt have the component with hit type(%s)', hitType)
            self.__uiHitComponents[hitType].setUI(component, self.__isVisible)

        handler = avatar_getter.getInputHandler()
        if handler is not None:
            from AvatarInputHandler import AvatarInputHandler
            if isinstance(handler, AvatarInputHandler):
                handler.onPostmortemKillerVisionEnter += self.__onPostmortemKillerVision
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling += self.__onVehicleControlling
        return

    def clearViewComponents(self):
        for uiComponent in self.__uiHitComponents.itervalues():
            uiComponent.clear()

    def addHit(self, hitDirYaw, attackerID, damage, isBlocked, critFlags, isHighExplosive, damagedID, attackReasonID):
        atackerVehInfo = self.__arenaDP.getVehicleInfo(attackerID)
        atackerVehType = atackerVehInfo.vehicleType
        isAlly = self.__arenaDP.isAllyTeam(atackerVehInfo.team)
        playerVehType = self.__arenaDP.getVehicleInfo(damagedID).vehicleType
        hitData = HitData(yaw=hitDirYaw, attackerID=attackerID, isAlly=isAlly, damage=damage, attackerVehName=atackerVehType.shortNameWithPrefix, isBlocked=isBlocked, attackerVehClassTag=atackerVehType.classTag, critFlags=critFlags, playerVehMaxHP=playerVehType.maxHealth, isHighExplosive=isHighExplosive, attackReasonID=attackReasonID, friendlyFireMode=self.__isFriendlyFireMode())
        return self.__uiHitComponents[HitType.HIT_DAMAGE].pull.addHit(hitData)

    def addArtyHitPrediction(self, yaw):
        setting = self.settingsCore.options.getSetting(settings_constants.SOUND.ARTY_SHOT_ALERT_SOUND)
        hitData = SimpleHitData(yaw=yaw, soundName=setting.getEventName())
        pull = self.__uiHitComponents[HitType.ARTY_HIT_PREDICTION].pull
        hit = None
        if pull.hitNeedPostponed(hitData):
            pull.postponedHit(hitData)
        else:
            hit = pull.addHit(hitData)
        return hit

    def removeArtyHitPrediction(self, yaw):
        hitData = SimpleHitData(yaw=yaw)
        pull = self.__uiHitComponents[HitType.ARTY_HIT_PREDICTION].pull
        pull.removePostponedHit(hitData)
        hit = pull.findHit(hitData)
        if hit is not None:
            pull.hideHit(hit.getIndex())
        return

    def artyHitIsPostponed(self, yaw):
        hitData = SimpleHitData(yaw=yaw)
        return self.__uiHitComponents[HitType.ARTY_HIT_PREDICTION].pull.findPostponedHit(hitData) is not None

    def _hideAllHits(self):
        for uiComponent in self.__uiHitComponents.itervalues():
            uiComponent.pull.hideAllHits()

    def __isFriendlyFireMode(self):
        isFriendlyFireMode = self.sessionProvider.arenaVisitor.bonus.isFriendlyFireMode()
        isCustomAllyDamageEffect = self.sessionProvider.arenaVisitor.bonus.hasCustomAllyDamageEffect()
        return isFriendlyFireMode and isCustomAllyDamageEffect

    def __clearHideCallbacks(self):
        for uiComponent in self.__uiHitComponents.itervalues():
            uiComponent.pull.clearHideCallbacks()

    def __handleGUIVisibility(self, event):
        self.setVisible(event.ctx['visible'])

    def __onSettingsChanged(self, diff):
        for uiComponent in self.__uiHitComponents.itervalues():
            uiComponent.invalidateSettings(diff)

    def __onPostmortemKillerVision(self, killerVehicleID):
        if killerVehicleID != self.__arenaDP.getPlayerVehicleID():
            self._hideAllHits()

    def __onVehicleControlling(self, vehicle):
        if self.__arenaDP.getPlayerVehicleID() != self.sessionProvider.shared.vehicleState.getControllingVehicleID():
            self._hideAllHits()


class HitDirectionControllerPlayer(HitDirectionController):

    def stopControl(self):
        self._hideAllHits()
        super(HitDirectionControllerPlayer, self).stopControl()
