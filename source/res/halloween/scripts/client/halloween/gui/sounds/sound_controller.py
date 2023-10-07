# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/sounds/sound_controller.py
import BigWorld
import BattleReplay
import SoundGroups
from halloween_common.halloween_constants import ARENA_BONUS_TYPE as BONUS
from Math import Matrix
from constants import EQUIPMENT_STAGES, ARENA_PERIOD
from items import vehicles
from helpers import dependency, isPlayerAvatar
from TeamBaseRecapturable import ITeamBasesRecapturableListener
from gui.prb_control.entities.listener import IGlobalListener
from halloween.gui.halloween_gui_constants import FUNCTIONAL_FLAG
from gui.Scaleform.daapi.view.lobby.image_view.image_view import ImageView
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AirDropEvent, LootEvent
from gui.battle_control.avatar_getter import getSoundNotifications
from halloween.hw_constants import INVALID_PHASE_INDEX
from halloween.gui.sounds.sound_constants import SoundLanguage, WitchesVO, HangarEvents, BattleEvents, MAGIC_BOOK_BG, TeamBasesVO, BattleEndVO
from halloween.gui.Scaleform.daapi.view.battle.consumables_panel import HWConsumablesPanel
from halloween.skeletons.gui.sound_controller import IHWSoundController
from skeletons.gui.game_control import IHalloweenController
from constants import CURRENT_REALM, IS_CHINA
from skeletons.gui.battle_session import IBattleSessionProvider
from PlayerEvents import g_playerEvents
from halloween.gui.halloween_gui_constants import HW_EQUIPMENT
_POINTS_EQUIL_EPSILON = 0.05

