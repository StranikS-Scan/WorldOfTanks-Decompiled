# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/avatar_epic_data.py
import BigWorld
import CommandMapping
import Event
import constants
from aih_constants import CTRL_MODE_NAME
from arena_component_system.sector_base_arena_component import ID_TO_BASENAME, _MISSION_SECTOR_ID_MAPPING
from avatar_helpers import getBestShotResultSound
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
from constants import DEATH_ZONES, SECTOR_STATE, VEHICLE_HIT_FLAGS as VHF
from debug_utils import LOG_DEBUG_DEV
from epic_constants import EPIC_BATTLE_TEAM_ID
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.sounds.epic_sound_constants import EPIC_SOUND
_KB_MAPPING = {'EPIC_GLOBAL_SAVETANKS': CommandMapping.EPIC_GLOBAL_MSG_SAVE_TANKS,
 'EPIC_GLOBAL_TIME': CommandMapping.EPIC_GLOBAL_MSG_TIME,
 'EPIC_GLOBAL_HQ': CommandMapping.EPIC_GLOBAL_MSG_FOCUS_HQ,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_WEST: CommandMapping.EPIC_GLOBAL_MSG_LEFT_LANE,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_CENTER: CommandMapping.EPIC_GLOBAL_MSG_CENTER_LANE,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_EAST: CommandMapping.EPIC_GLOBAL_MSG_RIGHT_LANE}
_COMMAND_TO_LANE_MAPPING = {BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_WEST: 1,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_CENTER: 2,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_EAST: 3}
_ATTACKER_POSTFIX = '_ATK'
_DEFENDER_POSTFIX = '_DEF'

