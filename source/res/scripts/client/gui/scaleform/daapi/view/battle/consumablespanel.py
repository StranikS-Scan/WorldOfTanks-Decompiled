# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/ConsumablesPanel.py
from collections import namedtuple
from functools import partial
import math
import BigWorld
import CommandMapping
import rage
from constants import EQUIPMENT_STAGES
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.Scaleform.daapi.view.battle import COMMAND_AMMO_CHOICE_MASK, AMMO_ICON_PATH, NO_AMMO_ICON_PATH
from gui.battle_control import g_sessionProvider
from gui.battle_control.arena_info import isEventBattle, hasRage
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, VEHICLE_DEVICE_IN_COMPLEX_ITEM
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.utils.key_mapping import getScaleformKey
from gui.shared.utils.plugins import PluginsCollection, IPlugin
from helpers import i18n
import SoundGroups
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

class _FalloutSlotViewProps(namedtuple('_FalloutSlotViewProps', ('useStandardLayout',
 'drawHitArea',
 'hitAreaAlpha',
 'hitAreaWidth',
 'hitAreaHeight',
 'hitAreaXOffset',
 'hitAreaYOffset',
 'slot_Y_Offset',
 'actualSlotWidth',
 'slotType_h_margin',
 'slot_h_margin'))):

    def __new__(cls, useStandardLayout = True, drawHitArea = True, hitAreaAlpha = 0.5, hitAreaWidth = 47, hitAreaHeight = 47, hitAreaXOffset = 5, hitAreaYOffset = 5, slot_Y_Offset = -11, actualSlotWidth = 47, slotType_h_margin = 8, slot_h_margin = 1):
        return super(_FalloutSlotViewProps, cls).__new__(cls, useStandardLayout, drawHitArea, hitAreaAlpha, hitAreaWidth, hitAreaHeight, hitAreaXOffset, hitAreaYOffset, slot_Y_Offset, actualSlotWidth, slotType_h_margin, slot_h_margin)


class _RageBarViewProps(namedtuple('_RageBarViewProps', ('maxValue',
 'curValue',
 'rageBar_y_offset',
 'rageBar_x_offset'))):

    def __new__(cls, maxValue = 0, curValue = 0, rageBar_y_offset = 54, rageBar_x_offset = 7):
        return super(_RageBarViewProps, cls).__new__(cls, maxValue, curValue, rageBar_y_offset, rageBar_x_offset)


