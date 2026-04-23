# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/battle/cosmic_hud/cosmic_hud_view.py
import functools
import logging
import typing
import weakref
import BigWorld
import GUI
import CommandMapping
from cosmic_event.gui.impl.battle.cosmic_hud.announcements import AnnouncementGoal, _AnnouncementRespawn, getAnnouncementType
from cosmic_event.gui.impl.battle.cosmic_hud.progress_bar_manager import CosmicProgressBarsManager
from cosmic_event.gui.impl.battle.cosmic_hud.vehicle_markers_manager import VehicleMarkersManager
from cosmic_event.gui.impl.battle.cosmic_hud.poi_markers_manager import CosmicPOIMarkersManager
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.ability_model import AbilityModel, Ability
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.cosmic_hud_view_model import CosmicHudViewModel, AnnouncementTypeEnum, ArenaPhaseEnum
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.player_record_model import PlayerRecordModel
from constants import SERVER_TICK_LENGTH, ARENA_PERIOD, EQUIPMENT_STAGES
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.scoring_model import ScoringTypeEnum
from cosmic_event.gui.shared.events import ArtifactScanningEvent, LootEvent, CosmicVehicleEvent
from cosmic_event.settings import HINTS
from cosmic_event_common.cosmic_constants import BATTLE_EVENT_TYPE, COSMIC_EVENT_RAPIDSHELLING, COSMIC_EVENT_OVERCHARGE, COSMIC_EVENT_TELEPORT, LOOT_ITEM_ID, LOOT_STATE
from cosmic_sound import CosmicBattleSounds, playVoiceover
from debug_utils import LOG_ERROR
from frameworks.wulf import ViewFlags, ViewSettings
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE, EventPriority
from gui.shared.utils.key_mapping import getReadableKey
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from helpers.CallbackDelayer import CallbackDelayer
from helpers import dependency, time_utils
from items.vehicles import g_cache
from skeletons.gui.battle_session import IBattleSessionProvider, IArenaDataProvider
from cosmic_event.gui.battle_control.controllers.consumables.equipment_ctrl import ExtraEquipmentTags
from cosmic_event.gui.impl.battle.cosmic_hud.tooltips.ability_tooltip import AbilityTooltip
from skeletons.gui.game_control import ICosmicEventBattleController
from PlayerEvents import g_playerEvents
from cosmic_event.gui.gui_constants import ABILITY_TYPE_BY_EQUIP_NAME
from cosmic_event.cosmic_constants import COSMIC_VEHICLES_ROVER_ENUM
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.direction_marker_model import DirectionMarkerType
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.cosmic_progress_bar import ProgressBarType
UPDATE_TICK_LENGTH = SERVER_TICK_LENGTH
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Iterator, Sequence, Tuple, TypeVar, Callable, Optional, Any, Dict
    from Event import Event
    from gui.battle_control.controllers.consumables.equipment_ctrl import _VisualScriptItem
    from cosmic_event.gui.battle_control.controllers.consumables.equipment_ctrl import CosmicEquipmentsController
    from gui.battle_control.controllers.consumables.ammo_ctrl import ReloadingTimeSnapshot, AmmoController
    from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
    from gui.battle_control.controllers.interfaces import IBattleController
    from gui.battle_control.controllers.vehicle_state_ctrl import VehicleStateController
    from gui.battle_control.controllers.feedback_adaptor import BattleFeedbackAdaptor
    from gui.battle_control.controllers.feedback_events import PlayerFeedbackEvent
    from cosmic_event.settings import Goal
    from CosmicLoot import CosmicLoot
    BattleControllerType = TypeVar('BattleControllerType', bound=IBattleController)
SCORE_EVENT_IDS = {BATTLE_EVENT_TYPE.COSMIC_SHOT: ScoringTypeEnum.SHOT,
 BATTLE_EVENT_TYPE.COSMIC_ABILITY_HIT: ScoringTypeEnum.ABILITYHIT,
 BATTLE_EVENT_TYPE.COSMIC_PICKUP_ABILITY: ScoringTypeEnum.PICKUP,
 BATTLE_EVENT_TYPE.COSMIC_ARTIFACT_SCAN: ScoringTypeEnum.SCAN,
 BATTLE_EVENT_TYPE.COSMIC_KILL: ScoringTypeEnum.KILL,
 BATTLE_EVENT_TYPE.COSMIC_RAMMING: ScoringTypeEnum.RAM,
 BATTLE_EVENT_TYPE.COSMIC_ASSIST: ScoringTypeEnum.ASSIST,
 BATTLE_EVENT_TYPE.COSMIC_FIRST_BLOOD: ScoringTypeEnum.FIRSTBLOOD,
 BATTLE_EVENT_TYPE.COSMIC_KILL_STREAK: ScoringTypeEnum.KILLSTREAK,
 BATTLE_EVENT_TYPE.LOOT_RESEARCHING: ScoringTypeEnum.LOOTRESEARCHING,
 BATTLE_EVENT_TYPE.LOOT_RESEARCHING_DONE: ScoringTypeEnum.LOOTRESEARCHINGDONE,
 BATTLE_EVENT_TYPE.LOOT_RESEARCHABLE_PICK_UP: ScoringTypeEnum.LOOTRESEARCHABLEPICKUP}