class AvatarEpicData(object):

    def __init__(self):
        self.__lastPlayerSectorGroupID = None
        self.__isCurrentPlayerSectorGroupAllowed = True
        self.__lastTimerTypeForSectorGroup = {}
        self.__playerUnderFire = False
        self.__frontLineDevInfoEnabled = False
        return

    def onBecomePlayer(self):
        if constants.IS_DEVELOPMENT:
            self.__devEvtManager = Event.EventManager()
            self.onFrontLineInfoUpdated = Event.Event(self.__devEvtManager)

    def handleKey(self, isDown, key, mods):
        cmdMap = CommandMapping.g_instance
        return self.__sendGlobalChatCmdIfPossible(key) if cmdMap.isFiredList((CommandMapping.EPIC_GLOBAL_MSG_SAVE_TANKS,
         CommandMapping.EPIC_GLOBAL_MSG_TIME,
         CommandMapping.EPIC_GLOBAL_MSG_LEFT_LANE,
         CommandMapping.EPIC_GLOBAL_MSG_CENTER_LANE,
         CommandMapping.EPIC_GLOBAL_MSG_RIGHT_LANE,
         CommandMapping.EPIC_GLOBAL_MSG_FOCUS_HQ), key) and isDown else False

    def onBecomeNonPlayer(self):
        if constants.IS_DEVELOPMENT:
            self.__devEvtManager.clear()

    def showDestructibleShotResults(self, destructibleEntityID, hitFlagsList):
        LOG_DEBUG_DEV('showDestructibleShotResults', destructibleEntityID, hitFlagsList)
        if self.arena.componentSystem and hasattr(self.arena.componentSystem, 'destructibleEntityComponent'):
            destructibleComp = self.arena.componentSystem.destructibleEntityComponent
        if destructibleComp:
            destructibleObj = destructibleComp.getDestructibleEntity(destructibleEntityID)
            if destructibleObj is None or self.team == destructibleObj.team:
                return
        else:
            return
        bestSoundsSequence = None
        for hitFlags in hitFlagsList:
            if hitFlags & VHF.VEHICLE_KILLED or hitFlags & VHF.VEHICLE_WAS_DEAD_BEFORE_ATTACK:
                return
            sound = None
            if hitFlags & VHF.ATTACK_IS_EXTERNAL_EXPLOSION:
                if hitFlags & VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_EXPLOSION:
                    sound = 'enemy_hp_damaged_by_near_explosion_by_player'
                elif hitFlags & VHF.IS_ANY_PIERCING_MASK:
                    sound = 'enemy_no_hp_damage_by_near_explosion_by_player'
            elif hitFlags & VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_PROJECTILE:
                if hitFlags & (VHF.GUN_DAMAGED_BY_PROJECTILE | VHF.GUN_DAMAGED_BY_EXPLOSION):
                    sound = 'enemy_hp_damaged_by_projectile_and_gun_damaged_by_player'
                elif hitFlags & (VHF.CHASSIS_DAMAGED_BY_PROJECTILE | VHF.CHASSIS_DAMAGED_BY_EXPLOSION):
                    sound = 'enemy_hp_damaged_by_projectile_and_chassis_damaged_by_player'
                else:
                    sound = 'enemy_hp_damaged_by_projectile_by_player'
            elif hitFlags & VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_EXPLOSION:
                sound = 'enemy_hp_damaged_by_explosion_at_direct_hit_by_player'
            elif hitFlags & VHF.RICOCHET and not hitFlags & VHF.DEVICE_PIERCED_BY_PROJECTILE:
                sound = 'enemy_ricochet_by_player'
            elif hitFlags & VHF.MATERIAL_WITH_POSITIVE_DF_NOT_PIERCED_BY_PROJECTILE:
                sound = 'enemy_no_hp_damage_at_attempt_by_player'
            elif hitFlags & VHF.IS_ANY_PIERCING_MASK:
                sound = 'enemy_no_hp_damage_at_no_attempt_by_player'
            else:
                sound = 'enemy_no_piercing_by_player'
            if sound is not None:
                bestSoundsSequence = getBestShotResultSound(bestSoundsSequence, sound, None)

        if bestSoundsSequence is not None:
            self.soundNotifications.play(bestSoundsSequence[0])
        return

    def onDestructibleDestroyed(self, destructibleEntityID, shooterID):
        self.guiSessionProvider.shared.messages.showDestructibleEntityDestroyedMessage(self, destructibleEntityID, shooterID)

    def welcomeToSector(self, sectorID, groupID, groupState, goodGroup, actionTime, actionDuration):
        entered = groupID != self.__lastPlayerSectorGroupID
        deathZoneTimerType = None
        diffTime = actionTime - BigWorld.serverTime()
        playerUnderFire = False
        state = 'critical'
        if (groupState == SECTOR_STATE.TRANSITION or groupState == SECTOR_STATE.BOMBING) and not goodGroup:
            deathZoneTimerType = DEATH_ZONES.SECTOR_AIRSTRIKE
            if groupState == SECTOR_STATE.BOMBING:
                diffTime = actionDuration
                entered = True
                state = 'warning'
                actionDuration = 0
        elif groupState == SECTOR_STATE.CLOSED and not goodGroup:
            playerUnderFire = True
        ctrlMode = self.inputHandler.ctrlModeName
        if self.__playerUnderFire != playerUnderFire or ctrlMode == CTRL_MODE_NAME.POSTMORTEM:
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.UNDER_FIRE, playerUnderFire)
            self.__playerUnderFire = playerUnderFire
        deathZoneTimerEnabled = self.inputHandler.ctrlModeName not in (CTRL_MODE_NAME.DEATH_FREE_CAM, CTRL_MODE_NAME.RESPAWN_DEATH)
        lastDeathZoneTimer = self.__lastTimerTypeForSectorGroup.get(self.__lastPlayerSectorGroupID, None)
        if lastDeathZoneTimer is not None and deathZoneTimerType != lastDeathZoneTimer:
            self.updateVehicleDeathZoneTimer(0, lastDeathZoneTimer, entered, state=state)
            self.__lastTimerTypeForSectorGroup[self.__lastPlayerSectorGroupID] = None
        if deathZoneTimerType is not None and diffTime > 0 and deathZoneTimerEnabled:
            self.updateVehicleDeathZoneTimer(actionDuration, deathZoneTimerType, entered, actionTime, state=state)
            self.__lastTimerTypeForSectorGroup[groupID] = deathZoneTimerType
        componentSystem = self.arena.componentSystem
        componentSystem.sectorComponent.playerSectorGroupChanged(groupID, goodGroup, self.__lastPlayerSectorGroupID, self.__isCurrentPlayerSectorGroupAllowed, sectorID)
        self.__lastPlayerSectorGroupID = groupID
        self.__isCurrentPlayerSectorGroupAllowed = goodGroup
        lane = componentSystem.sectorComponent.getSectorById(sectorID).playerGroup
        componentSystem.playerDataComponent.setPhysicalLane(lane, groupID)
        return

    def onStepRepairPointAction(self, repairPointIndex, action, nextActionTime, pointsHealed):
        stepRepairPointComponent = self.arena.componentSystem.stepRepairPointComponent
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.stepRepairPointPlayerAction(repairPointIndex, action, nextActionTime, pointsHealed)
        return

    def onSectorBaseAction(self, sectorBaseID, action, nextActionTime):
        sectorBaseComponent = self.arena.componentSystem.sectorBaseComponent
        if sectorBaseComponent is not None:
            sectorBaseComponent.sectorBasePlayerAction(sectorBaseID, action, nextActionTime)
        return

    def enteringProtectionZone(self, zoneID):
        protectionZoneComponent = self.arena.componentSystem.protectionZoneComponent
        protectionZoneComponent.playerInProtectedZone(zoneID, True)
        if protectionZoneComponent.getOwningTeamForZone(zoneID) is not self.team:
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.UNDER_FIRE, True)

    def leavingProtectionZone(self, zoneID):
        protectionZoneComponent = self.arena.componentSystem.protectionZoneComponent
        protectionZoneComponent.playerInProtectedZone(zoneID, False)
        if protectionZoneComponent.getOwningTeamForZone(zoneID) is not self.team:
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.UNDER_FIRE, False)

    def protectionZoneShooting(self, zoneID):
        self.__playSound(EPIC_SOUND.BF_EB_LANDING_ZONE_PROTECTION)

    def onXPUpdated(self, xpValue):
        playerDataComponent = BigWorld.player().arena.componentSystem.playerDataComponent
        playerDataComponent.setPlayerXP(xpValue)

    def onRankUpdate(self, newRank):
        playerDataComponent = BigWorld.player().arena.componentSystem.playerDataComponent
        playerDataComponent.onPlayerRankUpdated(newRank)

    def enableFrontLineDevInfo(self, enable):
        self.__frontLineDevInfoEnabled = enable
        self.base.enableFrontLineDevInfo(enable)

    def toggleFrontLineDevInfo(self):
        self.__frontLineDevInfoEnabled = not self.__frontLineDevInfoEnabled
        self.base.enableFrontLineDevInfo(self.__frontLineDevInfoEnabled)

    def onSectorShooting(self, sectorID):
        self.__playSound(EPIC_SOUND.BF_EB_CLOSED_ZONE_ARTILLERY)

    def frontLineInformationUpdate(self, params):
        frontlinePoints = params[0]
        attackerIntruder = params[1]
        defenderIntruder = params[2]
        self.onFrontLineInfoUpdated(frontlinePoints, attackerIntruder, defenderIntruder)

    def __sendGlobalChatCmdIfPossible(self, key):
        sectorBaseCmp = getattr(self.guiSessionProvider.arenaVisitor.getComponentSystem(), 'sectorBaseComponent', None)
        if not sectorBaseCmp:
            return False
        ctrl = self.guiSessionProvider.dynamic.maps
        if not ctrl:
            return False
        elif not ctrl.overviewMapScreenVisible:
            return False
        lane = 0
        chatCommandName = None
        cmdMap = CommandMapping.g_instance
        isAttacker = BigWorld.player().team == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER
        for chatCmd, keyboardCmd in _KB_MAPPING.iteritems():
            if cmdMap.isFired(keyboardCmd, key):
                if chatCmd in _COMMAND_TO_LANE_MAPPING.keys():
                    lane = _COMMAND_TO_LANE_MAPPING[chatCmd]
                    chatCommandName = chatCmd
                    break
                else:
                    chatCommandName = chatCmd + (_ATTACKER_POSTFIX if isAttacker else _DEFENDER_POSTFIX)
                    break

        commands = self.guiSessionProvider.shared.chatCommands
        if chatCommandName is not None and commands is not None:
            baseName = ''
            if lane > 0:
                baseName = ID_TO_BASENAME[_MISSION_SECTOR_ID_MAPPING[lane][sectorBaseCmp.getNumNonCapturedBasesByLane(lane)]]
            commands.sendEpicGlobalCommand(chatCommandName, baseName)
            return True
        else:
            return False

    def __playSound(self, eventName):
        if not EPIC_SOUND.EPIC_MSG_SOUNDS_ENABLED:
            return
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(eventName)