class HWSoundController(IHWSoundController, IGlobalListener, ITeamBasesRecapturableListener):
    _hwController = dependency.descriptor(IHalloweenController)
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    HW_ITEM_TAG = 'halloween_equipment'
    HW_EQUIPMENT_SOUNDS = {HW_EQUIPMENT.LAUGH_ARROW: BattleEvents.EQUIPMENT_LAUGH_ARROW,
     HW_EQUIPMENT.FIRE_ARROW: BattleEvents.EQUIPMENT_FIRE_ARROW,
     HW_EQUIPMENT.FROZEN_ARROW: BattleEvents.EQUIPMENT_FROZEN_ARROW,
     HW_EQUIPMENT.CURSE_ARROW: BattleEvents.EQUIPMENT_CURSE_ARROW,
     HW_EQUIPMENT.HEALING_ARROW: BattleEvents.EQUIPMENT_HEALING_ARROW}

    def __init__(self, *args, **kwargs):
        super(HWSoundController, self).__init__(*args, **kwargs)
        self.__airDropPlacementSoundObjects = {}
        self.__soundInteractiveController = None
        self.__statsController = None
        self.__activePhaseIndex = INVALID_PHASE_INDEX
        self.__activeEquipment = set()
        return

    def registerStatsController(self, controller):
        self.__statsController = controller

    def invalidateStatsController(self):
        self.__statsController = None
        return

    def onLobbyInited(self, event):
        self.startGlobalListening()
        ImageView.onImageViewOpened += self.__onImageViewOpened
        ImageView.onImageViewClosed += self.__onImageViewClosed
        isEvent = bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.HALLOWEEN_BATTLE)
        if isEvent:
            SoundGroups.g_instance.playSound2D(HangarEvents.HW_ENTER)

    def onAccountBecomePlayer(self):
        self._hwController.onSyncCompleted += self.__onHWSyncCompleted

    def onAccountBecomeNonPlayer(self):
        self.stopGlobalListening()
        ImageView.onImageViewOpened -= self.__onImageViewOpened
        ImageView.onImageViewClosed -= self.__onImageViewClosed
        self._hwController.onSyncCompleted -= self.__onHWSyncCompleted

    def onPrbEntitySwitched(self):
        isEvent = bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.HALLOWEEN_BATTLE)
        if isEvent:
            SoundGroups.g_instance.playSound2D(HangarEvents.HW_ENTER)
        else:
            SoundGroups.g_instance.playSound2D(HangarEvents.HW_EXIT)

    def onAvatarBecomePlayer(self):
        if not self.__isEventBattle():
            return
        else:
            g_playerEvents.onAvatarBecomeNonPlayer += self.onAvatarBecomeNonPlayer
            self.__switchEventBattlePhase()
            self._hwController.phases.onArenaActivePhaseChanged += self.__onArenaActivePhaseChanged
            equipmentsCtrl = self._sessionProvider.shared.equipments
            if equipmentsCtrl is not None:
                equipmentsCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
            HWConsumablesPanel.onHandleEquipmentPressed += self._onHandleEquipmentPressed
            vehicleCtrl = self._sessionProvider.shared.vehicleState
            if vehicleCtrl is not None:
                vehicleCtrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
            player = BigWorld.player()
            if player is not None and hasattr(player, 'arena'):
                arena = player.arena
                if arena is not None:
                    arena.onVehicleKilled += self.__onVehicleKilled
            g_eventBus.addListener(AirDropEvent.AIR_DROP_SPAWNED, self.__onAirDropSpawned, scope=EVENT_BUS_SCOPE.BATTLE)
            g_eventBus.addListener(LootEvent.LOOT_SPAWNED, self.__onLootSpawned, scope=EVENT_BUS_SCOPE.BATTLE)
            g_eventBus.addListener(LootEvent.LOOT_PICKED_UP, self.__onLootPickedUp, scope=EVENT_BUS_SCOPE.BATTLE)
            g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
            teamBaseController = self._sessionProvider.dynamic.teamBaseRecapturable
            if teamBaseController is not None:
                teamBaseController.registerListener(self)
            self.__destroyInteractiveController()
            from halloween.gui.sounds.sound_interactive_controller import SoundInteractiveController
            self.__soundInteractiveController = SoundInteractiveController()
            self.__soundInteractiveController.onBattleEndWarningSound += self.__onBattleEndWarningSound
            if BattleReplay.g_replayCtrl.isPlaying:
                self.__setEventVoiceoverLanguage()
            return

    def onConnected(self):
        self.__setEventVoiceoverLanguage()
        self.__switchEventBattlePhase()

    def onAvatarBecomeNonPlayer(self):
        if not self.__isEventBattle():
            return
        else:
            g_playerEvents.onAvatarBecomeNonPlayer -= self.onAvatarBecomeNonPlayer
            self._hwController.phases.onArenaActivePhaseChanged -= self.__onArenaActivePhaseChanged
            equipmentsCtrl = self._sessionProvider.shared.equipments
            if equipmentsCtrl is not None:
                equipmentsCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
            HWConsumablesPanel.onHandleEquipmentPressed -= self._onHandleEquipmentPressed
            vehicleCtrl = self._sessionProvider.shared.vehicleState
            if vehicleCtrl is not None:
                vehicleCtrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
            player = BigWorld.player()
            if player is not None and hasattr(player, 'arena'):
                arena = player.arena
                if arena is not None:
                    arena.onVehicleKilled -= self.__onVehicleKilled
            g_eventBus.removeListener(AirDropEvent.AIR_DROP_SPAWNED, self.__onAirDropSpawned, scope=EVENT_BUS_SCOPE.BATTLE)
            g_eventBus.removeListener(LootEvent.LOOT_SPAWNED, self.__onLootSpawned, scope=EVENT_BUS_SCOPE.BATTLE)
            g_eventBus.removeListener(LootEvent.LOOT_PICKED_UP, self.__onLootPickedUp, scope=EVENT_BUS_SCOPE.BATTLE)
            g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
            teamBaseController = self._sessionProvider.dynamic.teamBaseRecapturable
            if teamBaseController is not None:
                teamBaseController.unregisterListener(self)
            self.__destroyInteractiveController()
            self.__activeEquipment.clear()
            return

    def onVehicleBeingAttacked(self, victimID, attackerID, newHealth):
        if self.__soundInteractiveController is not None:
            self.__soundInteractiveController.onVehicleBeingAttacked(victimID, attackerID, newHealth)
        return

    def switchSoundPhase(self, phase):
        self.__switchEventBattlePhase(phase)

    def _onHandleEquipmentPressed(self, intCD):
        ctrl = self._sessionProvider.shared.equipments
        if ctrl is None:
            return
        else:
            item = ctrl.getEquipment(intCD)
            if self.HW_ITEM_TAG in item.getTags() and item.getStage() == EQUIPMENT_STAGES.COOLDOWN:
                SoundGroups.g_instance.playSound2D(BattleEvents.EQUIPMENT_NOT_READY)
            return

    def __setEventVoiceoverLanguage(self):
        if IS_CHINA:
            SoundGroups.g_instance.setSwitch(SoundLanguage.VOICEOVER_LOCALIZATION_SWITCH, SoundLanguage.VOICEOVER_CN)
        elif CURRENT_REALM in SoundLanguage.RU_VOICEOVER_REALM_CODES:
            SoundGroups.g_instance.setSwitch(SoundLanguage.VOICEOVER_LOCALIZATION_SWITCH, SoundLanguage.VOICEOVER_RU)
        else:
            SoundGroups.g_instance.setSwitch(SoundLanguage.VOICEOVER_LOCALIZATION_SWITCH, SoundLanguage.VOICEOVER_EN)

    def __onHWSyncCompleted(self):
        self.__switchEventBattlePhase()

    def __onArenaActivePhaseChanged(self, newPhaseIndex):
        self.__switchEventBattlePhase(newPhaseIndex)

    def __switchEventBattlePhase(self, phaseIndex=None):
        if phaseIndex is not None:
            currentPhaseIndex = phaseIndex
        else:
            currentPhaseIndex = self._hwController.phases.getActivePhaseIndex()
        if currentPhaseIndex != INVALID_PHASE_INDEX and currentPhaseIndex != self.__activePhaseIndex:
            SoundGroups.g_instance.setSwitch(WitchesVO.GROUP, WitchesVO.getSwitch(currentPhaseIndex))
            self.__activePhaseIndex = currentPhaseIndex
        return

    def __onEquipmentUpdated(self, _, item):
        if self.HW_ITEM_TAG not in item.getTags() or item.getPrevStage() == item.getStage():
            return
        else:
            eqID = item.getEquipmentID()
            equipment = vehicles.g_cache.equipments().get(eqID)
            if equipment is None:
                return
            stage = item.getStage()
            prevStage = item.getPrevStage()
            if stage == prevStage:
                return
            cooldownStage = EQUIPMENT_STAGES.COOLDOWN
            activeStage = EQUIPMENT_STAGES.ACTIVE
            readyStage = EQUIPMENT_STAGES.READY
            isActivationStage = stage == activeStage and prevStage == readyStage
            isDeactivationStage = stage == cooldownStage and prevStage in (activeStage, readyStage)
            isReadyStage = stage == readyStage and prevStage == cooldownStage
            activationSound = equipment.activationWWSoundFeedback
            deactivationSound = equipment.deactivationWWSoundFeedback
            if isActivationStage and activationSound:
                SoundGroups.g_instance.playSound2D(activationSound)
                self.__activeEquipment.add(eqID)
            elif isDeactivationStage and deactivationSound:
                SoundGroups.g_instance.playSound2D(deactivationSound)
                self.__activeEquipment.remove(eqID)
            elif isReadyStage:
                SoundGroups.g_instance.playSound2D(BattleEvents.EQUIPMENT_READY)
            return

    def __onImageViewOpened(self, image):
        if image == MAGIC_BOOK_BG:
            SoundGroups.g_instance.playSound2D(HangarEvents.MAGIC_BOOK_ENTER)

    def __onImageViewClosed(self, image):
        if image == MAGIC_BOOK_BG:
            SoundGroups.g_instance.playSound2D(HangarEvents.MAGIC_BOOK_EXIT)

    def __onRespawnBaseMoving(self):
        pass

    def __onVehicleKilled(self, victimID, attackerID, equipmentID, reason, numVehiclesAffected):
        if victimID == BigWorld.player().playerVehicleID:
            self.__clearActiveEquipment()
            SoundGroups.g_instance.playSound2D(BattleEvents.VEHICLE_KILLED)

    def __onAirDropSpawned(self, event):
        SoundGroups.g_instance.playSound2D(BattleEvents.AIR_DROP_SPAWNED)

    def __onLootSpawned(self, event):
        mProv = Matrix()
        mProv.translation = event.ctx['position']
        soundObject = SoundGroups.g_instance.WWgetSoundObject('airDropPlacement_' + str(event.ctx['id']), mProv)
        soundObject.play(BattleEvents.LOOT_SPAWNED)
        soundObjectIdle = SoundGroups.g_instance.WWgetSoundObject('idle_' + str(event.ctx['id']), mProv)
        soundObjectIdle.play('ev_shadowPlay_ability_apple_idle')
        self.__airDropPlacementSoundObjects[event.ctx['id']] = (soundObject, soundObjectIdle)

    def __onLootPickedUp(self, event):
        if event.ctx['id'] in self.__airDropPlacementSoundObjects:
            soundObject, soundObjectIdle = self.__airDropPlacementSoundObjects.pop(event.ctx['id'])
            soundObject.stopAll()
            soundObjectIdle.play('ev_shadowPlay_ability_apple_pickup')

    def onBaseCaptured(self, baseId, newTeam):
        if not self.__isEventBattle():
            return
        elif newTeam == 0:
            return
        else:
            teamBaseController = self._sessionProvider.dynamic.teamBaseRecapturable
            if teamBaseController is None:
                return
            teamBases = teamBaseController.teamBases
            capturedBasesCount = 0
            for teamBase in teamBases.values():
                capturedBasesCount += 1 if teamBase.team == newTeam else 0

            self.__playVO(TeamBasesVO.getVO(newTeam == self._sessionProvider.getArenaDP().getNumberOfTeam(), capturedBasesCount))
            return

    def __playVO(self, vo):
        soundNotifications = getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(vo)

    def __destroyInteractiveController(self):
        if self.__soundInteractiveController is not None:
            self.__soundInteractiveController.onBattleEndWarningSound -= self.__onBattleEndWarningSound
            self.__soundInteractiveController.finalize()
            self.__soundInteractiveController = None
        return

    def __onBattleEndWarningSound(self):
        if self.__statsController is not None:
            stats = self.__statsController.getTotalStats(self._sessionProvider.arenaVisitor, self._sessionProvider)
            allyPoints = stats['leftScope']
            enemyPoints = stats['rightScope']
            rate = float(allyPoints) / max(enemyPoints, 0.1)
            if rate < 1 - _POINTS_EQUIL_EPSILON and enemyPoints > 0:
                self.__playVO(BattleEndVO.ENEMY_WINS)
            elif rate > 1 + _POINTS_EQUIL_EPSILON:
                self.__playVO(BattleEndVO.ALLY_WINS)
            else:
                self.__playVO(BattleEndVO.DRAW)
        return

    def __onArenaPeriodChange(self, period, endTime, length, additionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__playVO(BattleEvents.ARENA_START_BATTLE_VO)
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self.__clearActiveEquipment()

    def __isEventBattle(self):
        return isPlayerAvatar() and BigWorld.player().arenaBonusType in (BONUS.HALLOWEEN_BATTLES, BONUS.HALLOWEEN_BATTLES_WHEEL)

    def __clearActiveEquipment(self):
        for eqID in self.__activeEquipment:
            equipment = vehicles.g_cache.equipments().get(eqID)
            if equipment.deactivationWWSoundFeedback:
                SoundGroups.g_instance.playSound2D(equipment.deactivationWWSoundFeedback)

        self.__activeEquipment.clear()
