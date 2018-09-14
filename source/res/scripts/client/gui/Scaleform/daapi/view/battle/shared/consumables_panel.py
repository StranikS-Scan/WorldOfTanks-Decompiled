# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/consumables_panel.py
import math
from functools import partial
import BigWorld
import CommandMapping
import SoundGroups
from constants import EQUIPMENT_STAGES
from debug_utils import LOG_ERROR
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.meta.ConsumablesPanelMeta import ConsumablesPanelMeta
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.battle_control import g_sessionProvider
from gui.battle_control.battle_constants import VEHICLE_DEVICE_IN_COMPLEX_ITEM, GUN_RELOADING_VALUE_TYPE
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.utils.key_mapping import getScaleformKey
from helpers import i18n
from shared_utils import forEach
AMMO_ICON_PATH = '../maps/icons/ammopanel/battle_ammo/%s'
NO_AMMO_ICON_PATH = '../maps/icons/ammopanel/battle_ammo/NO_%s'
COMMAND_AMMO_CHOICE_MASK = 'CMD_AMMO_CHOICE_{0:d}'
PANEL_MAX_LENGTH = 12
AMMO_START_IDX = 0
AMMO_END_IDX = 2
AMMO_RANGE = xrange(AMMO_START_IDX, AMMO_END_IDX + 1)
AMMO_FULL_MASK = sum([ 1 << idx for idx in AMMO_RANGE ])
EQUIPMENT_START_IDX = 3
EQUIPMENT_END_IDX = 5
EQUIPMENT_RANGE = xrange(EQUIPMENT_START_IDX, EQUIPMENT_END_IDX + 1)
EQUIPMENT_FULL_MASK = sum([ 1 << idx for idx in EQUIPMENT_RANGE ])
ORDERS_START_IDX = 6
ORDERS_END_IDX = 8
ORDERS_RANGE = xrange(ORDERS_START_IDX, ORDERS_END_IDX + 1)
ORDERS_FULL_MASK = sum([ 1 << idx for idx in ORDERS_RANGE ])
OPT_DEVICE_START_IDX = 9
OPT_DEVICE_END_IDX = 11
OPT_DEVICE_RANGE = xrange(OPT_DEVICE_START_IDX, OPT_DEVICE_END_IDX + 1)
OPT_DEVICE_FULL_MASK = sum([ 1 << idx for idx in OPT_DEVICE_RANGE ])
EMPTY_EQUIPMENTS_SLICE = [0] * (EQUIPMENT_END_IDX - EQUIPMENT_START_IDX + 1)
EMPTY_ORDERS_SLICE = [0] * (ORDERS_START_IDX - ORDERS_END_IDX + 1)
EMPTY_EQUIPMENT_TOOLTIP = i18n.makeString('#ingame_gui:consumables_panel/equipment/tooltip/empty')
TOOLTIP_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}\n/{{BODY}}{1:>s}{{/BODY}}'
TOOLTIP_NO_BODY_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}'

