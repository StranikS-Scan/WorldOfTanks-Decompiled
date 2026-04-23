# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/battle_control/controllers/equipments.py
import typing
import BigWorld
import SoundGroups
from constants import EQUIPMENT_STAGES
from items import vehicles
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.consumables.equipment_ctrl import InCooldownError, _TriggerItem, _OrderItem, EquipmentsController, EquipmentsReplayPlayer, _ReplayItem, _ActivationError, _ReplayArtilleryItem, _ReplayMineFieldItem, _ReplayReconItem
from historical_battles.gui.sounds.sound_constants import HBDeathZoneEvent, HBUISound
from gui.shared.system_factory import registerEquipmentItem
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.equipment_ctrl import _EquipmentItem

class _HBBufItem(_TriggerItem):

    @property
    def becomeActive(self):
        return self._prevStage == EQUIPMENT_STAGES.READY and self._stage in (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_HBBufItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.READY):
            self._totalTime = self._descriptor.cooldownSeconds
        elif stage == EQUIPMENT_STAGES.ACTIVE:
            self._totalTime = timeRemaining
        elif stage == EQUIPMENT_STAGES.PREPARING:
            self._totalTime = 0

    def _soundUpdate(self, prevQuantity, quantity):
        if not BigWorld.player().isObserver() or BigWorld.player().isObserverFPV:
            equipment = vehicles.g_cache.equipments().get(self.getEquipmentID(), None)
            if not equipment:
                return
            if self.becomeReady:
                SoundGroups.g_instance.playSound2D(HBUISound.READY_SOUND)
                if hasattr(equipment, 'soundNotificationActive'):
                    avatar_getter.getSoundNotifications().play(equipment.soundNotificationActive)
            elif self.becomeActive:
                if equipment.soundNotification:
                    avatar_getter.getSoundNotifications().play(equipment.soundNotification)
        return

    def getDelay(self):
        return self.getDescriptor().delay

    def getDuration(self):
        return self.getDescriptor().duration


class _HBAbilityItem(_OrderItem):

    @property
    def becomeAppointed(self):
        return self._prevStage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING) and self._needActivateMapCase() and self._stage in (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)

    def _soundUpdate(self, prevQuantity, quantity):
        if not BigWorld.player().isObserver() or BigWorld.player().isObserverFPV:
            equipment = vehicles.g_cache.equipments()[self.getEquipmentID()]
            if not equipment:
                return
            if self.becomeReady:
                SoundGroups.g_instance.playSound2D(HBUISound.READY_SOUND)
                if hasattr(equipment, 'soundNotification'):
                    avatar_getter.getSoundNotifications().play(equipment.soundNotification)
            elif self.becomeAppointed:
                if self.getAppointmentUISound():
                    SoundGroups.g_instance.playSound2D(self.getAppointmentUISound())
                if hasattr(equipment, 'wwsoundFiring') and equipment.wwsoundFiring:
                    SoundGroups.g_instance.playSound2D(equipment.wwsoundFiring)
                if hasattr(equipment, 'wwsoundEquipmentUsed') and equipment.wwsoundEquipmentUsed:
                    avatar_getter.getSoundNotifications().play(equipment.wwsoundEquipmentUsed)

    def getAppointmentUISound(self):
        return HBUISound.EMPTY_SOUND

    def getDelay(self):
        return self.getDescriptor().delay

    def getDuration(self):
        return self.getDescriptor().duration

    def getAimingControlMode(self):
        from historical_battles.avatar_input_handler.hb_map_case_mode import HBMapCaseControlMode
        return HBMapCaseControlMode


class HBAfterburningBuffItem(_HBBufItem):
    pass


class HBDeathZoneItem(_HBAbilityItem):

    def getMarker(self):
        pass

    def _soundUpdate(self, prevQuantity, quantity):
        SoundGroups.g_instance.playSound2D(HBDeathZoneEvent.SOUND)


class HBArtilleryItem(_HBAbilityItem):

    def getMarker(self):
        pass

    def _getErrorMsg(self):
        return InCooldownError(self._descriptor.userString) if self._quantity else None

    def getAppointmentUISound(self):
        return HBUISound.AOE_ABILITY_APPOINTED_SOUND

    def canActivate(self, entityName=None, avatar=None):
        return (False, _ActivationError('combatEquipmentNotReady', {'equipmentName': self._descriptor.userString})) if self._stage == EQUIPMENT_STAGES.UNAVAILABLE else super(HBArtilleryItem, self).canActivate(entityName, avatar)


