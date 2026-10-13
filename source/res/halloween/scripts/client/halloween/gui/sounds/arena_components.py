# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/sounds/arena_components.py
from __future__ import absolute_import, division
import BigWorld
import SoundGroups
import WWISE
from HWArenaInfoBossHealthBarComponent import getArenaInfoBossHealthBarComponent
from HWArenaPhasesComponent import HWArenaPhasesComponent
from PlayerEvents import g_playerEvents
from StaticDeathZone import StaticDeathZone
from VehicleRespawnComponent import VehicleRespawnComponent
from constants import FINISH_REASON, EQUIPMENT_STAGES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, VEHICLE_VIEW_STATE
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from halloween.gui.hw_vehicle_role_helper import getVehicleRole
from halloween.gui.shared.events import HWBattleLootEvent
from halloween.gui.sounds import playSound, SoundComponentBase, playVoiceover
from halloween.gui.sounds.sound_constants import DeathZoneSounds, PostMortemSounds, BossBattleMusic, HexapodBossBattleMusic, BattleEquipmentPanelSounds, BattleBuffsPanelSounds, BossBattleSound, PersonalDeathZoneSounds, PersonalDeathZoneAbilityBossState, VO, PhaseStartSounds, VehicleDetectorSounds, BOTS_SPAWN, DEFAULT_BOT_SPAWN, LootSounds, LOOT_OBJ_NAME_PATTERN
from halloween_common.halloween_constants import PLAYERS_TEAM, ATTACK_REASON
from helpers import dependency
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
_NITRO_EQUIPMENT_NAME = 'nitroRamDamage'
_HW_EQUIPMENT = 'hwEquipment'
_HW_EMPTY_SLOT = 'hwEmptySlot'
_VEH_DETECTOR_DISTANCE_FAR_AWAY = 0

class HWStaticDeathZoneSounds(SoundComponentBase):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onAvatarReady(self):
        StaticDeathZone.onVehicleEntered += self._onVehicleEnteredInDeathZone
        StaticDeathZone.onVehicleLeft += self._onVehicleLeftInDeathZone
        StaticDeathZone.onDamage += self._onVehicleReceiveDamageByDeathZone
        vehicleStateCtrl = self._sessionProvider.shared.vehicleState
        if vehicleStateCtrl is not None:
            deathZoneState = vehicleStateCtrl.getStateValue(VEHICLE_VIEW_STATE.DEATHZONE)
            if deathZoneState and deathZoneState[0] is True:
                playSound(DeathZoneSounds.ENTER)
        return

    def onDestroy(self):
        StaticDeathZone.onVehicleEntered -= self._onVehicleEnteredInDeathZone
        StaticDeathZone.onVehicleLeft -= self._onVehicleLeftInDeathZone
        StaticDeathZone.onDamage -= self._onVehicleReceiveDamageByDeathZone

    def _onVehicleEnteredInDeathZone(self, zoneId, vehicleId):
        player = BigWorld.player()
        if player.playerVehicleID == vehicleId:
            playSound(DeathZoneSounds.ENTER)

    def _onVehicleLeftInDeathZone(self, zoneId, vehicleId):
        player = BigWorld.player()
        if player.playerVehicleID == vehicleId:
            playSound(DeathZoneSounds.LEAVE)

    def _onVehicleReceiveDamageByDeathZone(self, zoneId, vehicleId):
        player = BigWorld.player()
        if player.playerVehicleID == vehicleId:
            playSound(DeathZoneSounds.DAMAGE)


class HWPostMortemSounds(SoundComponentBase):

    def onAvatarReady(self):
        VehicleRespawnComponent.onVehicleRespawned += self._onVehicleRespawned
        vehicleStateCtrl = self._sessionProvider.shared.vehicleState
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onPostMortemSwitched += self._onPostMortemSwitched
            if vehicleStateCtrl.isInPostmortem:
                playSound(PostMortemSounds.ON)
        return

    def onDestroy(self):
        VehicleRespawnComponent.onVehicleRespawned -= self._onVehicleRespawned
        vehicleStateCtrl = self._sessionProvider.shared.vehicleState
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onPostMortemSwitched -= self._onPostMortemSwitched
        return

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        playSound(PostMortemSounds.ON)

    def _onVehicleRespawned(self, vehicle):
        if vehicle.id == BigWorld.player().playerVehicleID:
            playSound(PostMortemSounds.OFF)


