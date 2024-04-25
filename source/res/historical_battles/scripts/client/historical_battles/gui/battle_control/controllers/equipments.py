# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/battle_control/controllers/equipments.py
import typing
import BigWorld
import SoundGroups
from constants import EQUIPMENT_STAGES
from items import vehicles
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.consumables.equipment_ctrl import InCooldownError, _TriggerItem, _OrderItem, EquipmentsController, EquipmentsReplayPlayer, _ReplayItem, _ActivationError
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
                SoundGroups.g_instance.playSound2D(self.getAppointmentUISound())
                if hasattr(equipment, 'wwsoundFiring') and equipment.wwsoundFiring:
                    SoundGroups.g_instance.playSound2D(equipment.wwsoundFiring)
                if equipment.wwsoundEquipmentUsed:
                    avatar_getter.getSoundNotifications().play(equipment.wwsoundEquipmentUsed)

    def getAppointmentUISound(self):
        return HBUISound.EMPTY_SOUND


class _AoeArcadeArtileryItem(_HBAbilityItem):

    def _getErrorMsg(self):
        return InCooldownError(self._descriptor.userString) if self._quantity else None

    def getAimingControlMode(self):
        from historical_battles.avatar_input_handler.hb_map_case_mode import AoeArcadeMapCaseControlMode
        return AoeArcadeMapCaseControlMode


class HBDynamicActiveStageCooldownItem(_HBBufItem):

    @property
    def becomeActive(self):
        isSuperActive = super(HBDynamicActiveStageCooldownItem, self).becomeActive
        return isSuperActive or self._prevStage == EQUIPMENT_STAGES.READY and self._stage == EQUIPMENT_STAGES.PREPARING

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(HBDynamicActiveStageCooldownItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.READY):
            self._totalTime = self._descriptor.cooldownSeconds
        elif stage == EQUIPMENT_STAGES.ACTIVE:
            self._totalTime = timeRemaining
        elif stage == EQUIPMENT_STAGES.PREPARING:
            self._totalTime = 0

    def getEntitiesIterator(self, avatar=None):
        return []

    def canActivate(self, entityName=None, avatar=None):
        result, error = super(HBDynamicActiveStageCooldownItem, self).canActivate()
        if not result:
            return (result, error)
        if self.getStage() == EQUIPMENT_STAGES.PREPARING:
            error = _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString})
            result = False
        return (result, error)

    def canDeactivate(self):
        return False


class HBAfterburningBuffItem(_HBBufItem):
    pass


class HBDeathZoneItem(_HBAbilityItem):

    def getMarker(self):
        pass

    def _soundUpdate(self, prevQuantity, quantity):
        SoundGroups.g_instance.playSound2D(HBDeathZoneEvent.SOUND)


class HBArtileryItem(_HBAbilityItem):

    def getMarker(self):
        pass

    def _getErrorMsg(self):
        return InCooldownError(self._descriptor.userString) if self._quantity else None

    def getAppointmentUISound(self):
        return HBUISound.ARTILERY_APPOINTED_SOUND

    def canActivate(self, entityName=None, avatar=None):
        return (False, _ActivationError('combatEquipmentNotReady', {'equipmentName': self._descriptor.userString})) if self._stage == EQUIPMENT_STAGES.UNAVAILABLE else super(HBArtileryItem, self).canActivate(entityName, avatar)


class HBTacticalMineItem(HBArtileryItem):

    def getMarker(self):
        pass

    def getAppointmentUISound(self):
        return HBUISound.TACTICAL_MINEFIELD_APPOINTED_SOUND


class HBBomberItem(HBArtileryItem):

    def getMarker(self):
        pass


class HBBomberCasItem(HBBomberItem):

    def getMarker(self):
        pass


class HBMinefieldItem(_AoeArcadeArtileryItem):

    def getMarker(self):
        pass

    def getAppointmentUISound(self):
        return HBUISound.ARTILERY_APPOINTED_SOUND


class HBArcadeMinefieldItem(_AoeArcadeArtileryItem):

    def getMarker(self):
        pass

    def getAppointmentUISound(self):
        return HBUISound.MINEFIELD_APPOINTED_SOUND


class HBAoeArcadeTeamRepairKitItem(_AoeArcadeArtileryItem):
    pass


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
                SoundGroups.g_instance.playSound2D(HBUISound.ARTILERY_APPOINTED_SOUND)
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


class HBAfterburning(_HBBufItem):
    pass


class HBHealPoint(_HBBufItem):

    def canActivate(self, entityName=None, avatar=None):
        return (False, _ActivationError('combatEquipmentNotReady', {'equipmentName': self._descriptor.userString})) if self._stage == EQUIPMENT_STAGES.NOT_RUNNING else super(HBHealPoint, self).canActivate(entityName, avatar)


class HBDeathZoneReplayItem(_ReplayItem):

    def _soundUpdate(self, *_):
        SoundGroups.g_instance.playSound2D(HBDeathZoneEvent.SOUND)


def registerHBEquipmentCtrls():
    registerEquipmentItem('afterburning_hb', HBAfterburning, _ReplayItem)
    registerEquipmentItem('healpoint_hb', HBHealPoint, _ReplayItem)
