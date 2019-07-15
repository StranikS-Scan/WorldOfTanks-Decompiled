# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/consumables_panel.py
import math
from functools import partial
from types import NoneType
import BigWorld
import CommandMapping
from constants import EQUIPMENT_STAGES
from debug_utils import LOG_ERROR
from gui import GUI_SETTINGS
from gui import TANKMEN_ROLES_ORDER_DICT
from gui.Scaleform.daapi.view.battle.shared.timers_common import PythonTimer
from gui.Scaleform.daapi.view.meta.ConsumablesPanelMeta import ConsumablesPanelMeta
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.battle_control.battle_constants import VEHICLE_DEVICE_IN_COMPLEX_ITEM
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, DEVICE_STATE_DESTROYED
from gui.battle_control.controllers.consumables.equipment_ctrl import IgnoreEntitySelection
from gui.battle_control.controllers.consumables.equipment_ctrl import NeedEntitySelection, InCooldownError
from gui.impl import backport
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.utils.key_mapping import getScaleformKey
from helpers import dependency
from helpers import i18n
from shared_utils import forEach
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
AMMO_ICON_PATH = '../maps/icons/ammopanel/battle_ammo/%s'
NO_AMMO_ICON_PATH = '../maps/icons/ammopanel/battle_ammo/NO_%s'
COMMAND_AMMO_CHOICE_MASK = 'CMD_AMMO_CHOICE_{0:d}'
PANEL_MAX_LENGTH = 12
AMMO_START_IDX = 0
AMMO_END_IDX = 2
AMMO_RANGE = xrange(AMMO_START_IDX, AMMO_END_IDX + 1)
AMMO_FULL_MASK = sum([ 1 << _idx for _idx in AMMO_RANGE ])
EQUIPMENT_START_IDX = 3
EQUIPMENT_END_IDX = 5
EQUIPMENT_RANGE = xrange(EQUIPMENT_START_IDX, EQUIPMENT_END_IDX + 1)
EQUIPMENT_FULL_MASK = sum([ 1 << _idx for _idx in EQUIPMENT_RANGE ])
ORDERS_START_IDX = 6
ORDERS_END_IDX = 8
ORDERS_RANGE = xrange(ORDERS_START_IDX, ORDERS_END_IDX + 1)
ORDERS_FULL_MASK = sum([ 1 << _idx for _idx in ORDERS_RANGE ])
OPT_DEVICE_START_IDX = 9
OPT_DEVICE_END_IDX = 11
OPT_DEVICE_RANGE = xrange(OPT_DEVICE_START_IDX, OPT_DEVICE_END_IDX + 1)
OPT_DEVICE_FULL_MASK = sum([ 1 << _idx for _idx in OPT_DEVICE_RANGE ])
EQUIPMENT_ICON_PATH = '../maps/icons/artefact/%s.png'
EMPTY_EQUIPMENTS_SLICE = [0] * (EQUIPMENT_END_IDX - EQUIPMENT_START_IDX + 1)
EMPTY_ORDERS_SLICE = [0] * (ORDERS_START_IDX - ORDERS_END_IDX + 1)
EMPTY_EQUIPMENT_TOOLTIP = i18n.makeString('#ingame_gui:consumables_panel/equipment/tooltip/empty')
TOOLTIP_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}\n/{{BODY}}{1:>s}{{/BODY}}'
TOOLTIP_NO_BODY_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}'
_EQUIPMENT_GLOW_TIME = 7

def _isEquipmentAvailableToUse(eq):
    return eq.isAvailableToUse


class _PythonReloadTicker(PythonTimer):

    def __init__(self, viewObject):
        super(_PythonReloadTicker, self).__init__(viewObject, 0, 0, 0, 0, interval=0.1)
        self.__index = 0

    def _hideView(self):
        pass

    def _showView(self, isBubble):
        pass

    def startAnimation(self, index, actualTime, baseTime):
        self.__index = index
        self._stopTick()
        if actualTime > 0:
            self._totalTime = baseTime
            self._finishTime = BigWorld.serverTime() + actualTime
            self.show()

    def _setViewSnapshot(self, timeLeft):
        if self._totalTime > 0:
            timeGone = self._totalTime - timeLeft
            progressInPercents = float(timeGone) / self._totalTime * 100
            self._viewObject.as_setCoolDownPosAsPercentS(self.__index, progressInPercents)

    def _stopTick(self):
        super(_PythonReloadTicker, self)._stopTick()
        self._viewObject.as_setCoolDownPosAsPercentS(self.__index, 100.0)