class HWBossBattleMusic(SoundComponentBase):

    def __init__(self, parent):
        super(HWBossBattleMusic, self).__init__(parent)
        self._arenaBonusType = BigWorld.player().arena.bonusType
        self._bossReceivesFirstDamageOnPhase = False

    def onAvatarReady(self):
        HWArenaPhasesComponent.onPhaseChanged += self._onPhaseChanged
        g_playerEvents.onRoundFinished += self._onRoundFinished
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onBossLivesChanged += self._onBossLivesChanged
        if HWArenaPhasesComponent.getInstance().isLastPhase():
            playSound(BossBattleMusic.BOSS_FIGHT_START)
            bossHBComp = getArenaInfoBossHealthBarComponent()
            if bossHBComp is not None and bossHBComp.livesLeft < bossHBComp.maxLives:
                playSound(BossBattleMusic.PHASE_1_FINISH)
        return

    def onDestroy(self):
        HWArenaPhasesComponent.onPhaseChanged -= self._onPhaseChanged
        g_playerEvents.onRoundFinished -= self._onRoundFinished
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onBossLivesChanged -= self._onBossLivesChanged

    def onShotAtBoss(self, attackerID, *_):
        if BigWorld.player().playerVehicleID == attackerID and not self._bossReceivesFirstDamageOnPhase and HWArenaPhasesComponent.getInstance().isLastPhase():
            self._bossReceivesFirstDamageOnPhase = True
            bossHBComp = getArenaInfoBossHealthBarComponent()
            if bossHBComp is not None:
                playSound(BossBattleMusic.getFirstDamageEventByBossLives(bossHBComp.livesLeft))
        return

    def _onBossLivesChanged(self):
        bossHBComp = getArenaInfoBossHealthBarComponent()
        if bossHBComp is not None and bossHBComp.livesLeft > 0:
            playSound(BossBattleSound.BOSS_TELEPORTATION)
            playSound(BossBattleMusic.PHASE_1_FINISH)
            self._bossReceivesFirstDamageOnPhase = False
        return

    def _onPhaseChanged(self, arenaPhases):
        if arenaPhases.isLastPhase():
            playSound(BossBattleMusic.BOSS_FIGHT_START)

    def _onRoundFinished(self, winnerTeam, reason):
        if winnerTeam == PLAYERS_TEAM:
            playSound(BossBattleMusic.BOSS_KILLED)
        elif reason == FINISH_REASON.EXTERMINATION:
            bossHBComp = getArenaInfoBossHealthBarComponent()
            if bossHBComp is not None and bossHBComp.isActive:
                playSound(BossBattleMusic.getLoseEvent(self._bossReceivesFirstDamageOnPhase, bossHBComp.livesLeft))
        return


class HWHexapodBossBattleMusic(SoundComponentBase):

    def __init__(self, parent):
        super(HWHexapodBossBattleMusic, self).__init__(parent)
        self._bossHBComp = None
        return

    def onAvatarReady(self):
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onBossHealthChanged += self._onBossHealthChanged
            hwBattleGuiCtrl.onBossHealthActivated += self._onBossHealthActivated
            self.hwBattleGuiCtrl.onBossLivesChanged += self._onBossLivesChanged
        self._updateBossHealthRTPC()

    def onDestroy(self):
        self._bossHBComp = None
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onBossHealthChanged -= self._onBossHealthChanged
            hwBattleGuiCtrl.onBossHealthActivated -= self._onBossHealthActivated
            self.hwBattleGuiCtrl.onBossLivesChanged -= self._onBossLivesChanged
        return

    @property
    def bossHBComp(self):
        if not self._bossHBComp:
            self._bossHBComp = getArenaInfoBossHealthBarComponent()
        return self._bossHBComp

    def _onBossHealthChanged(self, newHealth, prevHealth, bossVehicleID, attackerID, attackReasonID):
        self._updateBossHealthRTPC()

    def _onBossHealthActivated(self):
        self._updateBossHealthRTPC()

    def _updateBossHealthRTPC(self):
        bossHBComp = self.bossHBComp
        if bossHBComp is not None:
            curHP, maxHP = bossHBComp.getBossCurrentLifeHealthValues()
            if maxHP > 0:
                SoundGroups.g_instance.setGlobalRTPC(HexapodBossBattleMusic.BOSS_HP_RTPC, 100.0 * curHP / maxHP)
        return

    def _onBossLivesChanged(self):
        bossHBComp = self.bossHBComp
        if bossHBComp is not None and bossHBComp.livesLeft > 0:
            playSound(BossBattleSound.BOSS_TELEPORTATION)
        return