class _HBReplayArtilleryItem(_ReplayArtilleryItem):

    def getMarker(self):
        pass

    def getDelay(self):
        return self.getDescriptor().delay

    def getDuration(self):
        return self.getDescriptor().duration


class HBBomberItem(HBArtilleryItem):

    def getMarker(self):
        pass


class _HBReplayBomberItem(_HBReplayArtilleryItem):

    def getMarker(self):
        pass


class HBAttackPlaneItem(HBBomberItem):

    def getMarker(self):
        pass


class _HBReplayAttackPlaneItem(_HBReplayBomberItem):

    def getMarker(self):
        pass


class HBMinefieldItem(HBArtilleryItem):

    def getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import ArcadeMapCaseControlMode
        return ArcadeMapCaseControlMode

    def getMarker(self):
        pass

    def getAppointmentUISound(self):
        return HBUISound.MINEFIELD_APPOINTED_SOUND


class _HBReplayMinefieldItem(_ReplayMineFieldItem):

    def getMarker(self):
        pass


class HBReconPlaneItem(_HBAbilityItem):

    def getMarker(self):
        pass

    def getAppointmentUISound(self):
        return HBUISound.AOE_ABILITY_APPOINTED_SOUND

    def canActivate(self, entityName=None, avatar=None):
        return (False, _ActivationError('combatEquipmentNotReady', {'equipmentName': self._descriptor.userString})) if self._stage == EQUIPMENT_STAGES.UNAVAILABLE else super(HBReconPlaneItem, self).canActivate(entityName, avatar)

    def _getErrorMsg(self):
        return InCooldownError(self._descriptor.userString) if self._quantity else None


class _HBReplayReconPlaneItem(_ReplayReconItem):

    def getMarker(self):
        pass

    def getDelay(self):
        return self.getDescriptor().delay

    def getDuration(self):
        return self.getDescriptor().duration


class _HBShotItem(_HBBufItem):

    @property
    def becomeActive(self):
        return self._prevStage == EQUIPMENT_STAGES.READY and self._stage in (EQUIPMENT_STAGES.PREPARING, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)

    def canActivate(self, entityName=None, avatar=None):
        result = True
        error = None
        if self._stage and self._stage == EQUIPMENT_STAGES.ACTIVE:
            return (result, error)
        else:
            result, error = super(_HBShotItem, self).canActivate(entityName, avatar)
            return (result, error)


class HBIncendiaryShot(_HBShotItem):
    pass


class HBStunShot(_HBShotItem):
    pass


class HBAfterburning(_HBBufItem):
    pass


class HBHealPoint(_HBBufItem):

    def canActivate(self, entityName=None, avatar=None):
        return (False, _ActivationError('combatEquipmentNotReady', {'equipmentName': self._descriptor.userString})) if self._stage == EQUIPMENT_STAGES.NOT_RUNNING else super(HBHealPoint, self).canActivate(entityName, avatar)


class HBDeathZoneReplayItem(_ReplayItem):

    def getMarker(self):
        pass

    def _soundUpdate(self, *_):
        SoundGroups.g_instance.playSound2D(HBDeathZoneEvent.SOUND)

    def getDelay(self):
        return self.getDescriptor().delay

    def getDuration(self):
        return self.getDescriptor().duration


class HBLastStandItem(_HBBufItem):

    def canActivate(self, entityName=None, avatar=None):
        return (False, None)


class HBArtilleryOnYourselfItem(_HBAbilityItem):

    def getMarker(self):
        pass

    def _getErrorMsg(self):
        return InCooldownError(self._descriptor.userString) if self._quantity else None

    def canActivate(self, entityName=None, avatar=None):
        return (False, _ActivationError('combatEquipmentNotReady', {'equipmentName': self._descriptor.userString})) if self._stage == EQUIPMENT_STAGES.UNAVAILABLE else super(HBArtilleryOnYourselfItem, self).canActivate(entityName, avatar)


class _HBReplayArtilleryOnYourselfItem(_ReplayItem):

    def getMarker(self):
        pass

    def getDelay(self):
        return self.getDescriptor().delay

    def getDuration(self):
        return self.getDescriptor().duration


class HBBerserkItem(_HBBufItem):

    def canActivate(self, entityName=None, avatar=None):
        return (False, None)


class HBAmbushFire(_HBBufItem):

    def canActivate(self, entityName=None, avatar=None):
        return (False, None)