class ConsumablesPanel(ConsumablesPanelMeta, BattleGUIKeyHandler):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(ConsumablesPanel, self).__init__()
        self.__cds = [None] * PANEL_MAX_LENGTH
        self.__mask = 0
        self.__keys = {}
        self.__currentActivatedSlotIdx = -1
        self.__equipmentsGlowCallbacks = {}
        if self.sessionProvider.isReplayPlaying:
            self.__reloadTicker = _PythonReloadTicker(self)
        else:
            self.__reloadTicker = None
        return

    def onClickedToSlot(self, bwKey):
        self.__handleBWKey(int(bwKey))

    def onPopUpClosed(self):
        keys = {}
        for _, bwKey, _, handler in self.__getKeysGenerator():
            if handler:
                keys[bwKey] = handler

        self.__keys.clear()
        self.__keys = keys

    def handleEscKey(self, isDown):
        if isDown:
            self.__collapseEquipmentSlot()
            return True
        return False

    def _populate(self):
        super(ConsumablesPanel, self)._populate()
        if self.sessionProvider.isReplayPlaying:
            self.as_handleAsReplayS()
        self.__addListeners()
        self.as_setPanelSettingsS(self._getPanelSettings())

    def _dispose(self):
        self.__clearAllEquipmentGlow()
        self.__removeListeners()
        self.__keys.clear()
        super(ConsumablesPanel, self)._dispose()

    def _getPanelSettings(self):
        return CONSUMABLES_PANEL_SETTINGS.DEFAULT_SETTINGS_ID

    def _addShellSlot(self, idx, keyCode, sfKeyCode, quantity, clipCapacity, shellIconPath, noShellIconPath, tooltipText):
        self.as_addShellSlotS(idx, keyCode, sfKeyCode, quantity, clipCapacity, shellIconPath, noShellIconPath, tooltipText)

    def _showEquipmentGlow(self, equipmentIndex, glowType=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_ORANGE):
        if equipmentIndex in self.__equipmentsGlowCallbacks:
            BigWorld.cancelCallback(self.__equipmentsGlowCallbacks[equipmentIndex])
            del self.__equipmentsGlowCallbacks[equipmentIndex]
        else:
            self.as_setGlowS(equipmentIndex, glowID=glowType)
        self.__equipmentsGlowCallbacks[equipmentIndex] = BigWorld.callback(_EQUIPMENT_GLOW_TIME, partial(self.__hideEquipmentGlowCallback, equipmentIndex))

    def __addListeners(self):
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
            vehicleCtrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
            vehicleCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            self.__fillShells(ammoCtrl)
            ammoCtrl.onShellsAdded += self.__onShellsAdded
            ammoCtrl.onShellsUpdated += self.__onShellsUpdated
            ammoCtrl.onNextShellChanged += self.__onNextShellChanged
            ammoCtrl.onCurrentShellChanged += self.__onCurrentShellChanged
            ammoCtrl.onGunReloadTimeSet += self.__onGunReloadTimeSet
            ammoCtrl.onGunSettingsSet += self.__onGunSettingsSet
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            self.__fillEquipments(eqCtrl)
            eqCtrl.onEquipmentAdded += self.__onEquipmentAdded
            eqCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
            eqCtrl.onEquipmentCooldownInPercent += self.__onEquipmentCooldownInPercent
            eqCtrl.onEquipmentCooldownTime += self.__onEquipmentCooldownTime
        optDevicesCtrl = self.sessionProvider.shared.optionalDevices
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
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            vehicleCtrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
            vehicleCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellsAdded -= self.__onShellsAdded
            ammoCtrl.onShellsUpdated -= self.__onShellsUpdated
            ammoCtrl.onNextShellChanged -= self.__onNextShellChanged
            ammoCtrl.onCurrentShellChanged -= self.__onCurrentShellChanged
            ammoCtrl.onGunReloadTimeSet -= self.__onGunReloadTimeSet
            ammoCtrl.onGunSettingsSet -= self.__onGunSettingsSet
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentAdded -= self.__onEquipmentAdded
            eqCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
            eqCtrl.onEquipmentCooldownInPercent -= self.__onEquipmentCooldownInPercent
            eqCtrl.onEquipmentCooldownTime -= self.__onEquipmentCooldownTime
        optDevicesCtrl = self.sessionProvider.shared.optionalDevices
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
        self.__mask |= 1 << idx
        return idx

    def __genKey(self, idx):
        cmdMappingKey = COMMAND_AMMO_CHOICE_MASK.format(idx + 1 if idx < 9 else 0)
        bwKey = CommandMapping.g_instance.get(cmdMappingKey)
        sfKey = 0
        if bwKey is not None:
            sfKey = getScaleformKey(bwKey)
        return (bwKey, sfKey)

    def __makeShellTooltip(self, descriptor, piercingPower):
        kind = descriptor.kind
        header = i18n.makeString('#ingame_gui:shells_kinds/{0:>s}'.format(kind), caliber=backport.getNiceNumberFormat(descriptor.caliber), userString=descriptor.userString)
        if GUI_SETTINGS.technicalInfo:
            tooltipStr = INGAME_GUI.SHELLS_KINDS_PARAMS
            paramsDict = {'damage': str(int(descriptor.damage[0])),
             'piercingPower': str(piercingPower)}
            if descriptor.hasStun and self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
                stun = descriptor.stun
                tooltipStr = INGAME_GUI.SHELLS_KINDS_STUNPARAMS
                paramsDict['stunMinDuration'] = backport.getNiceNumberFormat(stun.guaranteedStunDuration * stun.stunDuration)
                paramsDict['stunMaxDuration'] = backport.getNiceNumberFormat(stun.stunDuration)
            body = i18n.makeString(tooltipStr, **paramsDict)
            fmt = TOOLTIP_FORMAT
        else:
            body = ''
            fmt = TOOLTIP_NO_BODY_FORMAT
        return fmt.format(header, body)

    def __getKeysGenerator(self):
        hasEquipment = self.sessionProvider.shared.equipments.hasEquipment
        getEquipment = self.sessionProvider.shared.equipments.getEquipment
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
            elif (idx in EQUIPMENT_RANGE or idx in ORDERS_RANGE) and hasEquipment(intCD):
                item = getEquipment(intCD)
                if item is not None and item.getTag() and item.getQuantity() > 0:
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
        ctrl = self.sessionProvider.shared.ammo
        if ctrl is not None:
            ctrl.changeSetting(intCD)
        return

    def __handleEquipmentPressed(self, intCD, entityName=None):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is None:
            return
        else:
            result, error = ctrl.changeSetting(intCD, entityName=entityName, avatar=BigWorld.player())
            if not result and error:
                ctrl = self.sessionProvider.shared.messages
                if ctrl is not None:
                    ctrl.showVehicleError(error.key, error.ctx)
            else:
                self.__collapseEquipmentSlot()
            return

    def __handleEquipmentExpanded(self, intCD):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is None:
            return
        else:
            result, error = ctrl.changeSetting(intCD)
            item = ctrl.getEquipment(intCD)
            errorType = type(error)
            if errorType == IgnoreEntitySelection:
                return
            if not result and errorType not in (NoneType, NeedEntitySelection):
                ctrl = self.sessionProvider.shared.messages
                if ctrl is not None:
                    ctrl.showVehicleError(error.key, error.ctx)
                return
            if errorType == InCooldownError:
                return
            if intCD not in self.__cds:
                LOG_ERROR('Equipment is not found in panel', intCD, self.__cds)
                return
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
            return

    def __onShellsAdded(self, intCD, descriptor, quantity, _, gunSettings):
        toolTip = self.__makeShellTooltip(descriptor, int(gunSettings.getPiercingPower(intCD)))
        icon = descriptor.icon[0]
        shellIconPath = AMMO_ICON_PATH % icon
        noShellIconPath = NO_AMMO_ICON_PATH % icon
        idx = self.__genNextIdx(AMMO_FULL_MASK, AMMO_START_IDX)
        self.__cds[idx] = intCD
        bwKey, sfKey = self.__genKey(idx)
        self.__keys[bwKey] = partial(self.__handleAmmoPressed, intCD)
        self._addShellSlot(idx, bwKey, sfKey, quantity, gunSettings.clip.size, shellIconPath, noShellIconPath, toolTip)

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
            if self.__reloadTicker:
                self.__reloadTicker.startAnimation(index, state.getActualValue(), state.getBaseValue())
            else:
                self.as_setCoolDownTimeS(index, state.getActualValue(), state.getBaseValue(), state.getTimePassed(), not state.isReloadingFinished())
        else:
            LOG_ERROR('Ammo is not found in panel', currShellCD, self.__cds)

    def __onGunSettingsSet(self, _):
        self.__reset()

    def __onEquipmentAdded(self, intCD, item):
        if item:
            if item.isAvatar():
                idx = self.__genNextIdx(ORDERS_FULL_MASK, ORDERS_START_IDX)
            else:
                idx = self.__genNextIdx(EQUIPMENT_FULL_MASK, EQUIPMENT_START_IDX)
            self.__addEquipmentSlot(intCD, idx, item)
        else:
            idx = self.__genNextIdx(EQUIPMENT_FULL_MASK + ORDERS_FULL_MASK, EQUIPMENT_START_IDX)
            self.__cds[idx] = intCD
            bwKey, sfKey = self.__genKey(idx)
            self.as_addEquipmentSlotS(idx, bwKey, sfKey, None, 0, 0, 0, None, EMPTY_EQUIPMENT_TOOLTIP)
            snap = self.__cds[EQUIPMENT_START_IDX:EQUIPMENT_END_IDX + 1]
            if snap == EMPTY_EQUIPMENTS_SLICE:
                self.as_showEquipmentSlotsS(False)
        return

    def __onEquipmentUpdated(self, intCD, item):
        if intCD in self.__cds:
            idx = self.__cds.index(intCD)
            quantity = item.getQuantity()
            currentTime = item.getTimeRemaining()
            maxTime = item.getTotalTime()
            self.as_setItemTimeQuantityInSlotS(idx, quantity, currentTime, maxTime)
            if item.isReusable or item.isAvatar() and item.getStage() != EQUIPMENT_STAGES.PREPARING:
                glowType = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL if item.isAvatar() else CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN
                if self.__canApplyingGlowEquipment(item):
                    self._showEquipmentGlow(idx)
                elif item.becomeReady:
                    self.as_setGlowS(idx, glowID=glowType)
                elif idx in self.__equipmentsGlowCallbacks:
                    self.__clearEquipmentGlow(idx)
            if item.getStage() == EQUIPMENT_STAGES.PREPARING:
                self.__currentActivatedSlotIdx = idx
                self.as_setEquipmentActivatedS(idx)
            elif item.getStage() != EQUIPMENT_STAGES.PREPARING and self.__currentActivatedSlotIdx == idx:
                self.__currentActivatedSlotIdx = -1
                self.as_setEquipmentActivatedS(-1)
        else:
            LOG_ERROR('Equipment is not found in panel', intCD, self.__cds)

    def __onEquipmentCooldownInPercent(self, intCD, percent):
        if intCD in self.__cds:
            self.as_setCoolDownPosAsPercentS(self.__cds.index(intCD), percent)

    def _getEquipmentIconPath(self):
        return EQUIPMENT_ICON_PATH

    def __onEquipmentCooldownTime(self, intCD, timeLeft, isBaseTime, isFlash):
        if intCD in self.__cds:
            self.as_setCoolDownTimeSnapshotS(self.__cds.index(intCD), timeLeft, isBaseTime, isFlash)

    def __addEquipmentSlot(self, intCD, idx, item):
        self.__cds[idx] = intCD
        descriptor = item.getDescriptor()
        iconPath = self._getEquipmentIconPath() % descriptor.icon[0]
        body = descriptor.description
        if item.getTotalTime() > 0:
            tooltipStr = INGAME_GUI.CONSUMABLES_PANEL_EQUIPMENT_COOLDOWNSECONDS
            cooldownSeconds = str(int(descriptor.cooldownSeconds))
            paramsString = i18n.makeString(tooltipStr, cooldownSeconds=cooldownSeconds)
            body = body + '\n\n' + paramsString
        toolTip = TOOLTIP_FORMAT.format(descriptor.userString, body)
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
        self.as_addEquipmentSlotS(idx, bwKey, sfKey, tag, item.getQuantity(), item.getTimeRemaining(), item.getTotalTime(), iconPath, toolTip)
        return None

    def __onOptionalDeviceAdded(self, intCD, descriptor, isOn):
        idx = self.__genNextIdx(OPT_DEVICE_FULL_MASK, OPT_DEVICE_START_IDX)
        self.__cds[idx] = intCD
        iconPath = descriptor.icon[0]
        toolTip = TOOLTIP_FORMAT.format(descriptor.userString, descriptor.description.format(colorTagOpen='', colorTagClose=''))
        self.as_addOptionalDeviceSlotS(idx, -1 if isOn else 0, iconPath, toolTip)

    def __onOptionalDeviceUpdated(self, intCD, isOn):
        if intCD in self.__cds:
            duration = -1 if isOn else 0
            self.as_setCoolDownTimeS(self.__cds.index(intCD), duration, duration, 0, False)
        else:
            LOG_ERROR('Optional device is not found in panel', intCD, self.__cds)

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.__reset()
        if noRespawnPossible:
            if not BigWorld.player().isObserver():
                self.__removeListeners()
            self.as_switchToPosmortemS()

    def __onRespawnBaseMoving(self):
        self.__reset()

    def __reset(self):
        self.__cds = [None] * PANEL_MAX_LENGTH
        self.__mask = 0
        self.__keys.clear()
        self.__currentActivatedSlotIdx = -1
        self.as_resetS()
        return

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.SWITCHING:
            self.__reset()
            return
        elif state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__clearAllEquipmentGlow()
            return
        elif self.__cds.count(None) == PANEL_MAX_LENGTH:
            return
        else:
            ctrl = self.sessionProvider.shared.equipments
            if ctrl is None:
                return
            if state == VEHICLE_VIEW_STATE.DEVICES:
                deviceName, deviceState, actualState = value
                if deviceName in VEHICLE_DEVICE_IN_COMPLEX_ITEM:
                    itemName = VEHICLE_DEVICE_IN_COMPLEX_ITEM[deviceName]
                else:
                    itemName = deviceName
                equipmentTag = 'medkit' if itemName in TANKMEN_ROLES_ORDER_DICT['enum'] else 'repairkit'
                if deviceState == actualState and deviceState == DEVICE_STATE_DESTROYED:
                    for intCD, _ in ctrl.iterEquipmentsByTag(equipmentTag, _isEquipmentAvailableToUse):
                        self._showEquipmentGlow(self.__cds.index(intCD))

                elif deviceState != DEVICE_STATE_DESTROYED:
                    for intCD, equipment in ctrl.iterEquipmentsByTag(equipmentTag):
                        if not self.__canApplyingGlowEquipment(equipment):
                            self.__clearEquipmentGlow(self.__cds.index(intCD))

                idx = int(self.as_updateEntityStateS(itemName, actualState))
                if idx > 0 and idx < len(self.__cds):
                    intCD = self.__cds[idx]
                    if not ctrl.hasEquipment(intCD):
                        return
                    item = ctrl.getEquipment(intCD)
                    if item and item.isEntityRequired():
                        bwKey, _ = self.__genKey(idx)
                        self.__keys[bwKey] = partial(self.__handleEquipmentPressed, self.__cds[idx], deviceName)
            elif state == VEHICLE_VIEW_STATE.STUN:
                if value.duration > 0:
                    for intCD, _ in ctrl.iterEquipmentsByTag('medkit', _isEquipmentAvailableToUse):
                        self._showEquipmentGlow(self.__cds.index(intCD))

                else:
                    for intCD, equipment in ctrl.iterEquipmentsByTag('medkit'):
                        if not self.__canApplyingGlowEquipment(equipment):
                            self.__clearEquipmentGlow(self.__cds.index(intCD))

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
                            self._showEquipmentGlow(self.__cds.index(cID))

                else:
                    for intCD, equipment in ctrl.iterEquipmentsByTag('extinguisher'):
                        if not equipment.getDescriptor().autoactivate:
                            self.__clearEquipmentGlow(self.__cds.index(intCD))

            return

    def __canApplyingGlowEquipment(self, equipment):
        if equipment.getTag() == 'extinguisher':
            correction = True
            entityName = None
        elif equipment.isAvatar():
            correction = False
            entityName = None
        else:
            entityNames = [ name for name, state in equipment.getEntitiesIterator() if state == DEVICE_STATE_DESTROYED ]
            correction = hasDestroyed = len(entityNames)
            entityName = entityNames[0] if hasDestroyed else None
        canActivate, info = equipment.canActivate(entityName)
        infoType = type(info)
        return correction and (canActivate or infoType == NeedEntitySelection) or infoType == IgnoreEntitySelection

    def __hideEquipmentGlowCallback(self, equipmentIndex):
        return self.__clearEquipmentGlow(equipmentIndex, cancelCallback=False)

    def __clearEquipmentGlow(self, equipmentIndex, cancelCallback=True):
        if equipmentIndex in self.__equipmentsGlowCallbacks:
            self.as_hideGlowS(equipmentIndex)
            if cancelCallback:
                BigWorld.cancelCallback(self.__equipmentsGlowCallbacks[equipmentIndex])
            del self.__equipmentsGlowCallbacks[equipmentIndex]

    def __clearAllEquipmentGlow(self):
        for equipmentIndex, callbackID in self.__equipmentsGlowCallbacks.items():
            BigWorld.cancelCallback(callbackID)
            self.as_hideGlowS(equipmentIndex)
            del self.__equipmentsGlowCallbacks[equipmentIndex]

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