class HWPhaseStateUpdateSounds(SoundComponentBase):

    def onAvatarReady(self):
        HWArenaPhasesComponent.onPhaseChanged += self._onPhaseChanged

    def onDestroy(self):
        HWArenaPhasesComponent.onPhaseChanged -= self._onPhaseChanged

    def _onPhaseChanged(self, arenaPhases):
        phaseChangedEvent = PhaseStartSounds.getPhaseStartedEvent(arenaPhases.activePhase)
        playSound(phaseChangedEvent)


class HWEquipmentPanelSounds(SoundComponentBase):
    ACTIVE_EQUIPMENT_STAGES = (EQUIPMENT_STAGES.DEPLOYING,
     EQUIPMENT_STAGES.PREPARING,
     EQUIPMENT_STAGES.ACTIVE,
     EQUIPMENT_STAGES.COOLDOWN)

    def __init__(self, parent):
        super(HWEquipmentPanelSounds, self).__init__(parent)
        self._readyEquipment = set()
        self._nextTickEvents = set()
        self._nextTickCB = None
        return

    @property
    def vehicle(self):
        player = BigWorld.player()
        return player.vehicle if player is not None else None

    def onAvatarReady(self):
        ctrl = self._sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated += self._onEquipmentUpdated
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onHandleEquipmentPressed += self._onHandleEquipmentPressed
        vehicleSoulsContainer = self._getPlayerVehicleSoulsContainer()
        if vehicleSoulsContainer:
            vehicleSoulsContainer.onChangeSoulsCount += self._onSoulsChanged
        nitroComp = BigWorld.player().hwNitroAccelerationControl
        if nitroComp:
            nitroComp.onActivate += self._onNitroActivate
        vehicleCtrl = self._sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onVehicleStateUpdated += self._onVehicleStateUpdated
        return

    def onDestroy(self):
        ctrl = self._sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated -= self._onEquipmentUpdated
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onHandleEquipmentPressed -= self._onHandleEquipmentPressed
        vehicleSoulsContainer = self._getPlayerVehicleSoulsContainer()
        if vehicleSoulsContainer:
            vehicleSoulsContainer.onChangeSoulsCount -= self._onSoulsChanged
        vehicleCtrl = self._sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
        self._nextTickEvents.clear()
        self._clearCB()
        nitroComp = BigWorld.player().hwNitroAccelerationControl
        if nitroComp:
            nitroComp.onActivate -= self._onNitroActivate
        return

    def _onEquipmentUpdated(self, _, item):
        if item.getPrevStage() == EQUIPMENT_STAGES.READY and item.getStage() in self.ACTIVE_EQUIPMENT_STAGES:
            playSound(BattleEquipmentPanelSounds.ACTIVATE)
        elif self._checkEquipmentState(item) and self._isPlayerAlive():
            self._play(BattleEquipmentPanelSounds.READY)

    def _onSoulsChanged(self, newCount, reason):
        self._updateAbilities()

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.HEALTH:
            self._updateAbilities()

    def _updateAbilities(self):
        played = False
        if self.vehicle is None or self.vehicle.setups is None:
            return
        else:
            for equipmentId in self.vehicle.setups['eqsSetups'][0]:
                if not self._sessionProvider.shared.equipments.hasEquipment(equipmentId):
                    continue
                isReady = self._checkEquipmentState(self._sessionProvider.shared.equipments.getEquipment(equipmentId))
                if isReady and not played:
                    played = True
                    self._play(BattleEquipmentPanelSounds.READY)

            return

    def _onNitroActivate(self):
        item = self._getNitroEquipment()
        if item is None:
            return
        else:
            if not self._isAbilityReady(item):
                self._play(BattleEquipmentPanelSounds.NOT_READY)
            return

    def _getNitroEquipment(self):
        if self.vehicle is None:
            return
        else:
            for intCD in self.vehicle.setups['eqsSetups'][0]:
                item = self._sessionProvider.shared.equipments.getEquipment(intCD)
                if item.getDescriptor().name == _NITRO_EQUIPMENT_NAME:
                    return item

            return

    def _checkEquipmentState(self, item):
        if item is None:
            return False
        else:
            equipmentID = item.getEquipmentID()
            prevIsReady = equipmentID in self._readyEquipment
            isReady = self._isAbilityReady(item)
            if isReady:
                self._readyEquipment.add(equipmentID)
            else:
                self._readyEquipment.discard(equipmentID)
            return True if isReady and not prevIsReady else False

    def _isAbilityReady(self, item):
        return item.getStage() != EQUIPMENT_STAGES.COOLDOWN and item.canActivate()[0] and not self._isHalloweenEmptySlot(item)

    def _isHalloweenEmptySlot(self, item):
        return self._isHalloweenEquipment(item) and _HW_EMPTY_SLOT in item.getDescriptor().tags

    def _isHalloweenEquipment(self, item):
        return _HW_EQUIPMENT in item.getDescriptor().tags

    def _onHandleEquipmentPressed(self, intCD):
        item = self._sessionProvider.shared.equipments.getEquipment(intCD)
        if not self._isAbilityReady(item):
            self._play(BattleEquipmentPanelSounds.NOT_READY)

    def _getPlayerVehicleSoulsContainer(self):
        vehicle = self.vehicle
        return vehicle.dynamicComponents.get('hwSoulsContainer') if vehicle else None

    def _isPlayerAlive(self):
        vehicle = self.vehicle
        return vehicle and vehicle.isAlive()

    def _play(self, event):
        if event not in self._nextTickEvents:
            self._nextTickEvents.add(event)
        if self._nextTickCB is None:
            self._nextTickCB = BigWorld.callback(0, self._playOnNextTick)
        return

    def _playOnNextTick(self):
        for event in self._nextTickEvents:
            playSound(event)

        self._nextTickEvents.clear()
        self._clearCB()

    def _clearCB(self):
        if self._nextTickCB is not None:
            BigWorld.cancelCallback(self._nextTickCB)
            self._nextTickCB = None
        return


