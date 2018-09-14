# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/ConsumablesPanel.py
from functools import partial
import math
import BigWorld
import CommandMapping
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.battle import COMMAND_AMMO_CHOICE_MASK, AMMO_ICON_PATH, NO_AMMO_ICON_PATH
from gui.battle_control import g_sessionProvider
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, VEHICLE_DEVICE_IN_COMPLEX_ITEM
from gui.shared.utils.key_mapping import getScaleformKey
from helpers import i18n
PANEL_MAX_LENGTH = 9
AMMO_START_IDX = 0
AMMO_END_IDX = 2
AMMO_RANGE = xrange(AMMO_START_IDX, AMMO_END_IDX + 1)
AMMO_FULL_MASK = sum([ 1 << idx for idx in AMMO_RANGE ])
EQUIPMENT_START_IDX = 3
EQUIPMENT_END_IDX = 5
EQUIPMENT_RANGE = xrange(EQUIPMENT_START_IDX, EQUIPMENT_END_IDX + 1)
EQUIPMENT_FULL_MASK = sum([ 1 << idx for idx in EQUIPMENT_RANGE ])
OPT_DEVICE_START_IDX = 6
OPT_DEVICE_END_IDX = 8
OPT_DEVICE_RANGE = xrange(OPT_DEVICE_START_IDX, OPT_DEVICE_END_IDX + 1)
OPT_DEVICE_FULL_MASK = sum([ 1 << idx for idx in OPT_DEVICE_RANGE ])
EMPTY_EQUIPMENTS_SLICE = [0] * (EQUIPMENT_END_IDX - EQUIPMENT_START_IDX + 1)
EMPTY_EQUIPMENT_TOOLTIP = i18n.makeString('#ingame_gui:consumables_panel/equipment/tooltip/empty')

