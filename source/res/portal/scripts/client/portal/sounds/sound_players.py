# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/sounds/sound_players.py
import BigWorld
import nations
import WWISE
from debug_utils import LOG_ERROR
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.battle_control.controllers.sound_ctrls.common import SoundPlayer, VehicleStateSoundPlayer
from items import vehicles
from constants import EQUIPMENT_STAGES, ATTACK_REASON, ATTACK_REASON_INDICES
from portal_common.portal_constants import BattleState
from portal_common.items import portal_artefacts
from portal.sounds.sound_constants import LanguageSwitch, CharacterSwitch, SWITCH_CHARACTERS_FOR_NATIONS, GameplayVoiceovers, PortalUISound, PortalMusicState, PortalAbilitySound, PortalBattleUISound, PortalBattleSound
from portal.sounds.sound_helpers import playVoiceover, play2DSound
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from PlayerEvents import g_playerEvents
from PortalBattleStateComponent import PortalBattleStateComponent

class PortalGameFlowStateSoundPlayer(SoundPlayer):
    battleSession = dependency.descriptor(IBattleSessionProvider)
    __EQUIPMENT_ACTIVATION = {'berserk_portal': PortalAbilitySound.BERSERK_START,
     'guided_missile_portal': PortalAbilitySound.GUIDED_MISSILE_START}
    __EQUIPMENT_DEACTIVATION = {'reload_aura_portal': PortalAbilitySound.RELOAD_AURA_STOP,
     'berserk_portal': PortalAbilitySound.BERSERK_STOP}
    __EQUIPMENT_CANCELLATION = {'vehicle_change_shot_portal': PortalAbilitySound.CHANGE_SHOT_DEACTIVATION}

    def _subscribe(self):
        avatar = BigWorld.player()
        avatar.onVehicleEnterWorld += self.__onVehicleEnterWorld
        avatar.arena.onVehicleKilled += self.__onVehicleKilled
        ctrl = self.battleSession.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated += self.__onEquipmentUpdated
        return

    def _unsubscribe(self):
        avatar = BigWorld.player()
        avatar.arena.onVehicleKilled -= self.__onVehicleKilled
        ctrl = self.battleSession.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        return

    @property
    def __stateComp(self):
        return BigWorld.player().arena.arenaInfo.portalBattleStateComponent

    def __onVehicleEnterWorld(self, vehicle):
        if vehicle.id == avatar_getter.getVehicleIDAttached():
            BigWorld.player().onVehicleEnterWorld -= self.__onVehicleEnterWorld
            WWISE.WW_setSwitch(LanguageSwitch.GROUP, LanguageSwitch.RU)
            WWISE.WW_setSwitch(CharacterSwitch.GROUP, self.__getSwitchCharacterValue(vehicle))

    def __getSwitchCharacterValue(self, vehicle):
        compactDescr = vehicle.typeDescriptor.type.compactDescr
        _, nationIdx, _ = vehicles.parseIntCompactDescr(compactDescr)
        nationName = nations.NAMES[nationIdx]
        return SWITCH_CHARACTERS_FOR_NATIONS[nationName]

    def __onVehicleKilled(self, targetID, attackerID, equipmentID, reason, numVehiclesAffected):
        playerVehID = BigWorld.player().playerVehicleID
        if targetID == playerVehID:
            playVoiceover(GameplayVoiceovers.PLAYER_KILLED)

    def __onEquipmentUpdated(self, _, item):
        if item.getPrevStage() == item.getStage():
            return
        equipment = vehicles.g_cache.equipments().get(item.getEquipmentID())
        if not equipment:
            return
        prevStage = item.getPrevStage()
        curStage = item.getStage()
        if item.becomeReady:
            play2DSound(PortalUISound.READY_SOUND)
        elif prevStage == EQUIPMENT_STAGES.READY and curStage in (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.PREPARING, EQUIPMENT_STAGES.COOLDOWN):
            play2DSound(PortalUISound.PRESSED_SOUND)
            self.__playMappedSound(item, self.__EQUIPMENT_ACTIVATION)
        elif prevStage == EQUIPMENT_STAGES.PREPARING and curStage == EQUIPMENT_STAGES.COOLDOWN:
            if isinstance(equipment, (portal_artefacts.PortalMinefield, portal_artefacts.PortalSentryGun, portal_artefacts.VehicleTrap)):
                play2DSound(PortalUISound.APPLY_SOUND)
        elif prevStage == EQUIPMENT_STAGES.ACTIVE and curStage == EQUIPMENT_STAGES.COOLDOWN:
            self.__playMappedSound(item, self.__EQUIPMENT_DEACTIVATION)
        elif prevStage == EQUIPMENT_STAGES.PREPARING and curStage == EQUIPMENT_STAGES.READY:
            play2DSound(PortalUISound.CANCEL_SOUND)
            self.__playMappedSound(item, self.__EQUIPMENT_CANCELLATION)
        self.__playActivationVoiceover(equipment, prevStage, curStage)

    def __playActivationVoiceover(self, equipment, prevStage, curStage):
        if not equipment or not equipment.activationSound:
            return
        if prevStage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING) and curStage in (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.COOLDOWN):
            playVoiceover(equipment.activationSound)

    def __playMappedSound(self, item, soundMap):
        sound = soundMap.get(item.getDescriptor().name)
        if sound:
            play2DSound(sound)