class HWBuffsPanelSounds(SoundComponentBase):

    def __init__(self, parent):
        super(HWBuffsPanelSounds, self).__init__(parent)
        self._isNotificationActive = False
        self._playShowIconCB = None
        return

    def onAvatarReady(self):
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onApplyBuff += self._handleBuffApply
            self.hwBattleGuiCtrl.onShowPanelBuffNotification += self._onShowPanelBuffNotification

    def onDestroy(self):
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onApplyBuff -= self._handleBuffApply
            self.hwBattleGuiCtrl.onShowPanelBuffNotification -= self._onShowPanelBuffNotification
        self._clearCB()

    def _handleBuffApply(self, _):
        if self._playShowIconCB is None:
            self._playShowIconCB = BigWorld.callback(0, self._playShowIcon)
        return

    def _onShowPanelBuffNotification(self, isActive):
        if isActive:
            self._playActivation()
        else:
            self._playDeactivation()

    def _playShowIcon(self):
        playSound(BattleBuffsPanelSounds.SHOW_ICON)
        self._clearCB()

    def _playActivation(self):
        if not self._isNotificationActive:
            self._isNotificationActive = True
            playSound(BattleBuffsPanelSounds.ACTIVATE)

    def _playDeactivation(self):
        if self._isNotificationActive:
            self._isNotificationActive = False
            playSound(BattleBuffsPanelSounds.DEACTIVATE)

    def _clearCB(self):
        if self._playShowIconCB is not None:
            BigWorld.cancelCallback(self._playShowIconCB)
            self._playShowIconCB = None
        return