class ConsumablesPanel(object):

    def __init__(self, parentUI):
        self.__ui = parentUI
        self.__flashObject = None
        self.__cds = [None] * PANEL_MAX_LENGTH
        self.__mask = 0
        self.__keys = {}
        self.__currentOrderIdx = -1
        self.__plugins = PluginsCollection(self)
        plugins = {}
        if hasRage():
            plugins['rageBar'] = _RageBarPlugin
        self.__plugins.addPlugins(plugins)
        return

    def start(self):
        self.__flashObject = self.__ui.getMember('_level0.consumablesPanel')
        if self.__flashObject:
            self.__flashObject.resync()
            self.__flashObject.script = self
            self.__plugins.init()
            self.__plugins.start()
            props = _FalloutSlotViewProps(useStandardLayout=not hasRage())
            self.__flashObject.setProperties(isEventBattle(), props._asdict())
            self.__addListeners()
        else:
            LOG_ERROR('Display object is not found in the swf file.')

    def destroy(self):
        self.__plugins.stop()
        self.__plugins.fini()
        self.__removeListeners()
        self.__keys.clear()
        self.__ui = None
        if self.__flashObject is not None:
            self.__flashObject.script = None
            self.__flashObject = None
        return

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
        self.__handleBWKey(int(bwKey))

    def onPopUpClosed(self):
        keys = {}
        for idx, bwKey, _, handler in self.__getKeysGenerator():
            if handler:
                keys[bwKey] = handler

        self.__keys.clear()
        self.__keys = keys
        ctrl = g_sessionProvider.getVehicleStateCtrl()
        ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated

    @property
    def flashObject(self):
        return self.__flashObject

    def __callFlash(self, funcName, args = None):
        self.__ui.call('battle.consumablesPanel.%s' % funcName, args)

    def __addListeners(self):
        vehicleCtrl = g_sessionProvider.getVehicleStateCtrl()
        vehicleCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
        vehicleCtrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
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
        eqCtrl.onEquipmentCooldownInPercent += self.__onEquipmentCooldownInPercent
        optDevicesCtrl = g_sessionProvider.getOptDevicesCtrl()
        optDevicesCtrl.onOptionalDeviceAdded += self.__onOptionalDeviceAdded
        optDevicesCtrl.onOptionalDeviceUpdated += self.__onOptionalDeviceUpdated
        g_eventBus.addListener(GameEvent.CHOICE_CONSUMABLE, self.__handleConsumableChoice, scope=EVENT_BUS_SCOPE.BATTLE)

    def __removeListeners(self):
        g_eventBus.removeListener(GameEvent.CHOICE_CONSUMABLE, self.__handleConsumableChoice, scope=EVENT_BUS_SCOPE.BATTLE)
        vehicleCtrl = g_sessionProvider.getVehicleStateCtrl()
        vehicleCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
        vehicleCtrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        vehicleCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
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
        eqCtrl.onEquipmentCooldownInPercent -= self.__onEquipmentCooldownInPercent
        optDevicesCtrl = g_sessionProvider.getOptDevicesCtrl()
        optDevicesCtrl.onOptionalDeviceAdded -= self.__onOptionalDeviceAdded
        optDevicesCtrl.onOptionalDeviceUpdated -= self.__onOptionalDeviceUpdated

    def __genNextIdx(self, full, start):
        bits = self.__mask & full
        if not bits:
            idx = start
        else:
            idx = int(math.log(bits, 2)) + 1
        raise -1 < idx < PANEL_MAX_LENGTH - 1 or AssertionError
        self.__mask |= 1 << idx
        return idx

    def __genKey(self, idx):
        if not -1 < idx < PANEL_MAX_LENGTH - 1:
            raise AssertionError
            cmdMappingKey = COMMAND_AMMO_CHOICE_MASK.format(idx + 1 if idx < 9 else 0)
            bwKey = CommandMapping.g_instance.get(cmdMappingKey)
            sfKey = 0
            sfKey = bwKey is not None and bwKey != 0 and getScaleformKey(bwKey)
        return (bwKey, sfKey)

    def __makeShellTooltip(self, descriptor, piercingPower):
        kind = descriptor['kind']
        header = i18n.makeString('#ingame_gui:shells_kinds/{0:>s}'.format(kind), caliber=BigWorld.wg_getNiceNumberFormat(descriptor['caliber']), userString=descriptor['userString'])
        body = i18n.makeString('#ingame_gui:shells_kinds/params', damage=str(int(descriptor['damage'][0])), piercingPower=str(piercingPower))
        return TOOLTIP_FORMAT.format(header, body)

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

    def __handleConsumableChoice(self, event):
        self.__handleBWKey(event.ctx['key'])

    def __handleBWKey(self, bwKey):
        if bwKey in self.__keys:
            handler = self.__keys[bwKey]
            if handler and callable(handler):
                handler()

    def __handleAmmoPressed(self, intCD):
        g_sessionProvider.getAmmoCtrl().changeSetting(intCD)

    def __handleEquipmentPressed(self, intCD, entityName = None):
        result, error = g_sessionProvider.getEquipmentsCtrl().changeSetting(intCD, entityName=entityName, avatar=BigWorld.player())
        if not result and error:
            self.__ui.vErrorsPanel.showMessage(error.key, error.ctx)
        else:
            self.__flashObject.collapseEquipmentSlot()

    def __handleEquipmentExpanded(self, intCD):
        if not self.__flashObject.getVisibility():
            return
        result, error = g_sessionProvider.getEquipmentsCtrl().changeSetting(intCD)
        if not result and error:
            self.__ui.vErrorsPanel.showMessage(error.key, error.ctx)
            return
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
        ctrl = g_sessionProvider.getVehicleStateCtrl()
        ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated

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
        if item:
            if item.isAvatar():
                self.__addOrderSlot(intCD, item)
            else:
                self.__addEquipmentSlot(intCD, item)
        else:
            idx = self.__genNextIdx(EQUIPMENT_FULL_MASK + ORDERS_FULL_MASK, EQUIPMENT_START_IDX)
            self.__cds[idx] = intCD
            self.__flashObject.addEquipmentSlot(idx, None, None, None, 0, 0, None, EMPTY_EQUIPMENT_TOOLTIP)
            if self.__cds[EQUIPMENT_START_IDX:EQUIPMENT_END_IDX + 1] == EMPTY_EQUIPMENTS_SLICE:
                self.__flashObject.showEquipmentSlots(False)
            if self.__cds[ORDERS_START_IDX:ORDERS_END_IDX + 1] == EMPTY_ORDERS_SLICE:
                self.__flashObject.showOrdersSlots(False)
        return

    def __onEquipmentUpdated(self, intCD, item):
        if intCD in self.__cds:
            idx = self.__cds.index(intCD)
            quantity = item.getQuantity()
            currentTime = item.getTimeRemaining()
            maxTime = item.getTotalTime()
            if item.isAvatar():
                self.__flashObject.setItemTimeQuantityInSlot(self.__cds.index(intCD), quantity, currentTime, maxTime)
                self.__updateOrderSlot(idx, item)
            else:
                self.__flashObject.setItemTimeQuantityInSlot(idx, quantity, currentTime, maxTime)
                self.onPopUpClosed()
        else:
            LOG_ERROR('Equipment is not found in panel', intCD, self.__cds)

    def __onEquipmentCooldownInPercent(self, intCD, percent):
        if intCD in self.__cds:
            self.__flashObject.setCoolDownPosAsPercent(self.__cds.index(intCD), percent)

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
        self.__flashObject.addEquipmentSlot(idx, bwKey, sfKey, tag, item.getQuantity(), item.getTimeRemaining(), iconPath, toolTip)
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
        self.__flashObject.addOrderSlot(idx, bwKey, sfKey, item.getQuantity(), iconPath, toolTip, item.getStage() in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING), item.isQuantityUsed(), item.getTimeRemaining(), maxTime)
        self.__updateOrderSlot(idx, item)

    def __updateOrderSlot(self, idx, item):
        if item.getStage() == EQUIPMENT_STAGES.READY:
            self.__flashObject.setOrderAvailable(idx, True)
        elif item.getStage() == EQUIPMENT_STAGES.PREPARING:
            self.__currentOrderIdx = idx
            self.__flashObject.setOrderActivated(idx)
        else:
            self.__flashObject.setOrderAvailable(idx, False)
        if item.getStage() != EQUIPMENT_STAGES.PREPARING and self.__currentOrderIdx == idx:
            self.__currentOrderIdx = -1
            self.__flashObject.setOrderActivated(self.__currentOrderIdx)

    def __onOptionalDeviceAdded(self, intCD, descriptor, isOn):
        idx = self.__genNextIdx(OPT_DEVICE_FULL_MASK, OPT_DEVICE_START_IDX)
        self.__cds[idx] = intCD
        iconPath = descriptor.icon[0]
        toolTip = TOOLTIP_FORMAT.format(descriptor.userString, descriptor.description)
        self.__flashObject.addOptionalDeviceSlot(idx, -1 if isOn else 0, iconPath, toolTip)

    def __onOptionalDeviceUpdated(self, intCD, isOn):
        if intCD in self.__cds:
            self.__flashObject.setCoolDownTime(self.__cds.index(intCD), -1 if isOn else 0)
        else:
            LOG_ERROR('Optional device is not found in panel', intCD, self.__cds)

    def __onPostMortemSwitched(self):
        self.__flashObject.switchToPosmortem()

    def __onRespawnBaseMoving(self):
        self.__cds = [None] * PANEL_MAX_LENGTH
        self.__mask = 0
        self.__keys.clear()
        self.__currentOrderIdx = -1
        self.__flashObject.reset()
        self.__plugins.reset()
        return

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