class PortalVehicleStateSoundPlayer(VehicleStateSoundPlayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PortalVehicleStateSoundPlayer, self).__init__()
        self.__respawnTimerID = None
        self.__prbToBattleOffTimerID = None
        return

    def destroy(self):
        if self.__respawnTimerID:
            BigWorld.cancelCallback(self.__respawnTimerID)
            self.__respawnTimerID = None
        if self.__prbToBattleOffTimerID:
            BigWorld.cancelCallback(self.__prbToBattleOffTimerID)
            self.__prbToBattleOffTimerID = None
        super(PortalVehicleStateSoundPlayer, self).destroy()
        return

    def _subscribe(self):
        super(PortalVehicleStateSoundPlayer, self)._subscribe()
        avatar = BigWorld.player()
        avatar.onVehicleEnterWorld += self.__onVehicleEnterWorld
        avatar.onVehicleLeaveWorld += self.__onVehicleLeaveWorld
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onPlayerFeedbackReceived += self.__onPlayerFeedback
        PortalBattleStateComponent.onBattleStateChanged += self.__onBattleStateChanged
        PortalBattleStateComponent.onCampCaptured += self.__onCampCaptured

    def _unsubscribe(self):
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onPlayerFeedbackReceived -= self.__onPlayerFeedback
        avatar = BigWorld.player()
        avatar.onVehicleEnterWorld -= self.__onVehicleEnterWorld
        avatar.onVehicleLeaveWorld -= self.__onVehicleLeaveWorld
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        PortalBattleStateComponent.onBattleStateChanged -= self.__onBattleStateChanged
        PortalBattleStateComponent.onCampCaptured -= self.__onCampCaptured
        super(PortalVehicleStateSoundPlayer, self)._unsubscribe()

    @property
    def __stateComp(self):
        return BigWorld.player().arena.arenaInfo.portalBattleStateComponent

    def __onVehicleEnterWorld(self, vehicle):
        playerVehID = BigWorld.player().playerVehicleID
        if playerVehID != vehicle.id:
            return
        comp = self.__getRespawnComp(vehicle)
        if not comp:
            LOG_ERROR('[PortalSound]: invalid VehicleRespawnComponent')
            return
        comp.onSetSpawnTime += self.__onSetSpawnTime

    def __onVehicleLeaveWorld(self, vehicle):
        playerVehID = BigWorld.player().playerVehicleID
        if playerVehID != vehicle.id:
            return
        comp = self.__getRespawnComp(vehicle)
        if not comp:
            LOG_ERROR('[PortalSound]: invalid VehicleRespawnComponent')
            return
        comp.onSetSpawnTime -= self.__onSetSpawnTime

    def __getRespawnComp(self, vehicle):
        return vehicle.dynamicComponents.get('VehicleRespawnComponent') if vehicle else None

    def __onSetSpawnTime(self, vehicleID, spawnTime):
        playerVehID = BigWorld.player().playerVehicleID
        if playerVehID != vehicleID:
            return
        curTime = BigWorld.serverTime()
        self.__respawnTimerID = BigWorld.callback(spawnTime - curTime, self.__onRespawn)

    def __onRespawn(self):
        isNormalFight = self.__stateComp.battleState == BattleState.NORMAL
        isBossFight = self.__stateComp.battleState == BattleState.BOSS_FIGHT
        isSuperBossFight = self.__stateComp.battleState == BattleState.SUPER_BOSS_FIGHT
        playVoiceover(GameplayVoiceovers.NORMAL_RESPAWN)
        if isNormalFight:
            PortalMusicState.setState(PortalMusicState.BATTLE)
        elif isBossFight and self.__stateComp.isAllCampsCaptured():
            PortalMusicState.setState(PortalMusicState.BOSS_FIGHT)
        elif isSuperBossFight:
            PortalMusicState.setState(PortalMusicState.SUPER_BOSS_FIGHT)
        self.__respawnTimerID = None
        return

    def __prbToBattleOff(self):
        play2DSound(PortalBattleUISound.PREBATTLE_TO_BATTLE_OFF)
        PortalMusicState.setState(PortalMusicState.BATTLE)
        self.__prbToBattleOffTimerID = None
        return

    def __onRoundFinished(self, winnerTeam, reason, extraData):
        PortalMusicState.setState(PortalMusicState.AFTER_BATTLE)
        if winnerTeam == 1:
            if self.__stateComp.battleState == BattleState.BOSS_FIGHT:
                playVoiceover(GameplayVoiceovers.PORTAL_WIN)
            elif self.__stateComp.battleState == BattleState.SUPER_BOSS_FIGHT:
                playVoiceover(GameplayVoiceovers.RATTE_WIN)
        elif winnerTeam == 2:
            playVoiceover(GameplayVoiceovers.DEFEAT)

    def __onCampCaptured(self, campName):
        if self.__stateComp.isAllCampsCaptured():
            PortalMusicState.setState(PortalMusicState.BOSS_FIGHT)

    def __onBattleStateChanged(self, battleState):
        if battleState == BattleState.NORMAL:
            play2DSound(PortalBattleUISound.PREBATTLE_TO_BATTLE_ON)
            self.__prbToBattleOffTimerID = BigWorld.callback(PortalBattleUISound.PREBATTLE_TO_BATTLE_TIMER, self.__prbToBattleOff)
        if battleState == BattleState.BOSS_FIGHT and self.__stateComp.isAllCampsCaptured():
            PortalMusicState.setState(PortalMusicState.BOSS_FIGHT)
        elif battleState == BattleState.SUPER_BOSS_FIGHT:
            PortalMusicState.setState(PortalMusicState.SUPER_BOSS_FIGHT)

    def __onPlayerFeedback(self, events):
        for event in events:
            if event.getType() == FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER:
                self.__onPlayerVehicleDamaged(event)

    def __onPlayerVehicleDamaged(self, event):
        extra = event.getExtra()
        attackReasonID = extra.getAttackReasonID()
        if attackReasonID == ATTACK_REASON_INDICES[ATTACK_REASON.SUPER_BOSS_AURA]:
            play2DSound(PortalBattleSound.INCINERATING_AURA_DAMAGE)
