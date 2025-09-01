# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/sounds/arena_components.py
import BigWorld
import WWISE
from helpers import dependency
from constants import EQUIPMENT_STAGES, ARENA_PERIOD
from StaticDeathZone import StaticDeathZone
from PlayerEvents import g_playerEvents
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, VEHICLE_VIEW_STATE
from last_stand_common.last_stand_constants import PLAYERS_TEAM, INVALID_PHASE
from last_stand.gui.sounds import playSound, SoundComponentBase, playVoiceover
from last_stand.gui.sounds.sound_constants import DeathZoneSounds, PostMortemSounds, BattleEquipmentPanelSounds, PersonalDeathZoneSounds, PersonalDeathZoneAbilityBossState, LastStandVO, BattleMusic, CONVOY_PROGRESS_RTPC
from LSArenaPhasesComponent import LSArenaPhasesComponent
from VehicleRespawnComponent import VehicleRespawnComponent
_LS_EQUIPMENT = 'LS_equipment'
_LS_EMPTY_SLOT = 'LS_emptySlot'

class LSStaticDeathZoneSounds(SoundComponentBase):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parent):
        super(LSStaticDeathZoneSounds, self).__init__(parent)
        self._vehicleInDeathZone = False

    def onAvatarReady(self):
        StaticDeathZone.onDamage += self._onVehicleReceiveDamageByDeathZone
        vehicleStateCtrl = self._sessionProvider.shared.vehicleState
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated += self._onVehicleStateUpdated
            deathZoneState = vehicleStateCtrl.getStateValue(VEHICLE_VIEW_STATE.DEATHZONE)
            if deathZoneState is not None:
                self._onVehicleStateUpdated(VEHICLE_VIEW_STATE.DEATHZONE, deathZoneState)
        return

    def onDestroy(self):
        self._vehicleInDeathZone = False
        StaticDeathZone.onDamage -= self._onVehicleReceiveDamageByDeathZone
        vehicleStateCtrl = self._sessionProvider.shared.vehicleState
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
        return

    def _onVehicleReceiveDamageByDeathZone(self, zoneId, vehicleId):
        player = BigWorld.player()
        if player.playerVehicleID == vehicleId:
            playSound(DeathZoneSounds.DAMAGE)

    def _onVehicleStateUpdated(self, stateID, deathZoneState):
        if stateID != VEHICLE_VIEW_STATE.DEATHZONE:
            return
        if self._vehicleInDeathZone != deathZoneState[0]:
            self._vehicleInDeathZone = deathZoneState[0]
            playSound(DeathZoneSounds.ENTER if self._vehicleInDeathZone else DeathZoneSounds.LEAVE)


class LSPostMortemSounds(SoundComponentBase):

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


class LSEquipmentPanelSounds(SoundComponentBase):
    ACTIVE_EQUIPMENT_STAGES = (EQUIPMENT_STAGES.DEPLOYING,
     EQUIPMENT_STAGES.PREPARING,
     EQUIPMENT_STAGES.ACTIVE,
     EQUIPMENT_STAGES.COOLDOWN)

    def __init__(self, parent):
        super(LSEquipmentPanelSounds, self).__init__(parent)
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
        if self.lsBattleGuiCtrl:
            self.lsBattleGuiCtrl.onHandleEquipmentPressed += self._onHandleEquipmentPressed
        vehicleSoulsContainer = self._getPlayerVehicleSoulsContainer()
        if vehicleSoulsContainer:
            vehicleSoulsContainer.onChangeSoulsCount += self._onSoulsChanged
        vehicleCtrl = self._sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onVehicleStateUpdated += self._onVehicleStateUpdated
        return

    def onDestroy(self):
        ctrl = self._sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated -= self._onEquipmentUpdated
        if self.lsBattleGuiCtrl:
            self.lsBattleGuiCtrl.onHandleEquipmentPressed -= self._onHandleEquipmentPressed
        vehicleSoulsContainer = self._getPlayerVehicleSoulsContainer()
        if vehicleSoulsContainer:
            vehicleSoulsContainer.onChangeSoulsCount -= self._onSoulsChanged
        vehicleCtrl = self._sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
        self._nextTickEvents.clear()
        self._clearCB()
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
        return item.getStage() != EQUIPMENT_STAGES.COOLDOWN and item.canActivate()[0] and not self._isEmptySlot(item)

    def _isEmptySlot(self, item):
        return self._isLSEquipment(item) and _LS_EMPTY_SLOT in item.getDescriptor().tags

    def _isLSEquipment(self, item):
        return _LS_EQUIPMENT in item.getDescriptor().tags

    def _onHandleEquipmentPressed(self, intCD):
        item = self._sessionProvider.shared.equipments.getEquipment(intCD)
        if not self._isAbilityReady(item):
            self._play(BattleEquipmentPanelSounds.NOT_READY)

    def _getPlayerVehicleSoulsContainer(self):
        vehicle = self.vehicle
        return vehicle.dynamicComponents.get('lsSoulsContainer') if vehicle else None

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


class LSPersonalDeathZoneSounds(SoundComponentBase):
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