_EXPIRING_ABILITIES = (COSMIC_EVENT_TELEPORT,)
_AMMO_START_IDX = 0
_AMMO_COUNT = 1
_EQUIPMENT_START_IDX = _AMMO_START_IDX + _AMMO_COUNT
_EQUIPMENT_COUNT = 2
_PICKUP_START_IDX = _EQUIPMENT_START_IDX + _EQUIPMENT_COUNT
_PICKUP_COUNT = 1
_TOTAL_ABILITIES = _AMMO_COUNT + _EQUIPMENT_COUNT + _PICKUP_COUNT
_NO_BINDING = ''
_DO_ONCE = -1

def _getArenaScoreComponent():
    player = BigWorld.player()
    if player and player.arena is not None:
        arenaInfo = player.arena.arenaInfo
        if arenaInfo:
            return arenaInfo.dynamicComponents.get('ArenaInfoScoreSystemComponent', None)
    return


class CosmicHudView(ViewImpl):
    __slots__ = ('__callbackDelayer', '_vehMarkersMan', '__poiMarkersManager', '__poiMarkers', '__progressBarsManager', '__researchingPlayerNames', '_currentGoal', '__progressBars', '_respawnAnnouncement', '_shootingAbilityCD', '_isShootingAbilityActive', '_markersCtrl', '_period')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    cosmicController = dependency.descriptor(ICosmicEventBattleController)

    def __init__(self):
        settings = ViewSettings(R.views.cosmic_event.battle.cosmic_hud.CosmicReactHudView(), ViewFlags.VIEW, CosmicHudViewModel())
        super(CosmicHudView, self).__init__(settings)
        self.__callbackDelayer = CallbackDelayer()
        self._markersCtrl = GUI.MarkerPositionController()
        self._vehMarkersMan = VehicleMarkersManager(self.viewModel.getVehicleMarkers(), weakref.proxy(self._markersCtrl))
        self.__poiMarkersManager = CosmicPOIMarkersManager(self.viewModel.getPoiMarkers(), weakref.proxy(self._markersCtrl))
        self.__progressBarsManager = CosmicProgressBarsManager(self.viewModel.getProgressBars())
        self.__progressBars = {}
        self.__researchingPlayerNames = set()
        self._currentGoal = None
        self._respawnAnnouncement = None
        self._shootingAbilityCD = None
        self._isShootingAbilityActive = False
        self._period = ARENA_PERIOD.IDLE
        return

    @property
    def viewModel(self):
        return super(CosmicHudView, self).getViewModel()

    @property
    def currentGoal(self):
        return self._respawnAnnouncement if self._respawnAnnouncement is not None else self._currentGoal

    @property
    def vehicleID(self):
        player = BigWorld.player()
        return player.playerVehicleID

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.cosmic_event.battle.cosmic_hud.tooltips.AbilityTooltip():
            ability = event.getArgument('ability')
            return AbilityTooltip(ability=ability)
        return super(CosmicHudView, self).createToolTipContent(event, contentID)

    def setPeriod(self, period):
        if period == ARENA_PERIOD.PREBATTLE:
            self._currentGoal = AnnouncementGoal(HINTS.get(AnnouncementTypeEnum.PREBATTLE.value), {'param2': 'True'})
        elif period == ARENA_PERIOD.BATTLE:
            playVoiceover(CosmicBattleSounds.START_BATTLE)
            CosmicBattleSounds.startBattlePeriodMusic()
            with self.viewModel.transaction() as transaction:
                transaction.setArenaPhase(ArenaPhaseEnum.PHASE1)
                self._clearCurrentGoal(transaction=transaction)
                self._updateAnnouncement(transaction)
        elif period == ARENA_PERIOD.AFTERBATTLE:
            CosmicBattleSounds.startAfterBattlePeriodMusic()
            playerPosInRankedTable = self.__getPlayerPositionInRankedTable()
            CosmicBattleSounds.playAfterBattleResultVoice(playerPosInRankedTable)
            with self.viewModel.transaction() as transaction:
                self._clearCurrentGoal(transaction=transaction)
                transaction.setAnnouncementType(AnnouncementTypeEnum.MISSIONCOMPLETED)
        self.__stopPeriodTimer(self._period)
        self.__startPeriodTimer(period)
        self._period = period

    def showHint(self, hint, data=None):
        if self._currentGoal is not None and self._currentGoal.type in [AnnouncementTypeEnum.SCANNING, AnnouncementTypeEnum.SCANAVAILABLE, AnnouncementTypeEnum.FINALSCANAVAILABLE] and not self._currentGoal.ended:
            _logger.warning('Tried to show hint while scanning event is in progress.')
            return
        else:
            self._currentGoal = getAnnouncementType(hint, data)
            if self._currentGoal.type is AnnouncementTypeEnum.PREPARETOSCANFINAL:
                playVoiceover(CosmicBattleSounds.ScanningZone.SCANNING_ZONE_FINAL_PREPARING)
            return

    def _onLoading(self, *args, **kwargs):
        super(CosmicHudView, self)._onLoading(*args, **kwargs)
        CosmicBattleSounds.ScanningZone.switchInactiveState()
        crosshair = self.sessionProvider.shared.crosshair
        aimPos = crosshair.getPosition()
        self._onCrosshairPositionChanged(aimPos[0], aimPos[1])
        self._vehMarkersMan.start()
        gunMarkersSetInfo = crosshair.getGunMarkersSetInfo()
        self._markersCtrl.add(self.viewModel.crosshair.proxy, gunMarkersSetInfo.clientMarkerDataProvider.positionMatrixProvider)
        arenaDP = self.sessionProvider.getArenaDP()
        playerVehicleInfo = arenaDP.getVehicleInfo()
        playerName = playerVehicleInfo.player.name
        self.viewModel.setPlayerName(playerName if playerName is not None else '')
        self._updatePlayerListModel()
        self._currentGoal = AnnouncementGoal(HINTS.get(AnnouncementTypeEnum.AWAITINGPLAYERS.value), {})
        self.viewModel.setAnnouncementType(AnnouncementTypeEnum.AWAITINGPLAYERS)
        self.viewModel.setArenaPhase(ArenaPhaseEnum.PREBATTLE)
        abilitiesArray = self.viewModel.getAbilities()
        abilitiesArray.reserve(_TOTAL_ABILITIES)
        for i in range(_TOTAL_ABILITIES):
            model = AbilityModel()
            self._clearSlot(model)
            model.setKeyBind(self._getKeyString(i))
            abilitiesArray.addViewModel(model)

        self._updateSelectedVehicle()
        _logger.info('HUD: onLoading')
        return

    def _finalize(self):
        self.__stopCallbackDelayer()
        self._markersCtrl.clear()
        self._vehMarkersMan.stop()
        self.__poiMarkersManager.stop()
        self.__progressBarsManager.stop()
        self.__poiMarkersManager = None
        self.__progressBarsManager = None
        super(CosmicHudView, self)._finalize()
        return

    def _getListeners(self):
        listeners = [(ArtifactScanningEvent.VEHICLES_IN_ZONE_CHANGED,
          self._onScanningVehiclesChanged,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH),
         (ArtifactScanningEvent.ANNOUNCEMENT_CREATED, self._onArtifactAnnouncementCreated, EVENT_BUS_SCOPE.BATTLE),
         (ArtifactScanningEvent.ARTIFACT_SCANNING_READY, self._onArtifactCreated, EVENT_BUS_SCOPE.BATTLE),
         (ArtifactScanningEvent.ARTIFACT_DESTROYED, self._onArtifactDestroyed, EVENT_BUS_SCOPE.BATTLE),
         (LootEvent.PREPARING, self._onLootPreparing, EVENT_BUS_SCOPE.BATTLE),
         (LootEvent.SPAWNED, self._onLootSpawned, EVENT_BUS_SCOPE.BATTLE),
         (LootEvent.PICKED_UP, self._onLootPickedUp, EVENT_BUS_SCOPE.BATTLE),
         (LootEvent.DESTROYED, self._onLootDestroyed, EVENT_BUS_SCOPE.BATTLE),
         (CosmicVehicleEvent.START_LOOT_RESEARCHING, self._onLootResearchingStarted, EVENT_BUS_SCOPE.BATTLE),
         (CosmicVehicleEvent.STOP_LOOT_RESEARCHING, self._onLootResearchingStopped, EVENT_BUS_SCOPE.BATTLE)]
        return listeners

    def _getEvents(self):
        events = [(CommandMapping.g_instance.onMappingChanged, self._onMappingChanged)]
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            events.extend(((eqCtrl.onEquipmentCooldownTime, self._onEquipmentReloadTimeSet),
             (eqCtrl.onEquipmentAdded, self._onEquipmentAdded),
             (eqCtrl.onEquipmentRemoved, self._onEquipmentRemoved),
             (eqCtrl.onEquipmentUpdated, self._onEquipmentUpdated),
             (eqCtrl.onEquipmentsCleared, self._onClearEquipment)))
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            events.extend(((ammoCtrl.onGunReloadTimeSet, self._onGunReloadTimeSet), (ammoCtrl.onShellsAdded, self._onShellsAdded)))
        crosshair = self.sessionProvider.shared.crosshair
        if crosshair is not None:
            events.append((crosshair.onCrosshairPositionChanged, self._onCrosshairPositionChanged))
        arenScoreComp = _getArenaScoreComponent()
        if arenScoreComp:
            events.append((arenScoreComp.onArenaScoreUpdated, self.__onArenaScoreChanged))
        respawnCtrl = self.sessionProvider.dynamic.respawn
        if respawnCtrl is not None:
            events.append((respawnCtrl.onVehicleDeployed, self.__onVehicleDeployed))
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            events.append((vehicleCtrl.onVehicleStateUpdated, self._onVehicleStateUpdated))
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl is not None:
            events.append((feedbackCtrl.onPlayerFeedbackReceived, self._onPlayerFeedbackReceived))
            events.append((feedbackCtrl.onVehicleFeedbackReceived, self.__onVehicleFeedbackReceived))
        events.append((g_playerEvents.onAvatarReady, self.__onAvatarReady))
        return events

    def _updatePlayerListModel(self, totalScore=None):
        if totalScore is None:
            totalScore = self.__getArenaScore()
        arenaDP = self.sessionProvider.getArenaDP()
        vehicles = arenaDP.getVehiclesInfoIterator()
        scoreList = [ (totalScore.get(vInfo.vehicleID, 0), (vInfo.player.name, vInfo.player.clanAbbrev), vInfo.vehicleID) for vInfo in vehicles ]
        scoreList.sort(reverse=True)
        with self.viewModel.transaction() as model:
            playerList = model.getPlayerList()
            playerList.clear()
            playerList.reserve(len(scoreList))
            for scoreItem in scoreList:
                vehicleId = scoreItem[2]
                model = PlayerRecordModel()
                model.setName(scoreItem[1][0] if scoreItem[1] else '')
                model.setClanAbbrev(scoreItem[1][1] if scoreItem[1] else '')
                model.setScore(scoreItem[0])
                model.setLootResearching(scoreItem[1][0] in self.__researchingPlayerNames)
                vehicle = BigWorld.entity(vehicleId)
                if vehicle is not None:
                    name = vehicle.typeDescriptor.name
                    model.setVehicle(COSMIC_VEHICLES_ROVER_ENUM.get(name, COSMIC_VEHICLES_ROVER_ENUM['default']))
                playerList.addViewModel(model)

            playerList.invalidate()
        return

    def _updateSelectedVehicle(self):
        with self.viewModel.transaction() as model:
            model.setSelectedVehicleID(self.cosmicController.selectedVehicleID)

    def _updateArenaTimer(self, transaction):
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        remainingTime = periodCtrl.getEndTime() - BigWorld.serverTime()
        period = periodCtrl.getPeriod()
        if period == ARENA_PERIOD.BATTLE:
            transaction.setArenaTimeLeft(remainingTime)

    def _updateAnnouncement(self, transaction):
        if self.currentGoal is not None:
            self.currentGoal.updateAnnouncement(transaction)
        return

    def _clearCurrentGoal(self, transaction=None):
        if self._currentGoal is None:
            return
        else:
            self._currentGoal.endAnnouncement(transaction)
            self._currentGoal = None
            return

    def _onCrosshairPositionChanged(self, posx, posy):
        aimModel = self.viewModel.aim
        with aimModel.transaction() as model:
            model.setPosx(posx)
            model.setPosy(posy)

    def _onKillStreakChanged(self, killStreak):
        CosmicBattleSounds.playKillStreak(killStreak)
        aimModel = self.viewModel.aim
        with aimModel.transaction() as model:
            model.setKillStreak(killStreak)

    def _onShellsAdded(self, intCD, descriptor, *args):
        _logger.debug('Shell added: %s, %s', str(intCD), descriptor)
        idx = self._getAmmoIdx(intCD)
        if idx is None:
            return
        else:
            self.__addShell(idx)
            return

    def _onGunReloadTimeSet(self, intCD, state, skipAutoLoader):
        _logger.debug('Reload: %s, %s, %d', str(intCD), str(state), skipAutoLoader)
        timeLeft = state.getTimeLeft()
        reloadTime = state.getBaseValue()
        idx = self._getAmmoIdx(intCD)
        if idx is None:
            return
        else:
            with self.viewModel.transaction() as model:
                model.setReloadTimeLeft(timeLeft)
                model.setReloadTime(reloadTime)
                abilityArray = model.getAbilities()
                abilityModel = abilityArray[idx]
                abilityModel.setReloadTime(reloadTime)
                abilityModel.setReloadTimeLeft(timeLeft)
                if self._isShootingAbilityActive:
                    abilityModel.setReloadTimeLeft(0)
                    shootingIdx = self._getEquipmentIdx(self._shootingAbilityCD)
                    shootingModel = abilityArray[shootingIdx]
                    shootingModel.setReloadTime(reloadTime)
                    shootingModel.setReloadTimeLeft(timeLeft)
            return

    def _onEquipmentReloadTimeSet(self, intCD, timeLeft, isBaseTime, isFinish):
        _logger.debug('Reload equipment: %s, %s, %d, %d', str(intCD), timeLeft, isBaseTime, isFinish)
        idx = self._getEquipmentIdx(intCD)
        if idx is None:
            return
        else:
            self.__updateReload(idx, isBaseTime, timeLeft)
            return

    def _onEquipmentUpdated(self, intCD, item):
        timeLeft = item.getTimeRemaining()
        maxTime = item.getTotalTime()
        stage = item.getStage()
        _logger.debug('Equipment updated: intCD: %s, name: %s, timeLeft: %s, maxtime: %s, stage: %s, quantity: %s', str(intCD), item.getDescriptor().name, timeLeft, maxTime, stage, item.getQuantity())
        idx = self._getEquipmentIdx(intCD)
        if idx is None:
            return
        else:
            if self._isShootingAbility(intCD) and stage == EQUIPMENT_STAGES.ACTIVE:
                self._isShootingAbilityActive = True
                abilityModel = self.viewModel.getAbilities()[_AMMO_START_IDX]
                abilityModel.setIsEnabled(False)
            if ExtraEquipmentTags.TARGETING in item.getTags():
                self.__updateAbilityPanelTargeting(idx, stage)
                self.viewModel.setIsTargeting(stage == EQUIPMENT_STAGES.PREPARING)
            self.__updateAbilityLifetime(item, stage, idx)
            self.__updateEquipmentReload(idx, stage, timeLeft, maxTime)
            return

    def _isShootingAbility(self, intCD):
        return intCD == self._shootingAbilityCD

    def _onEquipmentAdded(self, intCD, item):
        equipmentName = item.getDescriptor().name
        _logger.debug('Equipment added: intCD %s, name: %s, quantity: %s, totalTime: %s, stage: %s', str(intCD), equipmentName, item.getQuantity(), item.getTotalTime(), item.getStage())
        if equipmentName == COSMIC_EVENT_RAPIDSHELLING:
            self._shootingAbilityCD = intCD
        if equipmentName == COSMIC_EVENT_RAPIDSHELLING or equipmentName == COSMIC_EVENT_OVERCHARGE:
            self.viewModel.setAbilityDuration(item.getDescriptor().duration)
        if equipmentName == COSMIC_EVENT_TELEPORT:
            self.viewModel.setAbilityDuration(item.getDescriptor().lifeTime)
        idx = self._getEquipmentIdx(intCD)
        if idx is None:
            return
        else:
            self.__addEquipment(idx, item, equipmentName)
            return

    def _onMappingChanged(self, *args):
        _logger.debug('Consumable panel: Updating key bindings.')
        with self.viewModel.transaction() as model:
            abilities = model.getAbilities()
            for i, ability in enumerate(abilities):
                ability.setKeyBind(self._getKeyString(i))

            abilities.invalidate()

    def _getKeyString(self, idx):
        if _AMMO_START_IDX <= idx < _EQUIPMENT_START_IDX:
            _logger.debug('Index is of an ammo slot, ammo slots should not have keybindings.')
            return _NO_BINDING
        relativeEquipmentIndex = idx - _EQUIPMENT_START_IDX
        command = CommandMapping.CMD_AMMO_CHOICE_1 + relativeEquipmentIndex
        if command > CommandMapping.CMD_AMMO_CHOICE_0:
            _logger.warning('No free command slots. Command: %s', command)
            return _NO_BINDING
        return getReadableKey(command)

    def _onEquipmentRemoved(self, intCD, item):
        _logger.debug('Equipment removed: %s, %s, %s', str(intCD), item.getDescriptor().name, item.getQuantity())
        if self._isShootingAbility(intCD):
            self._isShootingAbilityActive = False
            abilityModel = self.viewModel.getAbilities()[_AMMO_START_IDX]
            abilityModel.setIsEnabled(True)
        abilityType = ABILITY_TYPE_BY_EQUIP_NAME[item.getDescriptor().name]
        abilityArray = self.viewModel.getAbilities()
        for model in reversed(abilityArray):
            if model.getAbility() == abilityType:
                self._clearSlot(model)
                break

        abilityArray.invalidate()

    def _clearSlot(self, model):
        model.setIsActive(False)
        model.setAbility(Ability.NONE)
        model.setReloadTimeLeft(0)

    def _onClearEquipment(self):
        _logger.debug('clearing equipment from panel.')
        self._isShootingAbilityActive = False
        abilityArray = self.viewModel.getAbilities()
        for model in abilityArray:
            self._clearSlot(model)

        abilityArray.invalidate()

    def _getEquipmentIdx(self, intCD):
        eqCtrl = self.sessionProvider.shared.equipments
        idx = eqCtrl.getAbilityIndex(intCD)
        if idx is None:
            return
        else:
            idx += _EQUIPMENT_START_IDX
            if idx >= _TOTAL_ABILITIES:
                _logger.warning('Equipment %d at index %d. The index is out of the expected range. Equipment indices start at %d, total equipment slots %d', intCD, idx, _EQUIPMENT_START_IDX, _TOTAL_ABILITIES)
                return
            return idx

    def _getAmmoIdx(self, intCD):
        ammoCtrl = self.sessionProvider.shared.ammo
        if intCD not in ammoCtrl.getShellsOrderIter():
            _logger.warning('Shell %d cannot be found in ammo controller. Ammo list %s', intCD, ammoCtrl.getShellsLayout())
            return None
        idx = list(ammoCtrl.getShellsOrderIter()).index(intCD)
        idx += _AMMO_START_IDX
        if idx >= _AMMO_START_IDX + _AMMO_COUNT:
            _logger.info('Additional shell %d cannot be displayed in model. Model only displays %d shell(s).', intCD, _AMMO_COUNT)
            return None
        else:
            return idx

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DESTROY_TIMER:
            self.viewModel.setVehicleOverturned(avatar_getter.isVehicleOverturned())
        elif state == VEHICLE_VIEW_STATE.DEATH_INFO:
            self._respawnAnnouncement = _AnnouncementRespawn()
            with self.viewModel.transaction() as tx:
                self._updateAnnouncement(tx)
        elif state == VEHICLE_VIEW_STATE.DESTROYED or state == VEHICLE_VIEW_STATE.CREW_DEACTIVATED:
            self.viewModel.setIsRespawning(True)
            self._onKillStreakChanged(0)
        elif state == VEHICLE_VIEW_STATE.SWITCHING:
            self.viewModel.setIsRespawning(False)

    def _onPlayerFeedbackReceived(self, events):
        newMessages = []
        for event in events:
            eventType = event.getBattleEventType()
            if eventType in SCORE_EVENT_IDS:
                messageModel = self.viewModel.getMessagesType()()
                messageModel.setType(SCORE_EVENT_IDS.get(eventType))
                messageModel.setMarsPoints(event.getExtra())
                newMessages.append(messageModel)
                CosmicBattleSounds.playScoreNotification()
                if eventType == BATTLE_EVENT_TYPE.COSMIC_PICKUP_ABILITY:
                    CosmicBattleSounds.playAbilityPickup()
                elif eventType == BATTLE_EVENT_TYPE.COSMIC_FIRST_BLOOD or eventType == BATTLE_EVENT_TYPE.COSMIC_KILL:
                    playVoiceover(CosmicBattleSounds.KILL)
            if eventType == BATTLE_EVENT_TYPE.MAX_KILL_SERIES:
                self._onKillStreakChanged(event.getExtra())

        with self.viewModel.transaction() as model:
            messages = model.getMessages()
            messages.reserve(len(messages) + len(newMessages))
            for message in newMessages:
                messages.addViewModel(message)

            messages.invalidate()

    def _onScanningVehiclesChanged(self, event):
        self._setScanningVehicles(event)
        self._updateMarkerVisibility(event)

    def _setScanningVehicles(self, event):
        vehicles = event.ctx.get('vehicles')
        eventID = event.ctx.get('id')
        ctx = {'activePlayersCount': len(vehicles)}
        self.__progressBarsManager.updateProgressBar(eventID, ctx)

    def _updateMarkerVisibility(self, event):
        vehicles = event.ctx.get('vehicles')
        markerID = event.ctx.get('id')
        isMarkerVisible = self.__poiMarkersManager.isMarkerVisible(markerID)
        if self.vehicleID in vehicles and isMarkerVisible:
            self.__poiMarkersManager.setMarkerVisibility(markerID, False)
        elif self.vehicleID not in vehicles and not isMarkerVisible:
            self.__poiMarkersManager.setMarkerVisibility(markerID, True)

    def _onArtifactAnnouncementCreated(self, event):
        eventID = event.ctx.get('id')
        markerType = DirectionMarkerType.ARTIFACT_ZONE
        self.__poiMarkersManager.createMarker(event.ctx.get('position'), markerType, eventID)

    def _onArtifactCreated(self, event):
        eventID = event.ctx.get('id')
        CosmicBattleSounds.ScanningZone.setActive(event.ctx.get('isLastOne', False))
        ctx = {'totalTime': event.ctx.get('duration', 0),
         'timeLeft': max(event.ctx.get('endLifeTime', 0) - BigWorld.serverTime(), 0)}
        self.__progressBarsManager.createProgressBar(ProgressBarType.ARTIFACT_ZONE, eventID, ctx)

    def _onArtifactDestroyed(self, event):
        eventID = event.ctx.get('id')
        isLast = event.ctx.get('isLastOne', False)
        CosmicBattleSounds.ScanningZone.setInactive(isLast)
        self.__poiMarkersManager.destroyMarker(eventID)
        self.__progressBarsManager.destroyProgressBar(eventID)

    def _onLootPreparing(self, event):
        loot = event.ctx.get('loot')
        if not loot:
            _logger.error('LootEvent must contain information about loot.')
            return
        lootItemID = loot.itemID
        if lootItemID != LOOT_ITEM_ID.COSMIC_CORAL:
            return
        markerType = DirectionMarkerType.CORAL
        lootPosition = loot.position
        markerID = loot.id
        self.__poiMarkersManager.createMarker(lootPosition, markerType, markerID)

    def _onLootSpawned(self, event):
        loot = event.ctx.get('loot')
        if not loot:
            _logger.error('LootEvent must contain information about loot.')
            return
        lootItemID = loot.itemID
        if lootItemID != LOOT_ITEM_ID.COSMIC_CORAL:
            return
        lifeTime = loot.lifeTime
        timeRemained = loot.lifeTimeRemained
        markerID = loot.id
        lootPosition = loot.position
        markerType = DirectionMarkerType.CORAL
        self.__poiMarkersManager.createMarker(lootPosition, markerType, markerID)
        self.__poiMarkersManager.setMarkerTimer(markerID, timeRemained)
        ctx = {'totalTime': lifeTime,
         'timeLeft': timeRemained}
        self.__progressBarsManager.createProgressBar(ProgressBarType.CORAL, loot.id, ctx)

    def _onLootPickedUp(self, event):
        loot = event.ctx.get('loot')
        if not loot:
            _logger.error('LootEvent must contain information about loot.')
            return
        lootItemID = loot.itemID
        if lootItemID != LOOT_ITEM_ID.COSMIC_CORAL:
            return
        markerID = loot.id
        self.__poiMarkersManager.destroyMarker(markerID)

    def _onLootDestroyed(self, event):
        loot = event.ctx.get('loot')
        if not loot:
            _logger.error('LootEvent must contain information about loot.')
            return
        lootItemID = loot.itemID
        markerID = loot.id
        if lootItemID != LOOT_ITEM_ID.COSMIC_CORAL:
            return
        self.__poiMarkersManager.destroyMarker(markerID)
        self.__progressBarsManager.destroyProgressBar(loot.id)

    def _onLootResearchingStarted(self, event):
        playerName = event.ctx.get('playerName')
        timeRemained = event.ctx.get('lifeTimeRemained', 0)
        if not playerName:
            _logger.error('START_LOOT_RESEARCHING must contain information about playerName.')
            return
        self.__researchingPlayerNames.add(playerName)
        self._updatePlayerListModel()
        self._vehMarkersMan.setResearchingState(playerName, True)
        self._vehMarkersMan.setTimeRemained(playerName, timeRemained)
        if BigWorld.player().name == playerName:
            self.__showOwnResearchIcon(timeRemained)

    def _onLootResearchingStopped(self, event):
        playerName = event.ctx.get('playerName')
        if not playerName:
            _logger.error('STOP_LOOT_RESEARCHING must contain information about playerName.')
            return
        self.__researchingPlayerNames.discard(playerName)
        self._updatePlayerListModel()
        self._vehMarkersMan.setResearchingState(playerName, False)
        if BigWorld.player().name == playerName:
            self.__hideOwnResearchIcon()

    def __showOwnResearchIcon(self, timeRemained):
        self.viewModel.superLootScanning.setIsVisible(True)
        if timeRemained <= 0:
            return
        self.viewModel.superLootScanning.setTimeLeft(timeRemained)
        timeRemained -= 1
        self.__callbackDelayer.delayCallback(time_utils.ONE_SECOND, functools.partial(self.__onResearchIconTick, timeRemained))

    def __onResearchIconTick(self, timeRemained):
        if timeRemained <= 0 or not self.viewModel.superLootScanning.getIsVisible():
            return
        self.viewModel.superLootScanning.setTimeLeft(timeRemained)
        timeRemained -= 1
        self.__callbackDelayer.delayCallback(time_utils.ONE_SECOND, functools.partial(self.__onResearchIconTick, timeRemained))

    def __hideOwnResearchIcon(self):
        self.viewModel.superLootScanning.setIsVisible(False)
        self.viewModel.superLootScanning.setTimeLeft(0)

    def __startPeriodTimer(self, period):
        cd = self.__callbackDelayer
        if period == ARENA_PERIOD.PREBATTLE or period == ARENA_PERIOD.BATTLE:
            if not cd.hasDelayedCallback(self.__onSecond):
                self.__onSecond()
                cd.delayCallback(time_utils.ONE_SECOND, self.__onSecond)

    def __stopPeriodTimer(self, period):
        if period == ARENA_PERIOD.BATTLE:
            self.__callbackDelayer.stopCallback(self.__onSecond)

    def __stopCallbackDelayer(self):
        self.__callbackDelayer.clearCallbacks()

    def __addShell(self, idx):
        abilityArray = self.viewModel.getAbilities()
        if idx >= len(abilityArray):
            _logger.warning('Index is out of range for the abilities array. Array length: %s, Expected number of abilities %s', len(abilityArray), _TOTAL_ABILITIES)
            return
        abilityModel = abilityArray[idx]
        abilityModel.setReloadTime(0)
        abilityModel.setAbility(Ability.SHELL)
        abilityModel.setReloadTimeLeft(0)
        abilityModel.setIsActive(False)
        abilityModel.setKeyBind('')
        abilityArray.invalidate()

    def __updateReload(self, idx, isBaseTime, timeLeft):
        abilityArray = self.viewModel.getAbilities()
        if idx >= len(abilityArray):
            _logger.warning('Index is out of range for the abilities array. Array length: %s, Expected number of abilities %s', len(abilityArray), _TOTAL_ABILITIES)
            return
        abilityModel = abilityArray[idx]
        if isBaseTime:
            abilityModel.setReloadTime(timeLeft)
            abilityModel.setReloadTimeLeft(0)
        else:
            abilityModel.setReloadTimeLeft(timeLeft)
        abilityArray.invalidate()

    def __updateAbilityPanelTargeting(self, idx, stage):
        abilityArray = self.viewModel.getAbilities()
        if idx >= len(abilityArray):
            _logger.warning('Index is out of range for the abilities array. Array length: %s, Expected number of abilities %s', len(abilityArray), _TOTAL_ABILITIES)
            return
        abilityModel = abilityArray[idx]
        abilityModel.setIsTargeting(stage == EQUIPMENT_STAGES.PREPARING)
        abilityArray.invalidate()

    def __updateEquipmentReload(self, idx, stage, timeLeft, maxTime):
        abilityArray = self.viewModel.getAbilities()
        if idx >= len(abilityArray):
            _logger.warning('Index is out of range for the abilities array. Array length: %s, Expected number of abilities %s', len(abilityArray), _TOTAL_ABILITIES)
            return
        abilityModel = abilityArray[idx]
        abilityModel.setIsActive(stage == EQUIPMENT_STAGES.ACTIVE)
        if stage == EQUIPMENT_STAGES.COOLDOWN:
            abilityModel.setReloadTimeLeft(timeLeft)
            abilityModel.setReloadTime(maxTime)
        if stage == EQUIPMENT_STAGES.READY:
            abilityModel.setReloadTimeLeft(0)
        abilityArray.invalidate()

    def __addEquipment(self, idx, item, equipmentName):
        abilityArray = self.viewModel.getAbilities()
        if idx >= len(abilityArray):
            _logger.warning('Index is out of range for the abilities array. Array length: %s, Expected number of abilities %s', len(abilityArray), _TOTAL_ABILITIES)
            return
        abilityModel = abilityArray[idx]
        abilityModel.setReloadTime(item.getTotalTime())
        abilityModel.setAbility(ABILITY_TYPE_BY_EQUIP_NAME[equipmentName])
        abilityModel.setReloadTimeLeft(0)
        abilityModel.setIsActive(False)
        abilityArray.invalidate()

    @staticmethod
    def __getArenaScore():
        arenScoreComp = _getArenaScoreComponent()
        return {} if arenScoreComp is None else arenScoreComp.totalScore

    def __onVehicleDeployed(self):
        self._respawnAnnouncement = None
        with self.viewModel.transaction() as model:
            model.setIsTargeting(False)
            if self._currentGoal is not None and self._currentGoal.type == AnnouncementTypeEnum.AWAITINGPLAYERS:
                return
            model.setAnnouncementType(AnnouncementTypeEnum.NONE)
            model.setAnnouncementSecondsToEvent(-1)
        return

    def __onArenaScoreChanged(self, totalScore):
        self._updatePlayerListModel(totalScore)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, _):
        if eventID == FEEDBACK_EVENT_ID.ENTITY_IN_FOCUS:
            vehicle = BigWorld.entity(vehicleID)
            if vehicle is not None:
                vehicle.removeEdge()
        return

    def __getPlayerPositionInRankedTable(self):
        totalScore = self.__getArenaScore()
        arenaDP = self.sessionProvider.getArenaDP()
        vehicles = arenaDP.getVehiclesInfoIterator()
        scoreList = [ (totalScore.get(vInfo.vehicleID, 0), vInfo.player.name) for vInfo in vehicles ]
        scoreList.sort(reverse=True)
        playerName = arenaDP.getVehicleInfo().player.name
        for index, playerScore in enumerate(scoreList, 1):
            if playerScore[1] == playerName:
                return index

        LOG_ERROR('[COSMIC] Incorrect player position in a ranked table')

    def __onSecond(self):
        with self.viewModel.transaction() as model:
            self._updateArenaTimer(model)
            self._updateAnnouncement(model)
        return time_utils.ONE_SECOND

    def __updateAbilityLifetime(self, item, stage, idx):
        equipmentName = item.getDescriptor().name
        eqID = g_cache.equipmentIDs().get(equipmentName)
        equipment = g_cache.equipments().get(eqID) if eqID else None
        lifeTime = equipment.lifeTime if equipment and hasattr(equipment, 'lifeTime') else 0.0
        if stage == EQUIPMENT_STAGES.ACTIVE and equipmentName in _EXPIRING_ABILITIES:
            abilityArray = self.viewModel.getAbilities()
            abilityModel = abilityArray[idx]
            abilityModel.setReloadTime(lifeTime)
            abilityModel.setReloadTimeLeft(lifeTime)
            abilityArray.invalidate()
        return

    def __onAvatarReady(self):
        if self._period != ARENA_PERIOD.BATTLE:
            return
        for loot in BigWorld.entities.valuesOfType('CosmicLoot'):
            if loot.itemID == LOOT_ITEM_ID.COSMIC_CORAL:
                self.__updateCoralInfoOnReconnect(coralEntity=loot)

    def __updateCoralInfoOnReconnect(self, coralEntity):
        ctx = {'totalTime': coralEntity.lifeTime,
         'timeLeft': coralEntity.lifeTimeRemained}
        if coralEntity.state == LOOT_STATE.SPAWNED:
            self.__progressBarsManager.createProgressBar(ProgressBarType.CORAL, coralEntity.id, ctx)
            self.__poiMarkersManager.createMarker(coralEntity.position, DirectionMarkerType.CORAL, coralEntity.id)
            self.__poiMarkersManager.setMarkerTimer(coralEntity.id, coralEntity.lifeTimeRemained)
        else:
            self.__progressBarsManager.createProgressBar(ProgressBarType.CORAL, coralEntity.id, ctx)
