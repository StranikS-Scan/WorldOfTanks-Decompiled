# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/consumables_panel.py
import BigWorld
from Event import EventsSubscriber
from battle_royale.gui.Scaleform.daapi.view.common.respawn_ability import RespawnAbility
from battle_royale.gui.battle_control.controllers.spawn_ctrl import ISpawnListener
from constants import EQUIPMENT_STAGES, ARENA_BONUS_TYPE, ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel, TOOLTIP_FORMAT
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R
from helpers.time_utils import ONE_MINUTE

class BattleRoyaleConsumablesPanel(ConsumablesPanel, ISpawnListener):
    __slots__ = ('__quantityMap',)
    _PANEL_MAX_LENGTH = 11
    _AMMO_START_IDX = 0
    _AMMO_END_IDX = 1
    _EQUIPMENT_START_IDX = 2
    _EQUIPMENT_END_IDX = 9
    _RESPAWN_EQUIPMENT_IDX = 10
    _R_ARTEFACT_ICON = R.images.gui.maps.icons.battleRoyale.artefact

    def __init__(self):
        super(BattleRoyaleConsumablesPanel, self).__init__()
        self.__quantityMap = [None] * self._PANEL_MAX_LENGTH
        self.__equipmentRange = range(self._EQUIPMENT_START_IDX, self._EQUIPMENT_END_IDX + 1)
        self.__es = EventsSubscriber()
        self.__respawnTimestampSent = False
        return

    def _populate(self):
        super(BattleRoyaleConsumablesPanel, self)._populate()
        vehStateCtrl = self.sessionProvider.shared.vehicleState
        self.__es.subscribeToEvent(vehStateCtrl.onVehicleStateUpdated, self.__onVehicleLootAction)
        self.__es.subscribeToEvent(BigWorld.player().onObserverVehicleChanged, self.__onObserverVehicleChanged)
        self.__updateRespawnSkill()

    def _dispose(self):
        self.__es.unsubscribeFromAllEvents()
        super(BattleRoyaleConsumablesPanel, self)._dispose()

    def _getPanelSettings(self):
        return CONSUMABLES_PANEL_SETTINGS.BATTLE_ROYALE_SETTINGS_ID

    def _reset(self):
        super(BattleRoyaleConsumablesPanel, self)._reset()
        self.__quantityMap = [None] * self._PANEL_MAX_LENGTH
        return

    def _onShellsAdded(self, intCD, descriptor, quantity, _, gunSettings, isInfinite):
        if intCD in self._cds:
            return
        else:
            slotIdx = self.__getNewSlotIdx(self._AMMO_START_IDX, self._AMMO_END_IDX)
            if slotIdx is None:
                return
            self._addShellSlot(slotIdx, intCD, descriptor, quantity, gunSettings, isInfinite)
            self._mask |= 1 << slotIdx
            return

    def _onShellsUpdated(self, intCD, quantity, *args):
        if intCD not in self._cds:
            return
        super(BattleRoyaleConsumablesPanel, self)._onShellsUpdated(intCD, quantity, *args)

    def _onNextShellChanged(self, intCD):
        if intCD not in self._cds:
            return
        super(BattleRoyaleConsumablesPanel, self)._onNextShellChanged(intCD)

    def _onCurrentShellChanged(self, intCD):
        if intCD not in self._cds:
            return
        super(BattleRoyaleConsumablesPanel, self)._onCurrentShellChanged(intCD)

    def _onGunSettingsSet(self, _):
        self.__resetShellSlots()
        self._resetDelayedReload()

    def _onGunReloadTimeSet(self, currShellCD, state, skipAutoLoader):
        if currShellCD not in self._cds:
            return
        super(BattleRoyaleConsumablesPanel, self)._onGunReloadTimeSet(currShellCD, state, skipAutoLoader)

    def _onEquipmentAdded(self, intCD, item):
        if item is None or intCD in self._cds:
            return
        else:
            slotIdx = self.__getNewSlotIdx(self._EQUIPMENT_START_IDX, self._EQUIPMENT_END_IDX)
            if slotIdx is None:
                return
            self._addEquipmentSlot(slotIdx, intCD, item)
            self._mask |= 1 << slotIdx
            return

    def _isAvatarEquipment(self, item):
        return False

    def _resetOptDevices(self):
        pass

    def _addOptionalDeviceSlot(self, idx, intCD):
        pass

    def _buildEquipmentSlotTooltipText(self, item):
        descriptor = item.getDescriptor()
        body = descriptor.description
        toolTip = TOOLTIP_FORMAT.format(descriptor.userString, body)
        return toolTip

    def _updateShellSlot(self, idx, quantity):
        super(BattleRoyaleConsumablesPanel, self)._updateShellSlot(idx, quantity)
        prevQuantity = self.__quantityMap[idx]
        self.__quantityMap[idx] = quantity
        if prevQuantity is not None and quantity > prevQuantity:
            self.as_setGlowS(idx, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN)
        return

    def _updateEquipmentSlot(self, idx, item):
        super(BattleRoyaleConsumablesPanel, self)._updateEquipmentSlot(idx, item)
        prevQuantity = self.__quantityMap[idx]
        quantity = self.__quantityMap[idx] = item.getQuantity()
        if prevQuantity is not None and quantity > prevQuantity:
            self.as_setGlowS(idx, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN)
            return
        else:
            currStage = item.getStage()
            prevStage = item.getPrevStage()
            if currStage == EQUIPMENT_STAGES.READY and prevStage == EQUIPMENT_STAGES.COOLDOWN:
                self.as_setGlowS(idx, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL)
            elif currStage == EQUIPMENT_STAGES.COOLDOWN and prevStage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING, EQUIPMENT_STAGES.ACTIVE):
                self.as_setGlowS(idx, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_ORANGE)
            elif currStage == EQUIPMENT_STAGES.READY and prevStage == EQUIPMENT_STAGES.PREPARING:
                self.as_setEquipmentActivatedS(idx, False)
            return

    def _updateOptionalDeviceSlot(self, idx, isOn):
        pass

    def _showEquipmentGlow(self, equipmentIndex, glowType=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_ORANGE):
        pass

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self._reset()

    def __onObserverVehicleChanged(self):
        self._reset()
        self.__updateRespawnSkill()

    def __getNewSlotIdx(self, startIdx=0, endIdx=_PANEL_MAX_LENGTH - 1):
        resultIdx = None
        for idx in range(startIdx, endIdx + 1):
            if self._mask & 1 << idx == 0:
                resultIdx = idx
                break

        return resultIdx

    def __resetShellSlots(self):
        for idx in range(self._AMMO_START_IDX, self._AMMO_END_IDX + 1):
            self._mask &= ~(1 << idx)
            self._cds[idx] = None

        return

    def __resetEquipmentSlots(self):
        for idx in self.__equipmentRange:
            self._mask &= ~(1 << idx)
            self._cds[idx] = None

        return

    def __onVehicleLootAction(self, state, _):
        if state != VEHICLE_VIEW_STATE.LOOT:
            return
        else:
            self.__quantityMap = [ (numItems if numItems is not None else 0) for numItems in self.__quantityMap ]
            vehStateCtrl = self.sessionProvider.shared.vehicleState
            if vehStateCtrl is not None:
                vehStateCtrl.onVehicleStateUpdated -= self.__onVehicleLootAction
            return

    def updateLives(self, livesLeft, prev):
        isAvailable = livesLeft >= 0
        count = max(livesLeft, 0)
        self.__onRespawnCountUpdated(count)
        self.__onRespawnAvailabilityChanged(isAvailable)
        if prev is not None and count > prev:
            self.as_setGlowS(self._RESPAWN_EQUIPMENT_IDX, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN)
        return

    def _onVehicleStateUpdated(self, state, value):
        if state in (VEHICLE_VIEW_STATE.SWITCHING, VEHICLE_VIEW_STATE.RESPAWNING):
            self.__removeRespawnSlot()
        super(BattleRoyaleConsumablesPanel, self)._onVehicleStateUpdated(state, value)

    def __updateRespawnSkill(self):
        bwKey, sfKey = self._genKey(self._RESPAWN_EQUIPMENT_IDX)
        header = backport.text(RespawnAbility.name)
        body = self.__buildRespawnEquipmentTooltipText()
        tooltip = TOOLTIP_FORMAT.format(header, body)
        arena = BigWorld.player().arena
        period = arena.period
        count = 0
        isAvailable = False
        needToRemove = False
        if period == ARENA_PERIOD.BATTLE:
            vehicle = BigWorld.player().getVehicleAttached()
            if vehicle and vehicle.isAlive():
                vehicleBRRespawnComponent = vehicle.dynamicComponents.get('vehicleBRRespawnComponent')
                if vehicleBRRespawnComponent is not None:
                    count = vehicleBRRespawnComponent.lives
                    isAvailable = True
            else:
                needToRemove = True
        if needToRemove:
            self.__removeRespawnSlot()
        else:
            self.as_addRespawnSlotS(self._RESPAWN_EQUIPMENT_IDX, bwKey, sfKey, count, tooltip, False, isAvailable)
        return

    def __removeRespawnSlot(self):
        self.as_resetS([self._RESPAWN_EQUIPMENT_IDX])

    def __buildRespawnEquipmentTooltipText(self):
        bonusType = self.sessionProvider.arenaVisitor.getArenaBonusType()
        isSquadMode = bonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD_RANGE
        return backport.text(R.strings.artefacts.br_respawn.platoon.descr(), duration=RespawnAbility().platoonRespawnPeriod / ONE_MINUTE, timeToResurrect=RespawnAbility().platoonTimeToRessurect) if isSquadMode else backport.text(R.strings.artefacts.br_respawn.solo.descr(), duration=RespawnAbility().soloRespawnPeriod / ONE_MINUTE)

    def _onRespawnBaseMoving(self):
        super(BattleRoyaleConsumablesPanel, self)._onRespawnBaseMoving()
        self.__updateRespawnSkill()

    def __onRespawnCountUpdated(self, count):
        self.as_setRespawnSlotQuantityS(self._RESPAWN_EQUIPMENT_IDX, count)

    def __onRespawnAvailabilityChanged(self, isAvailable):
        self.as_setRespawnSlotStateS(self._RESPAWN_EQUIPMENT_IDX, isAvailable)