def registerHBEquipmentCtrls():
    registerEquipmentItem('personal_artillery_hb', HBDeathZoneItem, HBDeathZoneReplayItem)
    registerEquipmentItem('spotter_ability_hb', HBDeathZoneItem, HBDeathZoneReplayItem)
    registerEquipmentItem('boss_artillery_hb', HBDeathZoneItem, HBDeathZoneReplayItem)
    registerEquipmentItem('afterburning_hb', HBAfterburning, _ReplayItem)
    registerEquipmentItem('healpoint_hb', HBHealPoint, _ReplayItem)
    registerEquipmentItem('incendiaryshot_hb', HBIncendiaryShot, _ReplayItem)
    registerEquipmentItem('artillerystrike_offence_hb', HBArtilleryItem, _HBReplayArtilleryItem)
    registerEquipmentItem('artillerystrike_defence_hb', HBArtilleryItem, _HBReplayArtilleryItem)
    registerEquipmentItem('artillerymortar_hb', HBArtilleryItem, _HBReplayArtilleryItem)
    registerEquipmentItem('bomber_hb', HBBomberItem, _HBReplayBomberItem)
    registerEquipmentItem('attack_plane_hb', HBAttackPlaneItem, _HBReplayAttackPlaneItem)
    registerEquipmentItem('artilleryrocket_hb', HBArtilleryItem, _HBReplayArtilleryItem)
    registerEquipmentItem('minefield_hb', HBMinefieldItem, _HBReplayMinefieldItem)
    registerEquipmentItem('recon_hb', HBReconPlaneItem, _HBReplayReconPlaneItem)
    registerEquipmentItem('last_stand_hb', HBLastStandItem, _ReplayItem)
    registerEquipmentItem('berserk_hb', HBBerserkItem, _ReplayItem)
    registerEquipmentItem('stunshot_offence_hb', HBStunShot, _ReplayItem)
    registerEquipmentItem('stunshot_defence_hb', HBStunShot, _ReplayItem)
    registerEquipmentItem('ambush_fire_hb', HBAmbushFire, _ReplayItem)
    registerEquipmentItem('artillery_on_yourself_hb', HBArtilleryOnYourselfItem, _HBReplayArtilleryOnYourselfItem)


class HBEquipmentController(EquipmentsController):
    __slots__ = ()

    def _doChangeSetting(self, item, entityName=None, avatar=None):
        result, error = super(HBEquipmentController, self)._doChangeSetting(item, entityName, avatar)
        if isinstance(item, (_HBAbilityItem, _HBBufItem)):
            SoundGroups.g_instance.playSound2D(HBUISound.PRESSED_SOUND if result else HBUISound.NOT_READY_SOUND)
        return (result, error)


class HBReplayEquipmentController(EquipmentsReplayPlayer):
    __slots__ = ()

    def startControl(self, *args):
        super(HBReplayEquipmentController, self).startControl(*args)
        self.onEquipmentUpdated += self.__onEquipmentUpdated

    def stopControl(self):
        self.onEquipmentUpdated -= self.__onEquipmentUpdated
        super(HBReplayEquipmentController, self).stopControl()

    def __onEquipmentUpdated(self, _, item):
        if not isinstance(item, _ReplayItem) or item is None:
            return
        else:
            if item.becomeReady:
                SoundGroups.g_instance.playSound2D(HBUISound.READY_SOUND)
            elif self.__isItemApplied(item):
                SoundGroups.g_instance.playSound2D(HBUISound.PRESSED_SOUND)
            elif self.__isItemAppointed(item):
                SoundGroups.g_instance.playSound2D(HBUISound.AOE_ABILITY_APPOINTED_SOUND)
            return

    def __isItemApplied(self, item):
        prevStage = item.getPrevStage()
        curStage = item.getStage()
        if prevStage == curStage:
            return False
        return True if prevStage == EQUIPMENT_STAGES.READY and curStage in (EQUIPMENT_STAGES.PREPARING,
         EQUIPMENT_STAGES.ACTIVE,
         EQUIPMENT_STAGES.COOLDOWN,
         EQUIPMENT_STAGES.SHARED_COOLDOWN) else False

    def __isItemAppointed(self, item):
        prevStage = item.getPrevStage()
        curStage = item.getStage()
        return True if prevStage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING) and curStage in (EQUIPMENT_STAGES.ACTIVE,
         EQUIPMENT_STAGES.COOLDOWN,
         EQUIPMENT_STAGES.SHARED_COOLDOWN,
         EQUIPMENT_STAGES.EXHAUSTED) else False
