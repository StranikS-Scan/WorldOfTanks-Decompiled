# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/sound_ctrls/epic_battle_sounds.py
import SoundGroups
from BattleFeedbackCommon import BATTLE_EVENT_TYPE
from constants import EQUIPMENT_STAGES
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from gui.battle_control.avatar_getter import getSoundNotifications
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, PROGRESS_CIRCLE_TYPE
from gui.battle_control.controllers.sound_ctrls.common import BaseEfficiencySoundPlayer, SoundPlayersController, VehicleStateSoundPlayer
from gui.sounds.epic_sound_constants import EPIC_SOUND
from helpers import dependency
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IEpicBattleMetaGameController

class EpicBattleSoundController(SoundPlayersController):

    def __init__(self):
        super(EpicBattleSoundController, self).__init__()
        self._soundPlayers = (_MineFieldSoundPlayer(),
         _StealthSoundPlayer(),
         _EquipmentSoundPlayer(),
         _RepairPointAndRegenerationKitSoundPlayer(),
         _DeathZoneSoundPlayer(),
         _UnderFireSoundPlayer())

    @classmethod
    def playSoundNotification(cls, eventName):
        if not EPIC_SOUND.EPIC_MSG_SOUNDS_ENABLED:
            return
        soundNotifications = getSoundNotifications()
        if soundNotifications:
            soundNotifications.play(eventName)


class _EquipmentSoundPlayer(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def init(self):
        equipmentsCtrl = self.__sessionProvider.shared.equipments
        if equipmentsCtrl is not None:
            equipmentsCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
            equipmentsCtrl.onCombatEquipmentUsed += self.__onCombatEquipmentUsed
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        playerDataComponent = getattr(componentSystem, 'playerDataComponent', None)
        if playerDataComponent is not None:
            playerDataComponent.onPlayerRankUpdated += self.__onPlayerRankUpdated
        return

    def destroy(self):
        equipmentsCtrl = self.__sessionProvider.shared.equipments
        if equipmentsCtrl is not None:
            equipmentsCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
            equipmentsCtrl.onCombatEquipmentUsed -= self.__onCombatEquipmentUsed
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        playerDataComponent = getattr(componentSystem, 'playerDataComponent', None)
        if playerDataComponent is not None:
            playerDataComponent.onPlayerRankUpdated -= self.__onPlayerRankUpdated
        return

    @staticmethod
    def __getEventName(itemName):
        for soundName in EPIC_SOUND.EQUIPMENT_ACTIVATED:
            if soundName in itemName:
                return EPIC_SOUND.EQUIPMENT_ACTIVATED.get(soundName)

        return None

    def __onEquipmentUpdated(self, _, item):
        if item.getPrevStage() == item.getStage():
            return
        else:
            prevStageIsReady = item.getPrevStage() in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING)
            currentStageIsActive = item.getStage() in (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)
            if prevStageIsReady and currentStageIsActive:
                eventName = self.__getEventName(item.getDescriptor().name)
                if eventName is not None:
                    SoundGroups.g_instance.playSound2D(eventName)
            return

    def __onCombatEquipmentUsed(self, shooterID, eqID):
        battleCtx = self.__sessionProvider.getCtx()
        if battleCtx.isCurrentPlayer(shooterID):
            equipment = vehicles.g_cache.equipments().get(eqID)
            if equipment is None:
                return
            postfix = equipment.name.split('_')[0].upper()
            if postfix in EPIC_SOUND.BF_EB_EQUIPMENT_SOUND_LIST:
                if equipment.wwsoundEquipmentUsed:
                    SoundGroups.g_instance.playSound2D(equipment.wwsoundEquipmentUsed)
        return

    def __onPlayerRankUpdated(self, rank):
        if self.__epicController.isRandomBattleReserves():
            return
        missionsCtrl = self.__sessionProvider.dynamic.missions
        firstUnlocked, _ = missionsCtrl.getRankUpdateData(rank)
        reserveSoundId = EPIC_SOUND.EB_VO_RESERVE_UNLOCKED if firstUnlocked else EPIC_SOUND.EB_VO_RESERVE_UPGRADED
        EpicBattleSoundController.playSoundNotification(reserveSoundId)


class _MineFieldSoundPlayer(BaseEfficiencySoundPlayer):

    def _onEfficiencyReceived(self, events):
        for e in events:
            if e.getBattleEventType() == BATTLE_EVENT_TYPE.DAMAGE and e.isMineFieldDamage():
                SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_ABILITY_MINEFIELD_HITS_TARGET)
                break