class HWPersonalDeathZoneSounds(SoundComponentBase):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onAvatarReady(self):
        personalDeathZonesCtrl = self._personalDeathZonesCtrl
        if personalDeathZonesCtrl:
            personalDeathZonesCtrl.onPlayerEnteredDeathZone += self._onPlayerEnteredDeathZone
            personalDeathZonesCtrl.onPlayerLeftDeathZone += self._onPlayerLeftDeathZone

    def onDestroy(self):
        personalDeathZonesCtrl = self._personalDeathZonesCtrl
        if personalDeathZonesCtrl:
            personalDeathZonesCtrl.onPlayerEnteredDeathZone -= self._onPlayerEnteredDeathZone
            personalDeathZonesCtrl.onPlayerLeftDeathZone -= self._onPlayerLeftDeathZone

    def onBossAuraIntersectEvent(self, vehicleId, entered):
        player = BigWorld.player()
        if player.playerVehicleID == vehicleId:
            playSound(BossBattleSound.getAuraIntersectionEvent(entered))

    def _onPlayerEnteredDeathZone(self, _):
        if len(self._personalDeathZonesCtrl.enteredDeathZones) == 1:
            WWISE.WW_setState(PersonalDeathZoneAbilityBossState.GROUP, PersonalDeathZoneAbilityBossState.ENTER)
            playSound(PersonalDeathZoneSounds.ACTIVATION)

    def _onPlayerLeftDeathZone(self, _):
        if not self._personalDeathZonesCtrl.enteredDeathZones:
            WWISE.WW_setState(PersonalDeathZoneAbilityBossState.GROUP, PersonalDeathZoneAbilityBossState.EXIT)
            playSound(PersonalDeathZoneSounds.DEACTIVATION)

    @property
    def _personalDeathZonesCtrl(self):
        return self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.PERSONAL_DEATH_ZONES_GUI_CTRL)


class HWVehicleDetectorSounds(SoundComponentBase):

    def __init__(self, parent):
        super(HWVehicleDetectorSounds, self).__init__(parent)
        self._isVehicleSpotted = False

    def onAvatarReady(self):
        HWArenaPhasesComponent.onPhaseChanged += self._onPhaseChanged
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onVehicleDetectorChangeDistance += self._onVehicleDetectorChangeDistance

    def onDestroy(self):
        HWArenaPhasesComponent.onPhaseChanged -= self._onPhaseChanged
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onVehicleDetectorChangeDistance -= self._onVehicleDetectorChangeDistance

    def _onPhaseChanged(self, _):
        self._handleDistandeChange(distance=_VEH_DETECTOR_DISTANCE_FAR_AWAY)

    def _onVehicleDetectorChangeDistance(self, ctx):
        distance = ctx.get('indicator', _VEH_DETECTOR_DISTANCE_FAR_AWAY)
        self._handleDistandeChange(distance)

    def _handleDistandeChange(self, distance):
        WWISE.WW_setRTCPGlobal(VehicleDetectorSounds.RTPC, distance)
        if not self._isVehicleSpotted and distance > 0:
            self._isVehicleSpotted = True
            playSound(VehicleDetectorSounds.DETECTOR_ON)
        elif self._isVehicleSpotted and distance == 0:
            self._isVehicleSpotted = False
            playSound(VehicleDetectorSounds.DETECTOR_OFF)


class HWBotSpawnSounds(SoundComponentBase):

    def onBotCreated(self, vehicleType, position):
        spawnEvent = BOTS_SPAWN.get(vehicleType, DEFAULT_BOT_SPAWN)
        if spawnEvent is not None:
            SoundGroups.g_instance.playSoundPos(spawnEvent, position)
        return