class _RageBarPlugin(IPlugin):

    def __init__(self, parentObj):
        super(_RageBarPlugin, self).__init__(parentObj)
        self.__currentValue = 0

    def init(self):
        super(_RageBarPlugin, self).init()
        avatarStatsCtrl = g_sessionProvider.getAvatarStatsCtrl()
        avatarStatsCtrl.onUpdated += self.__onAvatarStatsUpdated

    def fini(self):
        avatarStatsCtrl = g_sessionProvider.getAvatarStatsCtrl()
        avatarStatsCtrl.onUpdated -= self.__onAvatarStatsUpdated
        super(_RageBarPlugin, self).fini()

    def start(self):
        super(_RageBarPlugin, self).start()
        avatarStatsCtrl = g_sessionProvider.getAvatarStatsCtrl()
        self.__currentValue = avatarStatsCtrl.getStats().get('ragePoints', 0)
        rageProps = _RageBarViewProps(maxValue=rage.g_cache.pointsLimit, curValue=self.__currentValue)
        self._parentObj.flashObject.initializeRageProgress(isEventBattle(), rageProps._asdict())

    def reset(self):
        super(_RageBarPlugin, self).reset()
        self._parentObj.flashObject.updateProgressBarValue(self.__currentValue)

    def __onAvatarStatsUpdated(self, stats):
        newValue = stats.get('ragePoints', 0)
        if newValue == self.__currentValue:
            return
        delta = newValue - self.__currentValue
        if delta < 0:
            self._parentObj.flashObject.updateProgressBarValue(newValue)
        else:
            self._parentObj.flashObject.updateProgressBarValueByDelta(delta)
        self.__currentValue = newValue