class ConsumablesPanel(ConsumablesPanelMeta, BattleGUIKeyHandler):

    def __init__(self):
        super(ConsumablesPanel, self).__init__()
        self.__cds = [None] * PANEL_MAX_LENGTH
        self.__mask = 0
        self.__keys = {}
        self.__currentOrderIdx = -1
        return

    def onClickedToSlot(self, bwKey):
        self.__handleBWKey(int(bwKey))

    def onPopUpClosed(self):
        keys = {}
        for idx, bwKey, _, handler in self.__getKeysGenerator():
            if handler:
                keys[bwKey] = handler

        self.__keys.clear()
        self.__keys = keys
        ctrl = g_sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        return

    def handleEscKey(self, isDown):
        if isDown:
            self.__collapseEquipmentSlot()
            return True
        else:
            return False

    def _populate(self):
        super(ConsumablesPanel, self)._populate()
        self.__addListeners()

    def _dispose(self):
        self.__removeListeners()
        self.__keys.clear()
        super(ConsumablesPanel, self)._dispose()

    def __addListeners(self):
        vehicleCtrl = g_sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
            vehicleCtrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
        ammoCtrl = g_sessionProvider.shared.ammo
        if ammoCtrl is not None:
            self.__fillShells(ammoCtrl)
            ammoCtrl.onShellsAdded += self.__onShellsAdded
            ammoCtrl.onShellsUpdated += self.__onShellsUpdated
            ammoCtrl.onNextShellChanged += self.__onNextShellChanged
            ammoCtrl.onCurrentShellChanged += self.__onCurrentShellChanged
            ammoCtrl.onGunReloadTimeSet += self.__onGunReloadTimeSet
        eqCtrl = g_sessionProvider.shared.equipments
        if eqCtrl is not None:
            self.__fillEquipments(eqCtrl)
            eqCtrl.onEquipmentAdded += self.__onEquipmentAdded
            eqCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
            eqCtrl.onEquipmentCooldownInPercent += self.__onEquipmentCooldownInPercent
        optDevicesCtrl = g_sessionProvider.shared.optionalDevices
        if optDevicesCtrl is not None:
            self.__fillOptionalDevices(optDevicesCtrl)
            optDevicesCtrl.onOptionalDeviceAdded += self.__onOptionalDeviceAdded
            optDevicesCtrl.onOptionalDeviceUpdated += self.__onOptionalDeviceUpdated
        CommandMapping.g_instance.onMappingChanged += self.__onMappingChanged
        g_eventBus.addListener(GameEvent.CHOICE_CONSUMABLE, self.__handleConsumableChoice, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def __removeListeners(self):
        g_eventBus.removeListener(GameEvent.CHOICE_CONSUMABLE, self.__handleConsumableChoice, scope=EVENT_BUS_SCOPE.BATTLE)
        CommandMapping.g_instance.onMappingChanged -= self.__onMappingChanged
        vehicleCtrl = g_sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            vehicleCtrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
            vehicleCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        ammoCtrl = g_sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellsAdded -= self.__onShellsAdded
            ammoCtrl.onShellsUpdated -= self.__onShellsUpdated
            ammoCtrl.onNextShellChanged -= self.__onNextShellChanged
            ammoCtrl.onCurrentShellChanged -= self.__onCurrentShellChanged
            ammoCtrl.onGunReloadTimeSet -= self.__onGunReloadTimeSet
        eqCtrl = g_sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentAdded -= self.__onEquipmentAdded
            eqCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
            eqCtrl.onEquipmentCooldownInPercent -= self.__onEquipmentCooldownInPercent
        optDevicesCtrl = g_sessionProvider.shared.optionalDevices
        if optDevicesCtrl is not None:
            optDevicesCtrl.onOptionalDeviceAdded -= self.__onOptionalDeviceAdded
            optDevicesCtrl.onOptionalDeviceUpdated -= self.__onOptionalDeviceUpdated
        return

    def __genNextIdx(self, full, start):
        bits = self.__mask & full
        if not bits:
            idx = start
        else:
            idx = int(math.log(bits, 2)) + 1
        assert -1 < idx < PANEL_MAX_LENGTH - 1
        self.__mask |= 1 << idx
        return idx

    def __genKey(self, idx):
        assert -1 < idx < PANEL_MAX_LENGTH - 1
        cmdMappingKey = COMMAND_AMMO_CHOICE_MASK.format(idx + 1 if idx < 9 else 0)
        bwKey = CommandMapping.g_instance.get(cmdMappingKey)
        sfKey = 0
        if bwKey is not None and bwKey != 0:
            sfKey = getScaleformKey(bwKey)
        return (bwKey, sfKey)

    def __makeShellTooltip(self, descriptor, piercingPower):
        kind = descriptor['kind']
        header = i18n.makeString('#ingame_gui:shells_kinds/{0:>s}'.format(kind), caliber=BigWorld.wg_getNiceNumberFormat(descriptor['caliber']), userString=descriptor['userString'])
        if GUI_SETTINGS.technicalInfo:
            body = i18n.makeString('#ingame_gui:shells_kinds/params', damage=str(int(descriptor['damage'][0])), piercingPower=str(piercingPower))
            fmt = TOOLTIP_FORMAT
        else:
            body = ''
            fmt = TOOLTIP_NO_BODY_FORMAT
        return fmt.format(header, body)

    def __getKeysGenerator(self):
        getEquipment = g_sessionProvider.shared.equipments.getEquipment
        for idx, intCD in enumerate(self.__cds):
            if not intCD:
                yield (idx,
                 None,
                 None,
                 None)
            bwKey, sfKey = self.__genKey(idx)
            handler = None
            if idx in AMMO_RANGE:
                handler = partial(self.__handleAmmoPressed, intCD)
            elif idx in EQUIPMENT_RANGE or idx in ORDERS_RANGE:
                item = getEquipment(intCD)
                if item and item.getTag() and item.getQuantity() > 0:
                    if item.isEntityRequired():
                        handler = partial(self.__handleEquipmentExpanded, intCD)
                    else:
                        handler = partial(self.__handleEquipmentPressed, intCD)
            yield (idx,
             bwKey,
             sfKey,
             handler)

        return

    def __onMappingChanged(self, *args):
        keys = {}
        slots = []
        for idx, bwKey, sfKey, handler in self.__getKeysGenerator():
            if handler:
                keys[bwKey] = handler
                slots.append((idx, bwKey, sfKey))

        self.as_setKeysToSlotsS(slots)
        self.__keys.clear()
        self.__keys = keys

    def __handleConsumableChoice(self, event):
        self.__handleBWKey(event.ctx['key'])

    def __handleBWKey(self, bwKey):
        if bwKey in self.__keys:
            handler = self.__keys[bwKey]
            if handler and callable(handler):
                handler()

    def __handleAmmoPressed(self, intCD):
        ctrl = g_sessionProvider.shared.ammo
        if ctrl is not None:
            ctrl.changeSetting(intCD)
        return

    def __handleEquipmentPressed(self, intCD, entityName=None):
        ctrl = g_sessionProvider.shared.equipments
        if ctrl is None:
            return
        else:
            result, error = ctrl.changeSetting(intCD, entityName=entityName, avatar=BigWorld.player())
            if not result and error:
                ctrl = g_sessionProvider.shared.messages
                if ctrl is not None:
                    ctrl.showVehicleError(error.key, error.ctx)
            else:
                self.__collapseEquipmentSlot()
            return

    def __handleEquipmentExpanded(self, intCD):
        ctrl = g_sessionProvider.shared.equipments
        if ctrl is None:
            return
        else:
            result, error = ctrl.changeSetting(intCD)
            if not result and error:
                ctrl = g_sessionProvider.shared.messages
                if ctrl is not None:
                    ctrl.showVehicleError(error.key, error.ctx)
                return
            if intCD not in self.__cds:
                LOG_ERROR('Equipment is not found in panel', intCD, self.__cds)
                return
            item = ctrl.getEquipment(intCD)
            if not item:
                LOG_ERROR('Equipment is not found in control', intCD)
                return
            slots = []
            keys = {}
            for entityIdx, (itemName, entityName, entityState) in enumerate(item.getGuiIterator()):
                bwKey, sfKey = self.__genKey(entityIdx)
                keys[bwKey] = partial(self.__handleEquipmentPressed, intCD, entityName)
                slots.append({'bwKeyCode': bwKey,
                 'sfKeyCode': sfKey,
                 'entityName': itemName,
                 'entityState': entityState})

            self.__expandEquipmentSlot(self.__cds.index(intCD), slots)
            self.__keys.clear()
            self.__keys = keys
            ctrl = g_sessionProvider.shared.vehicleState
            if ctrl is not None:
                ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            return

    def __onShellsAdded(self, intCD, descriptor, quantity, _, gunSettings):
        toolTip = self.__makeShellTooltip(descriptor, int(gunSettings.getPiercingPower(intCD)))
        icon = descriptor['icon'][0]
        shellIconPath = AMMO_ICON_PATH % icon
        noShellIconPath = NO_AMMO_ICON_PATH % icon
        idx = self.__genNextIdx(AMMO_FULL_MASK, AMMO_START_IDX)
        self.__cds[idx] = intCD
        bwKey, sfKey = self.__genKey(idx)
        self.__keys[bwKey] = partial(self.__handleAmmoPressed, intCD)
        self.as_addShellSlotS(idx, bwKey, sfKey, quantity, gunSettings.clip.size, shellIconPath, noShellIconPath, toolTip)

    def __onShellsUpdated(self, intCD, quantity, *args):
        if intCD in self.__cds:
            self.as_setItemQuantityInSlotS(self.__cds.index(intCD), quantity)
        else:
            LOG_ERROR('Ammo is not found in panel', intCD, self.__cds)

    def __onNextShellChanged(self, intCD):
        if intCD in self.__cds:
            self.as_setNextShellS(self.__cds.index(intCD))
        else:
            LOG_ERROR('Ammo is not found in panel', intCD, self.__cds)

    def __onCurrentShellChanged(self, intCD):
        if intCD in self.__cds:
            self.as_setCurrentShellS(self.__cds.index(intCD))
        else:
            LOG_ERROR('Ammo is not found in panel', intCD, self.__cds)

    def __onGunReloadTimeSet(self, currShellCD, state):
        if currShellCD in self.__cds:
            index = self.__cds.index(currShellCD)
            valueType = state.getValueType()
            if valueType == GUN_RELOADING_VALUE_TYPE.TIME:
                self.as_setCoolDownTimeS(index, state.getActualValue())
            elif valueType == GUN_RELOADING_VALUE_TYPE.PERCENT:
                self.as_setCoolDownPosAsPercentS(index, state.getActualValue())
        else:
            LOG_ERROR('Ammo is not found in panel', currShellCD, self.__cds)

    def __onEquipmentAdded(self, intCD, item):
        if item:
            if item.isAvatar():
                self.__addOrderSlot(intCD, item)
            else:
                self.__addEquipmentSlot(intCD, item)
        else:
            idx = self.__genNextIdx(EQUIPMENT_FULL_MASK + ORDERS_FULL_MASK, EQUIPMENT_START_IDX)
            self.__cds[idx] = intCD
            bwKey, sfKey = self.__genKey(idx)
            self.as_addEquipmentSlotS(idx, bwKey, sfKey, None, 0, 0, None, EMPTY_EQUIPMENT_TOOLTIP)
            snap = self.__cds[EQUIPMENT_START_IDX:EQUIPMENT_END_IDX + 1]
            if snap == EMPTY_EQUIPMENTS_SLICE:
                self.as_showEquipmentSlotsS(False)
            snap = self.__cds[ORDERS_START_IDX:ORDERS_END_IDX + 1]
            if snap == EMPTY_ORDERS_SLICE:
                self.as_showOrdersSlotsS(False)
        return

    def __onEquipmentUpdated(self, intCD, item):
        if intCD in self.__cds:
            idx = self.__cds.index(intCD)
            quantity = item.getQuantity()
            currentTime = item.getTimeRemaining()
            maxTime = item.getTotalTime()
            if item.isAvatar():
                self.as_setItemTimeQuantityInSlotS(idx, quantity, currentTime, maxTime)
                self.__updateOrderSlot(idx, item)
            else:
                if not quantity:
                    SoundGroups.g_instance.playSound2D('battle_equipment_%d' % intCD)
                self.as_setItemTimeQuantityInSlotS(idx, quantity, currentTime, maxTime)
                self.onPopUpClosed()
        else:
            LOG_ERROR('Equipment is not found in panel', intCD, self.__cds)

    def __onEquipmentCooldownInPercent(self, intCD, percent):
        if intCD in self.__cds:
            self.as_setCoolDownPosAsPercentS(self.__cds.index(intCD), percent)

    def __addEquipmentSlot(self, intCD, item):
        idx = self.__genNextIdx(EQUIPMENT_FULL_MASK, EQUIPMENT_START_IDX)
        self.__cds[idx] = intCD
        descriptor = item.getDescriptor()
        iconPath = '../maps/icons/artefact/%s.png' % descriptor.icon[0]
        toolTip = TOOLTIP_FORMAT.format(descriptor.userString, descriptor.description)
        tag = item.getTag()
        if tag:
            bwKey, sfKey = self.__genKey(idx)
            if item.isEntityRequired():
                handler = partial(self.__handleEquipmentExpanded, intCD)
            else:
                handler = partial(self.__handleEquipmentPressed, intCD)
            if item.getQuantity() > 0:
                self.__keys[bwKey] = handler
        else:
            bwKey, sfKey = (None, None)
        self.as_addEquipmentSlotS(idx, bwKey, sfKey, tag, item.getQuantity(), item.getTimeRemaining(), iconPath, toolTip)
        return None

    def __addOrderSlot(self, intCD, item):
        idx = self.__genNextIdx(ORDERS_FULL_MASK, ORDERS_START_IDX)
        self.__cds[idx] = intCD
        descriptor = item.getDescriptor()
        iconPath = '../maps/icons/artefact/%s.png' % descriptor.icon[0]
        toolTip = TOOLTIP_FORMAT.format(descriptor.userString, descriptor.description)
        bwKey, sfKey = self.__genKey(idx)
        self.__keys[bwKey] = partial(self.__handleEquipmentPressed, intCD)
        maxTime = item.getTotalTime()
        self.as_addOrderSlotS(idx, bwKey, sfKey, item.getQuantity(), iconPath, toolTip, item.getStage() in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING), item.isQuantityUsed(), item.getTimeRemaining(), maxTime)
        self.__updateOrderSlot(idx, item)

    def __updateOrderSlot(self, idx, item):
        if item.getStage() == EQUIPMENT_STAGES.READY:
            self.as_setOrderAvailableS(idx, True)
        elif item.getStage() == EQUIPMENT_STAGES.PREPARING:
            self.__currentOrderIdx = idx
            self.as_setOrderActivatedS(idx)
        else:
            self.as_setOrderAvailableS(idx, False)
        if item.getStage() != EQUIPMENT_STAGES.PREPARING and self.__currentOrderIdx == idx:
            self.__currentOrderIdx = -1
            self.as_setOrderActivatedS(-1)

    def __onOptionalDeviceAdded(self, intCD, descriptor, isOn):
        idx = self.__genNextIdx(OPT_DEVICE_FULL_MASK, OPT_DEVICE_START_IDX)
        self.__cds[idx] = intCD
        iconPath = descriptor.icon[0]
        toolTip = TOOLTIP_FORMAT.format(descriptor.userString, descriptor.description)
        self.as_addOptionalDeviceSlotS(idx, -1 if isOn else 0, iconPath, toolTip)

    def __onOptionalDeviceUpdated(self, intCD, isOn):
        if intCD in self.__cds:
            self.as_setCoolDownTimeS(self.__cds.index(intCD), -1 if isOn else 0)
        else:
            LOG_ERROR('Optional device is not found in panel', intCD, self.__cds)

    def __onPostMortemSwitched(self):
        self.as_switchToPosmortemS()

    def __onRespawnBaseMoving(self):
        self.__cds = [None] * PANEL_MAX_LENGTH
        self.__mask = 0
        self.__keys.clear()
        self.__currentOrderIdx = -1
        self.as_resetS()
        return

    def __onVehicleStateUpdated(self, state, value):
        if state != VEHICLE_VIEW_STATE.DEVICES:
            return
        else:
            deviceName, _, actualState = value
            if deviceName in VEHICLE_DEVICE_IN_COMPLEX_ITEM:
                itemName = VEHICLE_DEVICE_IN_COMPLEX_ITEM[deviceName]
            else:
                itemName = deviceName
            idx = int(self.as_updateEntityStateS(itemName, actualState))
            if idx and idx < len(self.__cds):
                intCD = self.__cds[idx]
                ctrl = g_sessionProvider.shared.equipments
                if ctrl is None:
                    return
                item = ctrl.getEquipment(intCD)
                if item and item.isEntityRequired():
                    bwKey, _ = self.__genKey(idx)
                    self.__keys[bwKey] = partial(self.__handleEquipmentPressed, self.__cds[idx], deviceName)
            return

    def __expandEquipmentSlot(self, index, slots):
        self.as_expandEquipmentSlotS(index, slots)
        self.app.registerGuiKeyHandler(self)

    def __collapseEquipmentSlot(self):
        self.as_collapseEquipmentSlotS()
        self.app.unregisterGuiKeyHandler(self)

    def __fillShells(self, ctrl):
        forEach(lambda args: self.__onShellsAdded(*args), ctrl.getOrderedShellsLayout())
        shellCD = ctrl.getNextShellCD()
        if shellCD is not None:
            self.__onNextShellChanged(shellCD)
        shellCD = ctrl.getCurrentShellCD()
        if shellCD is not None:
            self.__onCurrentShellChanged(shellCD)
        return

    def __fillEquipments(self, ctrl):
        forEach(lambda args: self.__onEquipmentAdded(*args), ctrl.getOrderedEquipmentsLayout())

    def __fillOptionalDevices(self, ctrl):
        forEach(lambda args: self.__onOptionalDeviceAdded(*args), ctrl.getOrderedOptionalDevicesLayout())
