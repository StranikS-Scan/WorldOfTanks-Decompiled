# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/consumables_panel.py
import time
from datetime import datetime
from functools import partial
import BigWorld
import Event
from gui import TANKMEN_ROLES_ORDER_DICT
from gui.Scaleform.daapi.view.meta.HWConsumablesPanelMeta import HWConsumablesPanelMeta
from constants import EQUIPMENT_STAGES, ARENA_PERIOD
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from halloween_common.items.hw_artefacts import EventEquipment
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import TOOLTIP_FORMAT, EMPTY_EQUIPMENT_TOOLTIP
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, VEHICLE_DEVICE_IN_COMPLEX_ITEM, DEVICE_STATE_AS_DAMAGE, DEVICE_STATE_CRITICAL, DEVICE_STATE_DESTROYED
from gui.battle_control.controllers.consumables.equipment_ctrl import NeedEntitySelection, IgnoreEntitySelection
from PlayerEvents import g_playerEvents
from helpers.CallbackDelayer import CallbackDelayer
_ACTIVE_EQUIPMENT_STAGES = (EQUIPMENT_STAGES.PREPARING, EQUIPMENT_STAGES.ACTIVE)

class HWConsumablesPanel(HWConsumablesPanelMeta):
    _PANEL_MAX_LENGTH = 15
    _HW_EQUIPMENT_STATR_IDX = 0
    _HW_EQUIPMENT_END_IDX = 2
    _EQUIPMENT_START_IDX = 3
    _EQUIPMENT_END_IDX = 5
    _AMMO_START_IDX = 6
    _AMMO_END_IDX = 8
    _ORDERS_START_IDX = 9
    _ORDERS_END_IDX = 11
    _OPT_DEVICE_START_IDX = 12
    _OPT_DEVICE_END_IDX = 14
    PERMANENT_GLOW_MIN_DURATION_SECONDS = 7.0
    HW_EQUIPMENT_UPDATE_INTERVAL = 0.1
    onHandleEquipmentPressed = Event.Event()

    def __init__(self):
        super(HWConsumablesPanel, self).__init__()
        self._permanentGlows = set()
        self._permanentGlowTimestamp = {}
        self._arenaPeriod = None
        self._hwEquipmentGlow = {}
        self._hwEquipmentGlowAllowed = {}
        self._callbackDelayer = CallbackDelayer()
        return

    def onPopUpClosed(self):
        super(HWConsumablesPanel, self).onPopUpClosed()
        self._updateHWEquipmentKeyHandlers()

    def _populate(self):
        super(HWConsumablesPanel, self)._populate()
        g_playerEvents.onArenaPeriodChange += self._onArenaPeriodChange
        self._callbackDelayer.delayCallback(self.HW_EQUIPMENT_UPDATE_INTERVAL, self._onUpdateHWEquipmentTimer)
        self._arenaPeriod = self.sessionProvider.shared.arenaPeriod.getPeriod()

    def _dispose(self):
        self.sessionProvider.removeArenaCtrl(self)
        g_playerEvents.onArenaPeriodChange -= self._onArenaPeriodChange
        self._hwEquipmentGlow.clear()
        self._hwEquipmentGlowAllowed.clear()
        self._callbackDelayer.destroy()
        super(HWConsumablesPanel, self)._dispose()

    def _reset(self):
        super(HWConsumablesPanel, self)._reset()
        self.as_resetPassiveAbilitiesS()

    def _generateEquipmentKey(self, idx, item):
        return self._genKey(idx) if item.getTags() and item.getTimeRemaining() >= 0.0 else (None, None)

    def _onShellsAdded(self, intCD, descriptor, quantity, _, gunSettings):
        idx = self._bookNextSlotIdx(self._AMMO_START_IDX, self._AMMO_END_IDX)
        if idx is not None:
            self._addShellSlot(idx, intCD, descriptor, quantity, gunSettings)
            self.as_setShellInfinityS(idx, True)
        return

    def _onEquipmentAdded(self, intCD, item):
        if item and self._isHalloweenEquipment(item):
            idx = self._bookNextSlotIdx(self._HW_EQUIPMENT_STATR_IDX, self._HW_EQUIPMENT_END_IDX)
            if idx is not None:
                self._addHWEquipmentSlot(idx, intCD, item)
        else:
            idx = self._bookNextSlotIdx(self._EQUIPMENT_START_IDX, self._EQUIPMENT_END_IDX)
            if idx is not None:
                self._addEquipmentSlot(idx, intCD, item)
        return

    def _onOptionalDeviceAdded(self, optDeviceInBattle):
        if optDeviceInBattle.getIntCD() in self._cds:
            return
        else:
            idx = self._bookNextSlotIdx(self._OPT_DEVICE_START_IDX, self._OPT_DEVICE_END_IDX)
            if idx is not None:
                self._addOptionalDeviceSlot(idx, optDeviceInBattle)
            return

    def _addHWEquipmentSlot(self, idx, intCD, item):
        self._cds[idx] = intCD
        bwKey, sfKey = self._genKey(idx)
        if self._isHalloweenEmptySlot(item):
            bwKey, sfKey = self._genKey(idx)
            self.as_addAbilitySlotS(idx=idx, keyCode=bwKey, sfKeyCode=sfKey, quantity=0, timeRemaining=0, reloadingTime=0, iconPath='', tooltipText=EMPTY_EQUIPMENT_TOOLTIP)
            return
        handler = partial(self._handleEquipmentPressed, intCD)
        if item.getQuantity() > 0:
            self._extraKeys[idx] = self._keys[bwKey] = handler
        descriptor = item.getDescriptor()
        quantity = item.getQuantity()
        timeRemaining = item.getTimeRemaining()
        reloadingTime = item.getTotalTime()
        iconPath = self._getEquipmentIcon(idx, item, descriptor.icon[0])
        toolTip = self._buildEquipmentSlotTooltipText(item)
        if not self._isHalloweenPassive(item):
            self.as_addAbilitySlotS(idx=idx, keyCode=bwKey, sfKeyCode=sfKey, quantity=quantity, timeRemaining=timeRemaining, reloadingTime=reloadingTime, iconPath=iconPath, tooltipText=toolTip)
        else:
            self.as_addPassiveAbilitySlotS(idx=idx, iconPath=iconPath, state='green', tooltipText=toolTip)
        self._updateEquipmentSlot(idx, item)

    def _updateHWEquipmentKeyHandlers(self, updateSlots=None):
        hwEqupmentRange = xrange(self._HW_EQUIPMENT_STATR_IDX, self._HW_EQUIPMENT_END_IDX + 1)
        for idx, intCD in enumerate(self._cds):
            if idx not in hwEqupmentRange:
                continue
            bwKey, sfKey = self._genKey(idx) if intCD is not None else None
            handler = partial(self._handleEquipmentPressed, self._cds[idx]) if intCD is not None else None
            self._keys[bwKey] = handler
            self._extraKeys[idx] = handler
            if updateSlots is not None:
                updateSlots.append((idx, bwKey, sfKey))

        return

    def _onMappingChanged(self, *args):
        super(HWConsumablesPanel, self)._onMappingChanged(*args)
        slots = []
        self._updateHWEquipmentKeyHandlers(updateSlots=slots)
        self.as_setKeysToSlotsS(slots)

    def _handleEquipmentPressed(self, intCD, entityName=None):
        super(HWConsumablesPanel, self)._handleEquipmentPressed(intCD, entityName)
        self.onHandleEquipmentPressed(intCD)

    def _updateEquipmentGlow(self, idx, item):
        if item.isReusable or item.isAvatar() and item.getStage() != EQUIPMENT_STAGES.PREPARING:
            glowType = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL if item.isAvatar() else CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN
            if self._isAnyEquipmentModuleInState(item, (DEVICE_STATE_DESTROYED,)):
                equipmentTags = item.getTags()
                if 'medkit' in equipmentTags:
                    self._showEquipmentGlow(idx)
                else:
                    self._showPermanentGlow(idx)
            elif item.becomeReady:
                self._showEquipmentGlow(idx, glowType if not self._isAnyEquipmentModuleInState(item, (DEVICE_STATE_CRITICAL,)) else CONSUMABLES_PANEL_SETTINGS.GLOW_ID_ORANGE)
            elif idx in self._equipmentsGlowCallbacks:
                self._clearEquipmentGlow(idx)
        if not item.isAvailableToUse and self._isGlowShown(idx):
            self._clearEquipmentGlow(idx)
            self._hidePermanentGlow(idx)

    def _updateEquipmentSlot(self, idx, item):
        if not self._isHalloweenEquipment(item):
            super(HWConsumablesPanel, self)._updateEquipmentSlot(idx, item)
            return
        currStage = item.getStage()
        prevStage = item.getPrevStage()
        quantity = item.getQuantity()
        currentTime = item.getTimeRemaining()
        maxTime = item.getTotalTime()
        count = 0
        if self._isSuperShell(item):
            count = item.getDescriptor().shotsCount
            if currStage == EQUIPMENT_STAGES.ACTIVE:
                count, maxTime = maxTime, 0
        self.as_updateAbilityS(idx, currStage, count, currentTime, maxTime)
        bwKey, _ = self._genKey(idx)
        if quantity > 0 and bwKey not in self._keys:
            self._keys[bwKey] = partial(self._handleEquipmentPressed, self._cds[idx])
        isGlowAllowed = self._isGlowAllowed(item)
        self._hwEquipmentGlowAllowed[idx] = isGlowAllowed
        if not isGlowAllowed or currStage in (EQUIPMENT_STAGES.NOT_RUNNING, EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.COOLDOWN):
            self.as_hideGlowS(idx)
            self.as_setEquipmentActivatedS(idx, False)
        elif (prevStage, currStage) == (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.READY):
            self.as_setEquipmentActivatedS(idx, False)
            self._showHWEqupmentGlow(idx, glowID=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL)
        elif (prevStage, currStage) == (EQUIPMENT_STAGES.NOT_RUNNING, EQUIPMENT_STAGES.READY):
            self._showHWEqupmentGlow(idx, glowID=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL)
        elif (prevStage, currStage) == (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.READY):
            self._showHWEqupmentGlow(idx, glowID=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL)
        elif (prevStage, currStage) == (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.READY):
            self._showHWEqupmentGlow(idx, glowID=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL)
        elif currStage in _ACTIVE_EQUIPMENT_STAGES and prevStage not in _ACTIVE_EQUIPMENT_STAGES:
            self.as_setEquipmentActivatedS(idx, True)
        elif currStage not in _ACTIVE_EQUIPMENT_STAGES and prevStage in _ACTIVE_EQUIPMENT_STAGES:
            self.as_setEquipmentActivatedS(idx, False)

    def _showHWEqupmentGlow(self, idx, glowID):
        if self._arenaPeriod != ARENA_PERIOD.BATTLE:
            self._hwEquipmentGlow[idx] = glowID
        else:
            self.as_setGlowS(idx, glowID=glowID)

    def _onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == self._arenaPeriod:
            return
        self._arenaPeriod = period
        if period != ARENA_PERIOD.BATTLE:
            return
        for idx, glowID in self._hwEquipmentGlow.items():
            self.as_setGlowS(idx, glowID=glowID)

        self._hwEquipmentGlow.clear()

    def _onUpdateHWEquipmentTimer(self):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            for intCD, item in ctrl.iterEquipmentsByTag('halloween_equipment'):
                idx = self._cds.index(intCD)
                if self._hwEquipmentGlowAllowed.get(idx, None) != self._isGlowAllowed(item):
                    self._updateEquipmentSlot(idx, item)

        return self.HW_EQUIPMENT_UPDATE_INTERVAL

    def _clearAllEquipmentGlow(self):
        super(HWConsumablesPanel, self)._clearAllEquipmentGlow()
        self._permanentGlows.clear()
        self._permanentGlowTimestamp.clear()
        for idx in xrange(self._EQUIPMENT_START_IDX, self._PANEL_MAX_LENGTH - 1):
            self.as_hideGlowS(idx)

    def _buildEquipmentSlotTooltipText(self, item):
        if not self._isHalloweenEquipment(item):
            return super(HWConsumablesPanel, self)._buildEquipmentSlotTooltipText(item)
        descriptor = item.getDescriptor()
        body = descriptor.description
        if isinstance(descriptor, EventEquipment) and not self._isSuperShell(item):
            if int(descriptor.durationSeconds) > 0:
                body = '\n'.join((body, backport.text(R.strings.hw_ingame_gui.consumablesPanel.tooltip.durationTime(), time=str(int(descriptor.durationSeconds)))))
        cooldownSeconds = descriptor.cooldownSeconds
        if cooldownSeconds:
            tooltipStr = R.strings.ingame_gui.consumables_panel.equipment.cooldownSeconds()
            paramsString = backport.text(tooltipStr, cooldownSeconds=str(int(cooldownSeconds)))
            body = '\n\n'.join((body, paramsString))
        return TOOLTIP_FORMAT.format(descriptor.userString, body)

    def _onVehicleStateUpdated(self, state, value):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is None:
            return
        else:
            if state == VEHICLE_VIEW_STATE.DEVICES:
                deviceName, _, actualState = value
                if deviceName in VEHICLE_DEVICE_IN_COMPLEX_ITEM:
                    itemName = VEHICLE_DEVICE_IN_COMPLEX_ITEM[deviceName]
                else:
                    itemName = deviceName
                isCrewUpdated = itemName in TANKMEN_ROLES_ORDER_DICT['enum']
                equipmentTag = 'medkit' if isCrewUpdated else 'repairkit'
                if actualState in DEVICE_STATE_AS_DAMAGE:
                    for intCD, equipment in ctrl.iterEquipmentsByTag(equipmentTag, lambda e: e.isAvailableToUse):
                        idx = self._cds.index(intCD)
                        if actualState == DEVICE_STATE_CRITICAL:
                            if not self._isPermamentGlowShown(idx):
                                self._showEquipmentGlow(idx)
                            elif not self._isAnyEquipmentModuleInState(equipment, (DEVICE_STATE_DESTROYED,)):
                                self._defferPermanentGlowChange(idx, self.PERMANENT_GLOW_MIN_DURATION_SECONDS)
                        if self._isGlowShown(idx):
                            self._clearEquipmentGlow(idx)
                            self._hidePermanentGlow(idx)
                        if not isCrewUpdated:
                            self._showPermanentGlow(idx)
                        self._showEquipmentGlow(idx)

                else:
                    for intCD, equipment in ctrl.iterEquipmentsByTag(equipmentTag):
                        if not self._isAnyEquipmentModuleInState(equipment, DEVICE_STATE_AS_DAMAGE):
                            idx = self._cds.index(intCD)
                            self._clearEquipmentGlow(idx)
                            self._hidePermanentGlow(idx)

                idx = int(self.as_updateEntityStateS(itemName, actualState))
                if idx > 0 and idx < len(self._cds):
                    intCD = self._cds[idx]
                    if not ctrl.hasEquipment(intCD):
                        return
                    item = ctrl.getEquipment(intCD)
                    if item and item.isEntityRequired():
                        self._replaceEquipmentKeyHandler(self._keys, self._cds[idx], deviceName)
                        self._replaceEquipmentKeyHandler(self._extraKeys, self._cds[idx], deviceName)
            elif state == VEHICLE_VIEW_STATE.FIRE:
                if value:
                    hasReadyAutoExt = False
                    glowCandidates = []
                    for intCD, equipment in ctrl.iterEquipmentsByTag('extinguisher'):
                        if not equipment.isReady:
                            continue
                        if equipment.getDescriptor().autoactivate:
                            hasReadyAutoExt = True
                        glowCandidates.append(intCD)

                    if not hasReadyAutoExt:
                        for cID in glowCandidates:
                            self._showPermanentGlow(self._cds.index(cID))

                else:
                    for intCD, equipment in ctrl.iterEquipmentsByTag('extinguisher'):
                        if not equipment.getDescriptor().autoactivate:
                            self._hidePermanentGlow(self._cds.index(intCD))

            else:
                super(HWConsumablesPanel, self)._onVehicleStateUpdated(state, value)
            return

    def _showPermanentGlow(self, idx, glowID=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL):
        if BigWorld.player().isObserver():
            return
        self._permanentGlows.add(idx)
        self._permanentGlowTimestamp[idx] = time.mktime(datetime.now().timetuple())
        self.as_setGlowS(idx, glowID)

    def _hidePermanentGlow(self, idx):
        if idx in self._permanentGlows:
            self._permanentGlows.remove(idx)
            del self._permanentGlowTimestamp[idx]
            if idx not in self._equipmentsGlowCallbacks:
                self.as_hideGlowS(idx)

    def _defferPermanentGlowChange(self, idx, glowMinDuration):
        glowDurationLeft = 0
        if idx in self._permanentGlowTimestamp:
            glowTotalDuration = time.mktime(datetime.now().timetuple()) - self._permanentGlowTimestamp[idx]
            glowDurationLeft = max(0, glowMinDuration - glowTotalDuration)
        if idx in self._equipmentsGlowCallbacks:
            BigWorld.cancelCallback(self._equipmentsGlowCallbacks[idx])
            del self._equipmentsGlowCallbacks[idx]
        if glowDurationLeft > 0:
            self._equipmentsGlowCallbacks[idx] = BigWorld.callback(glowDurationLeft, partial(self._defferPermanentGlowChange, idx, glowMinDuration))
        else:
            self._hidePermanentGlow(idx)
            self._clearEquipmentGlow(idx)
            self._showEquipmentGlow(idx)

    def _isPermamentGlowShown(self, idx):
        return idx in self._permanentGlows

    def _isGlowShown(self, idx):
        return self._isPermamentGlowShown(idx) or idx in self._equipmentsGlowCallbacks

    def _clearEquipmentGlow(self, equipmentIndex, cancelCallback=True):
        if equipmentIndex in self._equipmentsGlowCallbacks:
            if equipmentIndex not in self._permanentGlows:
                self.as_hideGlowS(equipmentIndex)
            if cancelCallback:
                BigWorld.cancelCallback(self._equipmentsGlowCallbacks[equipmentIndex])
            del self._equipmentsGlowCallbacks[equipmentIndex]

    def _isGlowAllowed(self, equipment):
        canActivate, _ = equipment.canActivate()
        return canActivate or equipment.getStage() == EQUIPMENT_STAGES.ACTIVE

    def _isAnyEquipmentModuleInState(self, equipment, checkDeviceStates):
        equipmentTags = equipment.getTags()
        if 'extinguisher' in equipmentTags:
            correction = True
            entityName = None
        elif self._isHalloweenEquipment(equipment) or self._isHalloweenPassive(equipment):
            correction = False
            entityName = None
        else:
            entityNames = [ name for name, state in equipment.getEntitiesIterator() if state in checkDeviceStates ]
            correction = hasDestroyed = len(entityNames)
            entityName = entityNames[0] if hasDestroyed else None
        canActivate, info = equipment.canActivate(entityName)
        infoType = type(info)
        return correction and (canActivate or infoType == NeedEntitySelection) or infoType == IgnoreEntitySelection

    def _replaceEquipmentKeyHandler(self, keysContainer, intCD, deviceName):
        tempDeviceName = VEHICLE_DEVICE_IN_COMPLEX_ITEM.get(deviceName, deviceName)
        for key in keysContainer:
            if tempDeviceName in keysContainer[key].args:
                keysContainer[key] = partial(self._handleEquipmentPressed, intCD, deviceName)

    @staticmethod
    def _isHalloweenEquipment(item):
        return 'halloween_equipment' in item.getDescriptor().tags

    @classmethod
    def _isHalloweenEmptySlot(cls, item):
        return cls._isHalloweenEquipment(item) and 'empty_slot' in item.getDescriptor().tags

    @classmethod
    def _isHalloweenPassive(cls, item):
        return cls._isHalloweenEquipment(item) and item.getDescriptor().cooldownSeconds <= 0.0

    @staticmethod
    def _isSuperShell(item):
        return 'superShell' in item.getDescriptor().tags

    def _bookNextSlotIdx(self, startIdx, endIdx):
        for idx in range(startIdx, endIdx + 1):
            if self._mask & 1 << idx == 0:
                self._mask |= 1 << idx
                return idx

        return None