class _StealthSoundPlayer(VehicleStateSoundPlayer):

    def __init__(self):
        self.__stealthIsActive = False

    def destroy(self):
        self.__stopEvent()
        super(_StealthSoundPlayer, self).destroy()

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.STEALTH_RADAR:
            if self.__stealthIsActive == value.isActive:
                return
            if value.isActive:
                self.__stealthIsActive = True
                SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_ABILITY_STEALTH_START)
            else:
                self.__stopEvent()

    def _onSwitchViewPoint(self):
        self.__stopEvent()

    def __stopEvent(self):
        if self.__stealthIsActive:
            self.__stealthIsActive = False
            SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_ABILITY_STEALTH_STOP)


class _DeathZoneSoundPlayer(VehicleStateSoundPlayer):

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DEATHZONE_TIMER:
            if value.needToShow():
                EpicBattleSoundController.playSoundNotification(EPIC_SOUND.BF_EB_ENTER_CLOSED_ZONE)


class _UnderFireSoundPlayer(VehicleStateSoundPlayer):

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.UNDER_FIRE:
            if value:
                EpicBattleSoundController.playSoundNotification(EPIC_SOUND.BF_EB_ENTER_PROTECTION_ZONE)


class _RepairPointAndRegenerationKitSoundPlayer(VehicleStateSoundPlayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__isRepairing = False
        self.__isHealing = False
        self.__curPointIdx = -1

    def destroy(self):
        super(_RepairPointAndRegenerationKitSoundPlayer, self).destroy()
        self.__playResupplyStop()
        self.__curPointIdx = -1

    def _subscribe(self):
        super(_RepairPointAndRegenerationKitSoundPlayer, self)._subscribe()
        ctrl = self.__sessionProvider.dynamic.progressTimer
        if ctrl is not None:
            ctrl.onVehicleEntered += self.__onVehicleEntered
            ctrl.onCircleStatusChanged += self.__onCircleStatusChanged
            ctrl.onVehicleLeft += self.__onVehicleLeft
        return

    def _unsubscribe(self):
        super(_RepairPointAndRegenerationKitSoundPlayer, self)._unsubscribe()
        ctrl = self.__sessionProvider.dynamic.progressTimer
        if ctrl is not None:
            ctrl.onVehicleEntered -= self.__onVehicleEntered
            ctrl.onCircleStatusChanged -= self.__onCircleStatusChanged
            ctrl.onVehicleLeft -= self.__onVehicleLeft
        return

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.HEALING:
            isActive = value['isInactivation']
            if isActive is None:
                self.__stopHealingEvent()
            else:
                self.__isHealing = True
        return

    def _onSwitchViewPoint(self):
        self.__stopHealingEvent()

    def __stopHealingEvent(self):
        if self.__isHealing:
            self.__isHealing = False
            if self.__isRepairing:
                return
            SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_ABILITY_RENOVATION_COMPLETED)

    def __onVehicleEntered(self, type_, pointIdx, state):
        if type_ is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        self.__curPointIdx = pointIdx
        if state == EPIC_CONSTS.RESUPPLY_READY:
            self.__playResupplyReady()

    def __onVehicleLeft(self, type_, _):
        if type_ is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        self.__playResupplyStop()
        self.__curPointIdx = -1

    def __onCircleStatusChanged(self, type_, pointIdx, state):
        if type_ is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        if self.__curPointIdx != pointIdx:
            return
        if state == EPIC_CONSTS.RESUPPLY_FULL:
            EpicBattleSoundController.playSoundNotification(EPIC_SOUND.EB_UI_REPPAIR_POINT_COMPLETED)
        elif state == EPIC_CONSTS.RESUPPLY_READY:
            self.__playResupplyReady()
        elif state == EPIC_CONSTS.RESUPPLY_BLOCKED:
            self.__playResupplyStop()

    def __playResupplyReady(self):
        if not self.__isRepairing and self.__curPointIdx != -1:
            self.__isRepairing = True
            SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_UI_REPPAIR_POINT_PROGRESS)

    def __playResupplyStop(self):
        if self.__isRepairing and self.__curPointIdx != -1:
            self.__isRepairing = False
            SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_UI_REPPAIR_POINT_PROGRESS_STOP)
