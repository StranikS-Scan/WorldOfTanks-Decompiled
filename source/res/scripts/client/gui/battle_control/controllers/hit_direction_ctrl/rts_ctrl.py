# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/hit_direction_ctrl/rts_ctrl.py
import BigWorld
from aih_constants import CTRL_MODE_NAME
from helpers import dependency
from AvatarInputHandler import aih_global_binding
from gui.battle_control.controllers.commander.indicators import createRTSHitIndicator
from gui.battle_control.controllers.hit_direction_ctrl.base import HitType
from gui.battle_control.controllers.hit_direction_ctrl.components import HitDamageComponent
from gui.battle_control.controllers.hit_direction_ctrl.pulls import RTSHitPull
from gui.battle_control.controllers.hit_direction_ctrl.ctrl import HitDirectionController
from gui.battle_control.controllers.hit_direction_ctrl.hit_data import RTSHitData
from skeletons.gui.battle_session import IBattleSessionProvider

class RTSHitDirectionController(HitDirectionController):
    __ctrlMode = aih_global_binding.bindRO(aih_global_binding.BINDING_ID.CTRL_MODE_NAME)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, setup):
        super(RTSHitDirectionController, self).__init__(setup)
        self._uiHitComponents[HitType.HIT_DAMAGE] = HitDamageComponent(RTSHitPull())
        self.__isRTSMode = self.__ctrlMode in CTRL_MODE_NAME.COMMANDER_MODES
        self.__rtsIndicator = createRTSHitIndicator()
        self.__classicIndicator = None
        return

    def startControl(self):
        super(RTSHitDirectionController, self).startControl()
        aih_global_binding.subscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self.__onAvatarCtrlModeChanged)

    def stopControl(self):
        aih_global_binding.unsubscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self.__onAvatarCtrlModeChanged)
        super(RTSHitDirectionController, self).stopControl()

    def setViewComponents(self, *components):
        for component in components:
            hitType = component.getHitType()
            self.__classicIndicator = hitType == HitType.HIT_DAMAGE and component
            continue

        super(RTSHitDirectionController, self).setViewComponents(*components)

    def clearViewComponents(self):
        hitDamageIndicators = {self.__rtsIndicator, self.__classicIndicator}
        for uiComponent in self._uiHitComponents.itervalues():
            hitDamageIndicators.discard(uiComponent.ui)
            uiComponent.clear()

        for indicator in hitDamageIndicators:
            if indicator is not None:
                indicator.destroy()

        self.__rtsIndicator = None
        self.__classicIndicator = None
        return

    def addHit(self, hitDirYaw, attackerID, damage, isBlocked, critFlags, isHighExplosive, damagedID, attackReasonID):
        playerAvatar = BigWorld.player()
        if playerAvatar is None or not (damagedID == playerAvatar.currentVehicleID or playerAvatar.isCommander()):
            return
        else:
            attackerVehInfo = self._arenaDP.getVehicleInfo(attackerID)
            attackerVehType = attackerVehInfo.vehicleType
            isAlly = self._arenaDP.isAllyTeam(attackerVehInfo.team)
            playerVehType = self._arenaDP.getVehicleInfo(damagedID).vehicleType
            proxy = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(damagedID)
            if proxy is None or not proxy.isControllable or proxy.isEnemy:
                return
            hitData = RTSHitData(yaw=hitDirYaw, attackerID=attackerID, damagedID=damagedID, isAlly=isAlly, damage=damage, attackerVehName=attackerVehType.shortNameWithPrefix, isBlocked=isBlocked, attackerVehClassTag=attackerVehType.classTag, critFlags=critFlags, playerVehMaxHP=playerVehType.maxHealth, isHighExplosive=isHighExplosive, attackReasonID=attackReasonID, friendlyFireMode=self._isFriendlyFireMode())
            return self._getViewComponent(HitType.HIT_DAMAGE).pull.addHit(hitData)

    def getHit(self, idx, hitType=HitType.HIT_DAMAGE):
        if hitType == HitType.RTS_HIT:
            hitType = HitType.HIT_DAMAGE
        return self._uiHitComponents[hitType].pull.getHit(idx)

    def _updateComponentsVisibility(self):
        super(RTSHitDirectionController, self)._updateComponentsVisibility()
        self._getViewComponent(HitType.ARTY_HIT_PREDICTION).setVisible(not self.__isRTSMode and self.isVisible())

    def __onAvatarCtrlModeChanged(self, ctrlMode):
        isRTSMode = ctrlMode in CTRL_MODE_NAME.COMMANDER_MODES
        if isRTSMode != self.__isRTSMode:
            component = self._getViewComponent(HitType.HIT_DAMAGE)
            component.setVisible(False)
            component.setUI(self.__rtsIndicator if isRTSMode else self.__classicIndicator, self.isVisible())
            self.__isRTSMode = isRTSMode
            self._updateComponentsVisibility()


class RTSHitDirectionControllerPlayer(RTSHitDirectionController):

    def stopControl(self):
        self._hideAllHits()
        super(RTSHitDirectionControllerPlayer, self).stopControl()