class ConsumablesPanel(object):

    def __init__(self, parentUI):
        self.__ui = parentUI
        self.__cds = [None] * PANEL_MAX_LENGTH
        self.__mask = 0
        self.__keys = {}
        return

    def start(self):
        self.__flashObject = self.__ui.getMember('_level0.consumablesPanel')
        if self.__flashObject:
            self.__flashObject.resync()
            self.__flashObject.script = self
            self.__addListeners()
        else:
            LOG_ERROR('Display object is not found in the swf file.')

    def destroy(self):
        self.__removeListeners()
        self.__keys.clear()
        self.__ui = None
        if self.__flashObject is not None:
            self.__flashObject.script = None
            self.__flashObject = None
        return

    def handleKey(self, bwKey):
        if bwKey in self.__keys:
            handler = self.__keys[bwKey]
            if handler and callable(handler):
                handler()

    def bindCommands(self):
        keys = {}
        slots = []
        for idx, bwKey, sfKey, handler in self.__getKeysGenerator():
            if handler:
                keys[bwKey] = handler
                slots.append((idx, bwKey, sfKey))

        self.__flashObject.setKeysToSlots(slots)
        self.__keys.clear()
        self.__keys = keys

    def onClickedToSlot(self, bwKey):
        self.handleKey(int(bwKey))

    def onPopUpClosed(self):
        keys = {}
        for idx, bwKey, _, handler in self.__getKeysGenerator():
            if handler:
                keys[bwKey] = handler

        self.__keys.clear()
        self.__keys = keys
        g_sessionProvider.onVehicleStateUpdated -= self.__onVehicleStateUpdated

    def __callFlash(self, funcName, args = None):
        self.__ui.call('battle.consumablesPanel.%s' % funcName, args)

    def __addListeners(self):
        g_sessionProvider.onPostMortemSwitched += self.__onPostMortemSwitched
        ammoCtrl = g_sessionProvider.getAmmoCtrl()
        ammoCtrl.onShellsAdded += self.__onShellsAdded
        ammoCtrl.onShellsUpdated += self.__onShellsUpdated
        ammoCtrl.onNextShellChanged += self.__onNextShellChanged
        ammoCtrl.onCurrentShellChanged += self.__onCurrentShellChanged
        ammoCtrl.onGunReloadTimeSet += self.__onGunReloadTimeSet
        ammoCtrl.onGunReloadTimeSetInPercent += self.__onGunReloadTimeSetInPercent
        eqCtrl = g_sessionProvider.getEquipmentsCtrl()
        eqCtrl.onEquipmentAdded += self.__onEquipmentAdded
        eqCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
        optDevicesCtrl = g_sessionProvider.getOptDevicesCtrl()
        optDevicesCtrl.onOptionalDeviceAdded += self.__onOptionalDeviceAdded
        optDevicesCtrl.onOptionalDeviceUpdated += self.__onOptionalDeviceUpdated

    def __removeListeners(self):
        g_sessionProvider.onPostMortemSwitched -= self.__onPostMortemSwitched
        g_sessionProvider.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        ammoCtrl = g_sessionProvider.getAmmoCtrl()
        ammoCtrl.onShellsAdded -= self.__onShellsAdded
        ammoCtrl.onShellsUpdated -= self.__onShellsUpdated
        ammoCtrl.onNextShellChanged -= self.__onNextShellChanged
        ammoCtrl.onCurrentShellChanged -= self.__onCurrentShellChanged
        ammoCtrl.onGunReloadTimeSet -= self.__onGunReloadTimeSet
        ammoCtrl.onGunReloadTimeSetInPercent -= self.__onGunReloadTimeSetInPercent
        eqCtrl = g_sessionProvider.getEquipmentsCtrl()
        eqCtrl.onEquipmentAdded -= self.__onEquipmentAdded
        eqCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        optDevicesCtrl = g_sessionProvider.getOptDevicesCtrl()
        optDevicesCtrl.onOptionalDeviceAdded -= self.__onOptionalDeviceAdded
        optDevicesCtrl.onOptionalDeviceUpdated -= self.__onOptionalDeviceUpdated

    def __genNextIdx(self, full, start):
        bits = self.__mask & full
        if not bits:
            idx = start
        else:
            idx = int(math.log(bits, 2)) + 1
        raise -1 < idx < 10 or AssertionError
        self.__mask |= 1 << idx
        return idx

    def __genKey(self, idx):
        if not -1 < idx < 10:
            raise AssertionError
            cmdMappingKey = COMMAND_AMMO_CHOICE_MASK.format(idx + 1 if idx < 9 else 0)
            bwKey = CommandMapping.g_instance.get(cmdMappingKey)
            sfKey = 0
            sfKey = bwKey is not None and bwKey != 0 and getScaleformKey(bwKey)
        return (bwKey, sfKey)

    def __makeShellTooltip(self, descriptor, piercingPower):
        kind = descriptor['kind']
        return i18n.makeString('#ingame_gui:shells_kinds/{0:>s}'.format(kind), caliber=BigWorld.wg_getNiceNumberFormat(descriptor['caliber']), userString=descriptor['userString'], damage=str(int(descriptor['damage'][0])), piercingPower=str(piercingPower))

    def __getKeysGenerator(self):
        getEquipment = g_sessionProvider.getEquipmentsCtrl().getEquipment
        for idx, intCD in enumerate(self.__cds):
            if not intCD:
                yield (idx,
                 None,
                 None,
                 None)
            else:
                bwKey, sfKey = self.__genKey(idx)
                handler = None
                if idx in AMMO_RANGE:
                    handler = partial(self.__handleAmmoPressed, intCD)
                elif idx in EQUIPMENT_RANGE:
                    item = getEquipment(intCD)
                    if item and item.getTag():
                        if item.isEntityRequired():
                            handler = partial(self.__handleEquipmentExpanded, intCD)
                        else:
                            handler = partial(self.__handleEquipmentPressed, intCD)
                yield (idx,
                 bwKey,
                 sfKey,
                 handler)

        return

    def __handleAmmoPressed(self, intCD):
        g_sessionProvider.getAmmoCtrl().changeSetting(intCD)

    def __handleEquipmentPressed(self, intCD, entityName = None):
        result, error = g_sessionProvider.getEquipmentsCtrl().changeSetting(intCD, entityName=entityName, avatar=BigWorld.player())
        if not result and error:
            self.__ui.vErrorsPanel.showMessage(error.key, error.ctx)
        else:
            self.__flashObject.collapseEquipmentSlot()

    def __handleEquipmentExpanded(self, intCD):
        if intCD not in self.__cds:
            LOG_ERROR('Equipment is not found in panel', intCD, self.__cds)
            return
        item = g_sessionProvider.getEquipmentsCtrl().getEquipment(intCD)
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

        self.__flashObject.expandEquipmentSlot(self.__cds.index(intCD), slots)
        self.__keys.clear()
        self.__keys = keys
        g_sessionProvider.onVehicleStateUpdated += self.__onVehicleStateUpdated

    def __onShellsAdded(self, intCD, descriptor, quantity, _, gunSettings):
        toolTip = self.__makeShellTooltip(descriptor, int(gunSettings.getPiercingPower(intCD)))
        icon = descriptor['icon'][0]
        shellIconPath = AMMO_ICON_PATH % icon
        noShellIconPath = NO_AMMO_ICON_PATH % icon
        idx = self.__genNextIdx(AMMO_FULL_MASK, AMMO_START_IDX)
        self.__cds[idx] = intCD
        bwKey, sfKey = self.__genKey(idx)
        self.__keys[bwKey] = partial(self.__handleAmmoPressed, intCD)
        self.__flashObject.addShellSlot(idx, bwKey, sfKey, quantity, gunSettings.clip.size, shellIconPath, noShellIconPath, toolTip)

    def __onShellsUpdated(self, intCD, quantity, *args):
        if intCD in self.__cds:
            self.__flashObject.setItemQuantityInSlot(self.__cds.index(intCD), quantity)
        else:
            LOG_ERROR('Ammo is not found in panel', intCD, self.__cds)

    def __onNextShellChanged(self, intCD):
        if intCD in self.__cds:
            self.__flashObject.setNextShell(self.__cds.index(intCD))
        else:
            LOG_ERROR('Ammo is not found in panel', intCD, self.__cds)

    def __onCurrentShellChanged(self, intCD):
        if intCD in self.__cds:
            self.__flashObject.setCurrentShell(self.__cds.index(intCD))
        else:
            LOG_ERROR('Ammo is not found in panel', intCD, self.__cds)

    def __onGunReloadTimeSet(self, currShellCD, timeLeft, _):
        if currShellCD in self.__cds:
            self.__flashObject.setCoolDownTime(self.__cds.index(currShellCD), timeLeft)
        else:
            LOG_ERROR('Ammo is not found in panel', currShellCD, self.__cds)

    def __onGunReloadTimeSetInPercent(self, currShellCD, percent):
        if currShellCD in self.__cds:
            self.__flashObject.setCoolDownPosAsPercent(self.__cds.index(currShellCD), percent)

    def __onEquipmentAdded(self, intCD, item):
        idx = self.__genNextIdx(EQUIPMENT_FULL_MASK, EQUIPMENT_START_IDX)
        self.__cds[idx] = intCD
        if item:
            descriptor = item.getDescriptor()
            iconPath = descriptor.icon[0]
            toolTip = '{0:>s}\n{1:>s}'.format(descriptor.userString, descriptor.description)
            tag = item.getTag()
            if tag:
                bwKey, sfKey = self.__genKey(idx)
                if item.isEntityRequired():
                    handler = partial(self.__handleEquipmentExpanded, intCD)
                else:
                    handler = partial(self.__handleEquipmentPressed, intCD)
                self.__keys[bwKey] = handler
            else:
                bwKey, sfKey = (None, None)
            self.__flashObject.addEquipmentSlot(idx, bwKey, sfKey, tag, item.getQuantity(), item.getTimeRemaining(), iconPath, toolTip)
        else:
            self.__flashObject.addEquipmentSlot(idx, None, None, None, 0, 0, None, EMPTY_EQUIPMENT_TOOLTIP)
            if self.__cds[EQUIPMENT_START_IDX:EQUIPMENT_END_IDX + 1] == EMPTY_EQUIPMENTS_SLICE:
                self.__flashObject.showEquipmentSlots(False)
        return

    def __onEquipmentUpdated(self, intCD, quantity, timeRemaining):
        if intCD in self.__cds:
            self.__flashObject.setItemTimeQuantityInSlot(self.__cds.index(intCD), quantity, timeRemaining)
        else:
            LOG_ERROR('Equipment is not found in panel', intCD, self.__cds)

    def __onOptionalDeviceAdded(self, intCD, descriptor, isOn):
        idx = self.__genNextIdx(OPT_DEVICE_FULL_MASK, OPT_DEVICE_START_IDX)
        self.__cds[idx] = intCD
        iconPath = descriptor.icon[0]
        toolTip = '{0:>s}\n{1:>s}'.format(descriptor.userString, descriptor.description)
        self.__flashObject.addOptionalDeviceSlot(idx, -1 if isOn else 0, iconPath, toolTip)

    def __onOptionalDeviceUpdated(self, intCD, isOn):
        if intCD in self.__cds:
            self.__flashObject.setCoolDownTime(self.__cds.index(intCD), -1 if isOn else 0)
        else:
            LOG_ERROR('Optional device is not found in panel', intCD, self.__cds)

    def __onPostMortemSwitched(self):
        self.__flashObject.switchToPosmortem()

    def __onVehicleStateUpdated(self, state, value):
        if state != VEHICLE_VIEW_STATE.DEVICES:
            return
        deviceName, _, actualState = value
        if deviceName in VEHICLE_DEVICE_IN_COMPLEX_ITEM:
            itemName = VEHICLE_DEVICE_IN_COMPLEX_ITEM[deviceName]
        else:
            itemName = deviceName
        idx = int(self.__flashObject.updateEntityState(itemName, actualState))
        if idx and idx < len(self.__cds):
            intCD = self.__cds[idx]
            item = g_sessionProvider.getEquipmentsCtrl().getEquipment(intCD)
            if item and item.isEntityRequired():
                bwKey, _ = self.__genKey(idx)
                self.__keys[bwKey] = partial(self.__handleEquipmentPressed, self.__cds[idx], deviceName)