class LSTeamFightVoiceovers(SoundComponentBase):

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
        if vehicleID == BigWorld.player().playerVehicleID:
            if alliesAliveCount > 0 and LSArenaPhasesComponent.getInstance().isRespawnEnabled:
                playVoiceover(LastStandVO.PLAYER_DEAD)
        elif alliesAliveCount > 0:
            LastStandVO.getAllyTanksLeftVO(alliesAliveCount).play()


class LSVoiceovers(SoundComponentBase):

    def onAvatarReady(self):
        super(LSVoiceovers, self).onAvatarReady()
        if self.lsBattleGuiCtrl:
            self.lsBattleGuiCtrl.onEnemiesInfoChanged += self._onEnemiesInfoChanged
        g_playerEvents.onArenaPeriodChange += self._onArenaPeriodChaned

    def onDestroy(self):
        if self.lsBattleGuiCtrl:
            self.lsBattleGuiCtrl.onEnemiesInfoChanged -= self._onEnemiesInfoChanged
        g_playerEvents.onArenaPeriodChange -= self._onArenaPeriodChaned
        super(LSVoiceovers, self).onDestroy()

    def onPhaseChanged(self, activePhase):
        vo = LastStandVO.getWaveStartedVO(activePhase)
        if vo is not None:
            playVoiceover(vo)
        return

    def oneMinuteLeft(self, lastPhase, isInDelta):
        if isInDelta:
            playVoiceover(LastStandVO.ONE_MINUTE_LEFT)

    def _onEnemiesInfoChanged(self, info):
        if info['totalEnemies'] > 0 and info['aliveEnemies'] == 0 and not LSArenaPhasesComponent.getInstance().isLastPhase():
            LastStandVO.WAVE_FINISHED.play()

    def _onArenaPeriodChaned(self, period, *_):
        if period == ARENA_PERIOD.BATTLE:
            LastStandVO.BATTLE_STARTED.play()


class LSBattleMusic(SoundComponentBase):

    def __init__(self, parent):
        super(LSBattleMusic, self).__init__(parent)
        self._currentMusicEvent = None
        return

    def onAvatarReady(self):
        super(LSBattleMusic, self).onAvatarReady()
        if self.lsBattleGuiCtrl:
            self.lsBattleGuiCtrl.onEnemiesInfoChanged += self._onEnemiesInfoChanged
            phasesComp = LSArenaPhasesComponent.getInstance()
            if phasesComp.activePhase != INVALID_PHASE:
                self._changeMusicByEnemiesInfo(self.lsBattleGuiCtrl.getEnemiesInfo())

    def onDestroy(self):
        if self.lsBattleGuiCtrl:
            self.lsBattleGuiCtrl.onEnemiesInfoChanged -= self._onEnemiesInfoChanged
        super(LSBattleMusic, self).onDestroy()

    def onPhaseChanged(self, _):
        self._playMusic(BattleMusic.WAVE_STARTED)

    def _onEnemiesInfoChanged(self, info):
        self._changeMusicByEnemiesInfo(info)

    def _changeMusicByEnemiesInfo(self, info):
        if not info or info['totalEnemies'] <= 0:
            return
        if info['aliveEnemies'] == 0:
            if LSArenaPhasesComponent.getInstance().isLastPhase():
                self._playMusic(BattleMusic.WIN)
            else:
                self._playMusic(BattleMusic.BOTS_DESTROYED)
        else:
            self._playMusic(BattleMusic.WAVE_STARTED)

    def _playMusic(self, event):
        if self._currentMusicEvent != event:
            self._currentMusicEvent = event
            playSound(event)


class LSConvoySounds(SoundComponentBase):
    CONVOY_PROGRESS_START_VALUE = 100
    CONVOY_PROGRESS_FINISH_VALUE = 0

    def onAvatarReady(self):
        if self.lsBattleGuiCtrl is not None:
            self.lsBattleGuiCtrl.onConvoyStatusChanged += self._onConvoyStatusChanged
        return

    def onDestroy(self):
        if self.lsBattleGuiCtrl is not None:
            self.lsBattleGuiCtrl.onConvoyStatusChanged -= self._onConvoyStatusChanged
            self.lsBattleGuiCtrl.onConvoyDistanceIndicatorChanged -= self._onConvoyDistanceIndicatorChanged
        return

    def _onConvoyStatusChanged(self, status):
        if self.lsBattleGuiCtrl is not None:
            if status and all((not data['isDead'] for data in status)):
                self.lsBattleGuiCtrl.onConvoyDistanceIndicatorChanged += self._onConvoyDistanceIndicatorChanged
            elif status and all((data['isDead'] for data in status)):
                self.lsBattleGuiCtrl.onConvoyStatusChanged -= self._onConvoyStatusChanged
                self.lsBattleGuiCtrl.onConvoyDistanceIndicatorChanged -= self._onConvoyDistanceIndicatorChanged
        return

    def _onConvoyDistanceIndicatorChanged(self, value):
        WWISE.WW_setRTCPGlobal(CONVOY_PROGRESS_RTPC, max(self.CONVOY_PROGRESS_START_VALUE - value, self.CONVOY_PROGRESS_FINISH_VALUE))
