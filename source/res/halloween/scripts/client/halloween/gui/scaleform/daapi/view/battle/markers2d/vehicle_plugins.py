# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/markers2d/vehicle_plugins.py
from __future__ import absolute_import
import BigWorld
from HWTeamInfoStatsComponent import HWTeamInfoStatsComponent
from HWArenaInfoBossHealthBarComponent import getArenaInfoBossHealthBarComponent
from HWArenaPhasesComponent import HWArenaPhasesComponent
from constants import ATTACK_REASONS
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.settings import DamageType
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID, FEEDBACK_EVENT_ID
from gui.battle_control.battle_constants import MARKER_DEFAULT_HIT_STATES
from halloween.gui.hw_vehicle_role_helper import getVehicleRole
from gui.impl.gen import R
from gui.impl import backport
from halloween_common.halloween_constants import BOSS_ROLE_TAG, PLAYERS_TEAM
_STUN_EFFECT_DURATION = 1000
_STUN_STATE = 0
_HIT_STATE = MARKER_DEFAULT_HIT_STATES[FEEDBACK_EVENT_ID.VEHICLE_HIT]
BOSS_MARKER_ROLE = 'hwboss'
BOSS_ROLE = 'boss'
VEHICLE_MARKER = 'HWVehicleMarkerUI'

class HalloweenVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin):
    ICON_HIT_BLOCKED = 'hit_blocked'

    def init(self, *args):
        super(HalloweenVehicleMarkerPlugin, self).init()
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onBossHealthChanged += self._onBossHealthChanged
            hwBattleGuiCtrl.onBossAuraVictimMarkerIcon += self.__onAuraVictimMarkerIcon
            hwBattleGuiCtrl.onVehicleBuffIconAdded += self.__onVehicleBuffIconAdded
            hwBattleGuiCtrl.onVehicleBuffIconRemoved += self.__onVehicleBuffIconRemoved
            hwBattleGuiCtrl.onVehicleMaxHealthChanged += self.__onVehicleMaxHealthChanged
            hwBattleGuiCtrl.onPhaseTimeChangedNotification += self.__onPhaseTimeChangedNotification
        HWArenaPhasesComponent.onBossVulnerableChanged += self.__onBossVulnerableChanged
        arenaPhases = HWArenaPhasesComponent.getInstance()
        self.__isBossVulnerable = bool(arenaPhases.isBossVulnerable) if arenaPhases else False

    def fini(self):
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onBossHealthChanged -= self._onBossHealthChanged
            hwBattleGuiCtrl.onBossAuraVictimMarkerIcon -= self.__onAuraVictimMarkerIcon
            hwBattleGuiCtrl.onVehicleBuffIconAdded -= self.__onVehicleBuffIconAdded
            hwBattleGuiCtrl.onVehicleBuffIconRemoved -= self.__onVehicleBuffIconRemoved
            hwBattleGuiCtrl.onVehicleMaxHealthChanged -= self.__onVehicleMaxHealthChanged
            hwBattleGuiCtrl.onPhaseTimeChangedNotification -= self.__onPhaseTimeChangedNotification
        HWArenaPhasesComponent.onBossVulnerableChanged -= self.__onBossVulnerableChanged
        super(HalloweenVehicleMarkerPlugin, self).fini()

    @property
    def vehicleStats(self):
        return HWTeamInfoStatsComponent.getInstance()

    @property
    def hwBattleGuiCtrl(self):
        return self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    def invalidateVehicleStatus(self, flags, vInfoVO, arenaDP):
        vehID = vInfoVO.vehicleID
        if vInfoVO.team == PLAYERS_TEAM or vInfoVO.isAlive() or BigWorld.entities.get(vehID) is not None:
            return
        else:
            self._destroyVehicleMarker(vehID)
            return

    def _hideVehicleMarker(self, vehicleID):
        vInfo = self.sessionProvider.getArenaDP().getVehicleInfo(vehicleID)
        needDestroyMarker = not vInfo or vInfo.team != PLAYERS_TEAM and not vInfo.isAlive()
        if needDestroyMarker:
            self._destroyVehicleMarker(vehicleID)
        else:
            super(HalloweenVehicleMarkerPlugin, self)._hideVehicleMarker(vehicleID)

    def _getMarkerSymbol(self, vehicleID):
        return VEHICLE_MARKER

    def _restoreMarker(self, marker, vProxy, vInfo, guiProps):
        super(HalloweenVehicleMarkerPlugin, self)._restoreMarker(marker, vProxy, vInfo, guiProps)
        if marker.isAlive():
            self._setMarkerBoundEnabled(marker.getMarkerID(), True)
        else:
            self._updateMarkerState(marker.getMarkerID(), 'dead', True, '')
            self._setMarkerBoundEnabled(marker.getMarkerID(), False)
            hwBattleGuiCtrl = self.hwBattleGuiCtrl
            if hwBattleGuiCtrl and hwBattleGuiCtrl.isVehicleHidden(vInfo.vehicleID):
                self._hideVehicleMarker(vehicleID=vInfo.vehicleID)

    def _setHealthMarker(self, vehicleID, handle, newHealth):
        super(HalloweenVehicleMarkerPlugin, self)._setHealthMarker(vehicleID, handle, newHealth)
        self.__updateBossMarkerHealth(vehicleID, handle)

    def _updateHealthMarker(self, vehicleID, handle, newHealth, *args):
        component = getArenaInfoBossHealthBarComponent()
        if not component or not component.isActive or vehicleID not in component.bossVehicleIDs:
            super(HalloweenVehicleMarkerPlugin, self)._updateHealthMarker(vehicleID, handle, newHealth, *args)

    def _onBossHealthChanged(self, newHealth, prevHealth, bossVehicleID, attackerID, attackReasonID):
        if newHealth == prevHealth:
            return
        component = getArenaInfoBossHealthBarComponent()
        bossHealth, _ = component.getBossCurrentLifeHealthValues()
        for bossID in component.bossVehicleIDs:
            if bossID in self._markers:
                bossHandle = self._markers[bossID].getMarkerID()
                attackReason = ATTACK_REASONS[attackReasonID] if bossVehicleID == bossID else ATTACK_REASONS[0]
                vDamageType = DamageType.FROM_PLAYER if attackerID != bossID else DamageType.FROM_OTHER
                attackerInfo = self.sessionProvider.getArenaDP().getVehicleInfo(attackerID)
                super(HalloweenVehicleMarkerPlugin, self)._updateHealthMarker(bossID, bossHandle, bossHealth, vDamageType, attackReason, self._getImprovedRammingAnimationDamage(attackerInfo))

    def _getVehicleClassTag(self, vInfo):
        role = getVehicleRole(vInfo.vehicleType)
        if role is not None:
            if role != BOSS_ROLE:
                return role
            return BOSS_MARKER_ROLE
        else:
            return super(HalloweenVehicleMarkerPlugin, self)._getVehicleClassTag(vInfo)

    def _getVehicleName(self, nameParts, vInfo):
        return vInfo.vehicleType.shortNameWithPrefix if not vInfo.player.isBot else vInfo.vehicleType.name

    def _setVehicleInfoMarker(self, vehicleID, handle, *args):
        super(HalloweenVehicleMarkerPlugin, self)._setVehicleInfoMarker(vehicleID, handle, *args)
        self.__updateBossMarkerHealth(vehicleID, handle)

    def _onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        super(HalloweenVehicleMarkerPlugin, self)._onVehicleFeedbackReceived(eventID, vehicleID, value)
        if eventID == FEEDBACK_EVENT_ID.HW_VEHICLE_MARKER_HEALTH and vehicleID in self._markers:
            self.__updateBossMarkerHealth(vehicleID, self._markers[vehicleID].getMarkerID())
        elif eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD and self.__isVehicleBoss(vehicleID) and not self.__isBossVulnerable:
            self._hideVehicleMarker(vehicleID)

    def _updateMarkerState(self, handle, newState, immediate, text='', iconAnimation='', isFrequent=False):
        if self.__isBossMarker(handle) and not self.__isBossVulnerable:
            if newState == MARKER_DEFAULT_HIT_STATES[FEEDBACK_EVENT_ID.VEHICLE_ARMOR_PIERCED][0]:
                text = backport.text(R.strings.ingame_gui.hitMarker.useless())
                iconAnimation = self.ICON_HIT_BLOCKED
            elif newState == MARKER_DEFAULT_HIT_STATES[FEEDBACK_EVENT_ID.VEHICLE_HIT][0]:
                text = backport.text(R.strings.ingame_gui.hitMarker.useless())
        super(HalloweenVehicleMarkerPlugin, self)._updateMarkerState(handle, newState, immediate, text, iconAnimation, isFrequent)

    def _setMarkerInitialState(self, marker, vInfo):
        super(HalloweenVehicleMarkerPlugin, self)._setMarkerInitialState(marker, vInfo)
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            vID = vInfo.vehicleID
            for icon, priority in hwBattleGuiCtrl.vehicleMarkerIcons.get(vID, []):
                self.__onVehicleBuffIconAdded(vID, icon, priority)

    def __isBossMarker(self, markerID):
        for vehicleID, marker in self._markers.items():
            if marker.getMarkerID() == markerID:
                return self.__isVehicleBoss(vehicleID)

        return False

    def __isVehicleBoss(self, vehicleID):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is None:
            return False
        else:
            return True if BOSS_ROLE_TAG in vehicle.typeDescriptor.type.tags else False

    def __onAuraVictimMarkerIcon(self, vehicle, show):
        vehicleId = vehicle.id
        if vehicleId in self._markers:
            animated = True
            isSourceVehicle = True
            handle = self._markers[vehicleId].getMarkerID()
            self._updateStatusMarkerState(vehicleId, show, handle, _STUN_STATE, _STUN_EFFECT_DURATION, animated, isSourceVehicle)

    def __onVehicleBuffIconAdded(self, vehicleId, icon, priority):
        marker = self._markers.get(vehicleId)
        if marker is not None:
            self._invokeMarker(marker.getMarkerID(), 'showEnemyBuff', icon, priority)
        return

    def __onVehicleBuffIconRemoved(self, vehicleId, icon, priority):
        marker = self._markers.get(vehicleId)
        if marker is not None:
            self._invokeMarker(marker.getMarkerID(), 'removeEnemyBuff', icon, priority)
        return

    def __onBossVulnerableChanged(self, isVulnerable):
        self.__isBossVulnerable = isVulnerable
        component = getArenaInfoBossHealthBarComponent()
        if component is not None:
            for bossID in component.bossVehicleIDs:
                if bossID in self._markers:
                    bossHandle = self._markers[bossID].getMarkerID()
                    self.__updateBossMarkerHealth(bossID, bossHandle)

        return

    def __updateBossMarkerHealth(self, vehicleID, handle):
        if not self.__isVehicleBoss(vehicleID):
            return
        else:
            if self.__isBossVulnerable:
                component = getArenaInfoBossHealthBarComponent()
                if component is not None:
                    currentHealth, maxHealth = component.getBossCurrentLifeHealthValues()
                    self._invokeMarker(handle, 'setMaxHealth', maxHealth)
                    self._invokeMarker(handle, 'setHealth', currentHealth)
                    self._invokeMarker(handle, 'setBossMode', True)
            else:
                self._invokeMarker(handle, 'setBossMode', False)
            return

    def __onVehicleMaxHealthChanged(self, vehicleId, maxHealth):
        arenaDP = self.sessionProvider.getArenaDP()
        vInfo = arenaDP.getVehicleInfo(vehicleId)
        marker = self._markers.get(vehicleId)
        if marker and vInfo:
            getProps = arenaDP.getPlayerGuiProps
            getParts = self.sessionProvider.getCtx().getPlayerFullNameParts
            self._setVehicleInfo(marker, vInfo, getProps(vehicleId, vInfo.team), getParts(vehicleId))

    def __onPhaseTimeChangedNotification(self, looterID, ownerID, amount):
        marker = self._markers.get(ownerID)
        if marker is not None:
            text = backport.text(R.strings.halloween_battle.marker.phaseTime(), time=str(amount))
            self._invokeMarker(marker.getMarkerID(), 'addPhaseTime', text)
        return