class HWVoiceovers(SoundComponentBase):
    _PHASE_END_NOTIFY_TIME_OFFSET = 60
    _COLLECTOR_FILLED_PERCENT_NOTIFY = 50
    _INVULNERABLE_ATTACK_REASONS = (ATTACK_REASON.SHOT,)

    def __init__(self, parent):
        super(HWVoiceovers, self).__init__(parent)
        self._shotAtBossPerformed = False
        self._needNotifyOneMinLeftToGetMirium = True
        self._needNotifyCollectorHalfFilled = True
        self._needNotifyCollectorFullFilled = True
        self._needNotifyBossAppearing = True
        self._playersSoulsAtStart = 0

    def onAvatarReady(self):
        HWArenaPhasesComponent.onPhaseTimeChanged += self._onPhaseTimeChanged
        HWArenaPhasesComponent.onPhaseChanged += self._onPhaseChanged
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onSoulCollectorProgress += self._onCollectorSoulsChanged
            self.hwBattleGuiCtrl.onBossHPBarVisibilityChanged += self._onBossHPBarVisibilityChanged
        self._onPhaseChanged(self.arenaPhases)

    def onDestroy(self):
        HWArenaPhasesComponent.onPhaseTimeChanged -= self._onPhaseTimeChanged
        HWArenaPhasesComponent.onPhaseChanged -= self._onPhaseChanged
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onSoulCollectorProgress -= self._onCollectorSoulsChanged
            self.hwBattleGuiCtrl.onBossHPBarVisibilityChanged -= self._onBossHPBarVisibilityChanged

    def onBotCreated(self, vehicleType, _):
        vehType = vehicles.g_cache.vehicle(*vehicles.g_list.getIDsByName(vehicleType))
        role = getVehicleRole(vehType)
        vo = VO.BOTS_SPAWN_BY_ROLE.get(role, None)
        if vo:
            vo.play()
        return

    def onShotAtBoss(self, attackerID, attackReason, _):
        if BigWorld.player().playerVehicleID != attackerID:
            return
        if not self._shotAtBossPerformed and not self.arenaPhases.isLastPhase():
            self._shotAtBossPerformed = True
            VO.FIRST_SHOT_AT_BOSS_BEFORE_BOSS_BATTLE.play()
        if self.arenaPhases.isLastPhase() and not self.arenaPhases.isBossVulnerable:
            if attackReason in self._INVULNERABLE_ATTACK_REASONS:
                VO.SHOT_AT_INVULNERABLE_BOSS.play()

    def onBossEnterWorld(self, bossEntity):
        lastPhase = self.arenaPhases.isLastPhase()
        if self._needNotifyBossAppearing and not lastPhase:
            self._needNotifyBossAppearing = False
            playVoiceover(VO.BOSS_APPEARING.get(bossEntity.typeDescriptor.name))

    def _onBossHPBarVisibilityChanged(self, visible):
        bossHBComp = getArenaInfoBossHealthBarComponent()
        if not bossHBComp:
            return
        if not visible and bossHBComp.livesLeft > 0:
            VO.BOSSFIGHT_PHASE_2.play()
        if visible and bossHBComp.livesLeft < bossHBComp.maxLives:
            VO.BOSSFIGHT_PHASE_3.play()

    def _onPhaseChanged(self, arenaPhases):
        if arenaPhases.isLastPhase():
            return
        self._needNotifyOneMinLeftToGetMirium = True
        self._needNotifyCollectorHalfFilled = True
        self._needNotifyCollectorFullFilled = True
        self._needNotifyBossAppearing = True

    def _onPhaseTimeChanged(self, timeLeft, prev, isLastPhase):
        if isLastPhase:
            return
        if self._needNotifyOneMinLeftToGetMirium:
            self._needNotifyOneMinLeftToGetMirium = 0 < timeLeft <= self._PHASE_END_NOTIFY_TIME_OFFSET and False
            VO.PHASE_ONE_MINUTE_LEFT.play()

    def _onCollectorSoulsChanged(self, collected, capacity, isFull, isCampActivated):
        if self._needNotifyCollectorFullFilled and isFull:
            self._needNotifyCollectorFullFilled = False
            VO.COLLECTOR_FULL_FILLED.play()
        elif not isFull:
            if self._needNotifyCollectorHalfFilled and collected is not None and capacity is not None:
                if collected * 100.0 / capacity >= self._COLLECTOR_FILLED_PERCENT_NOTIFY:
                    self._needNotifyCollectorHalfFilled = False
                    VO.COLLECTOR_HALF_FILLED.play()
        return


class HWTeamFightVoiceovers(SoundComponentBase):

    @property
    def arenaDP(self):
        return self._sessionProvider.getArenaDP()

    def onAvatarReady(self):
        BigWorld.player().arena.onVehicleKilled += self._onArenaVehicleKilled

    def onDestroy(self):
        BigWorld.player().arena.onVehicleKilled -= self._onArenaVehicleKilled

    def _getAlliesAliveCount(self):
        vehInfoIterator = self.arenaDP.getVehiclesInfoIterator()
        return len([ v for v in vehInfoIterator if v.team == PLAYERS_TEAM and v.isAlive() ])

    def _onArenaVehicleKilled(self, vehicleID, *_):
        if not self.arenaDP.isAlly(vehicleID):
            return
        alliesAliveCount = self._getAlliesAliveCount()
        if alliesAliveCount < 1:
            return
        if vehicleID == BigWorld.player().playerVehicleID:
            if not self.arenaPhases.isRespawnEnabled:
                return
            vo = VO.PLAYER_DEAD_BOSSFIGHT if self.arenaPhases.isLastPhase() else VO.PLAYER_DEAD_COMMON
            playVoiceover(vo)
        else:
            VO.getAllyTanksLeftVO(alliesAliveCount).play()


class HWArenaLootSounds(SoundComponentBase):

    def __init__(self, parent):
        super(HWArenaLootSounds, self).__init__(parent)
        self._lootSounds = {}
        for event in self._getEvents():
            g_eventBus.addListener(*event)

    def onAvatarReady(self):
        HWArenaPhasesComponent.onPhaseChanged += self._onPhaseChanged

    def onDestroy(self):
        HWArenaPhasesComponent.onPhaseChanged -= self._onPhaseChanged
        for event in self._getEvents():
            g_eventBus.removeListener(*event)

        self._clearSounds()

    def _getEvents(self):
        return ((HWBattleLootEvent.APPEAR, self._onLootAppear, EVENT_BUS_SCOPE.BATTLE),
         (HWBattleLootEvent.CAPTURED, self._onLootCaptured, EVENT_BUS_SCOPE.BATTLE),
         (HWBattleLootEvent.VEH_CAPTURING_START, self._onVehCapturingStart, EVENT_BUS_SCOPE.BATTLE),
         (HWBattleLootEvent.VEH_CAPTURING_CANCEL, self._onVehCapturingCancel, EVENT_BUS_SCOPE.BATTLE))

    def _onPhaseChanged(self, arenaPhases):
        if arenaPhases.activePhase > 1:
            self._clearSounds()

    def _clearSounds(self):
        lootIDs = list(self._lootSounds.keys())
        for lootID in lootIDs:
            sound = self._lootSounds.pop(lootID)
            sound.stopAll()

    def _onLootAppear(self, event):
        ctx = event.ctx
        loot = ctx['loot']
        lootID = loot.entity.id
        sound = SoundGroups.g_instance.WWgetSoundObject(LOOT_OBJ_NAME_PATTERN.format(lootID), loot.entity.matrix)
        soundEvent = LootSounds.States.DEFAULT.get(loot.name)
        if soundEvent:
            sound.play(soundEvent)
        self._lootSounds[lootID] = sound

    def _onLootCaptured(self, event):
        ctx = event.ctx
        loot, vehicleID, vehicleIDs = ctx['loot'], ctx['vehID'], ctx['vehIDs']
        soundEvent = LootSounds.States.CAPTURED.get(loot.name)
        if soundEvent:
            lootID = loot.entity.id
            self._lootSounds[lootID].play(soundEvent)
        player = BigWorld.player()
        if player is not None:
            playerVehicleID = player.playerVehicleID
            if vehicleID == playerVehicleID or playerVehicleID in loot.looterEntities:
                playSound(LootSounds.Player.PICKUP_SUCCEED.get(loot.name))
            elif not vehicleIDs or playerVehicleID in vehicleIDs:
                SoundGroups.g_instance.playSoundPos(LootSounds.Ally.PICKUP_SUCCEED, loot.entity.position)
        return

    def _onVehCapturingStart(self, event):
        ctx = event.ctx
        loot, vehicleID = ctx['loot'], ctx['vehID']
        player = BigWorld.player()
        if player and player.playerVehicleID == vehicleID:
            playSound(LootSounds.Player.PICKUP_STARTED.get(loot.name))

    def _onVehCapturingCancel(self, event):
        ctx = event.ctx
        loot, vehicleID = ctx['loot'], ctx['vehID']
        player = BigWorld.player()
        if player and player.playerVehicleID == vehicleID:
            playSound(LootSounds.Player.PICKUP_CANCELED.get(loot.name))
