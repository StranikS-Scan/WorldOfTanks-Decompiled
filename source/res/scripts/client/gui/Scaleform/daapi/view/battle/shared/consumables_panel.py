# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/consumables_panel.py
import logging
import math
from functools import partial
from types import NoneType
import BigWorld
import CommandMapping
from constants import EQUIPMENT_STAGES, SHELL_TYPES
from items import vehicles
from gui import GUI_SETTINGS
from gui import TANKMEN_ROLES_ORDER_DICT
from gui.Scaleform.daapi.view.battle.shared.timers_common import PythonTimer
from gui.Scaleform.daapi.view.meta.ConsumablesPanelMeta import ConsumablesPanelMeta
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.battle_control.battle_constants import VEHICLE_DEVICE_IN_COMPLEX_ITEM, CROSSHAIR_VIEW_ID
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, DEVICE_STATE_DESTROYED
from gui.battle_control.controllers.consumables.equipment_ctrl import IgnoreEntitySelection
from gui.battle_control.controllers.consumables.equipment_ctrl import NeedEntitySelection, InCooldownError
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.formatters import text_styles
from gui.shared.utils.key_mapping import getScaleformKey
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from items.artefacts import SharedCooldownConsumableConfigReader
from shared_utils import forEach
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)
AMMO_ICON_PATH = '../maps/icons/ammopanel/battle_ammo/%s'
NO_AMMO_ICON_PATH = '../maps/icons/ammopanel/battle_ammo/NO_%s'
COMMAND_AMMO_CHOICE_MASK = 'CMD_AMMO_CHOICE_{0:d}'
TOOLTIP_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}\n/{{BODY}}{1:>s}{{/BODY}}'
TOOLTIP_NO_BODY_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}'
EMPTY_EQUIPMENT_TOOLTIP = backport.text(R.strings.ingame_gui.consumables_panel.equipment.tooltip.empty())
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


class ConsumablesPanel(ConsumablesPanelMeta, BattleGUIKeyHandler, CallbackDelayer):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _PANEL_MAX_LENGTH = 12
    _AMMO_START_IDX = 0
    _AMMO_END_IDX = 2
    _EQUIPMENT_START_IDX = 3
    _EQUIPMENT_END_IDX = 5
    _ORDERS_START_IDX = 6
    _ORDERS_END_IDX = 8
    _OPT_DEVICE_START_IDX = 9
    _OPT_DEVICE_END_IDX = 11
    _EQUIPMENT_ICON_PATH = '../maps/icons/artefact/%s.png'

    def __init__(self):
        super(ConsumablesPanel, self).__init__()
        self.__ammoRange = xrange(self._AMMO_START_IDX, self._AMMO_END_IDX + 1)
        self.__ammoFullMask = sum([ 1 << idx for idx in self.__ammoRange ])
        self.__equipmentRange = xrange(self._EQUIPMENT_START_IDX, self._EQUIPMENT_END_IDX + 1)
        self.__equipmentFullMask = sum([ 1 << idx for idx in self.__equipmentRange ])
        self.__ordersRange = xrange(self._ORDERS_START_IDX, self._ORDERS_END_IDX + 1)
        self.__ordersFullMask = sum([ 1 << idx for idx in self.__ordersRange ])
        self.__optDeviceRange = xrange(self._OPT_DEVICE_START_IDX, self._OPT_DEVICE_END_IDX + 1)
        self.__optDeviceFullMask = sum([ 1 << idx for idx in self.__optDeviceRange ])
        self.__emptyEquipmentsSlice = [0] * (self._EQUIPMENT_END_IDX - self._EQUIPMENT_START_IDX + 1)
        self._cds = [None] * self._PANEL_MAX_LENGTH
        self._mask = 0
        self.__keys = {}
        self.__extraKeys = {}
        self.__currentActivatedSlotIdx = -1
        self.__equipmentsGlowCallbacks = {}
        if self.sessionProvider.isReplayPlaying:
            self.__reloadTicker = _PythonReloadTicker(self)
        else:
            self.__reloadTicker = None
        self.delayedReload = None
        self.__delayedNextShellID = None
        return

    def onClickedToSlot(self, bwKey, idx):
        self.__handleBWKey(int(bwKey), idx)

    def onPopUpClosed(self):
        keys = {}
        extraKeys = {}
        for idx, bwKey, _, handler in self.__getKeysGenerator():
            if handler:
                extraKeys[idx] = keys[bwKey] = handler

        self.__keys.clear()
        self.__keys = keys
        self.__extraKeys.clear()
        self.__extraKeys = extraKeys

    def handleEscKey(self, isDown):
        if isDown:
            self.__collapseEquipmentSlot()
            return True
        return False

    def _populate(self):
        self.as_setPanelSettingsS(self._getPanelSettings())
        super(ConsumablesPanel, self)._populate()
        if self.sessionProvider.isReplayPlaying:
            self.as_handleAsReplayS()
        self.__addListeners()

    def _dispose(self):
        self.__clearAllEquipmentGlow()
        self.__removeListeners()
        self.__keys.clear()
        self.__extraKeys.clear()
        super(ConsumablesPanel, self)._dispose()

    def _getPanelSettings(self):
        return CONSUMABLES_PANEL_SETTINGS.DEFAULT_SETTINGS_ID

    def _resetCds(self):
        self._cds = [None] * self._PANEL_MAX_LENGTH
        return

    def _resetDelayedReload(self):
        self.delayedReload = None
        self.__delayedNextShellID = None
        return

    def _reset(self):
        self._resetCds()
        self._mask = 0
        self.__keys.clear()
        self.__extraKeys.clear()
        self.__currentActivatedSlotIdx = -1
        self._resetDelayedReload()
        self.as_resetS()

    def _addShellSlot(self, idx, intCD, descriptor, quantity, gunSettings):
        self._cds[idx] = intCD
        keyCode, sfKeyCode = self.__genKey(idx)
        self.__extraKeys[idx] = self.__keys[keyCode] = partial(self.__handleAmmoPressed, intCD)
        tooltipText = self.__makeShellTooltip(descriptor, int(gunSettings.getPiercingPower(intCD)), gunSettings.getShotSpeed(intCD))
        icon = descriptor.icon[0]
        shellIconPath = AMMO_ICON_PATH % icon
        noShellIconPath = NO_AMMO_ICON_PATH % icon
        self.as_addShellSlotS(idx, keyCode, sfKeyCode, quantity, gunSettings.clip.size, shellIconPath, noShellIconPath, tooltipText)

    def _addEquipmentSlot(self, idx, intCD, item):
        self._cds[idx] = intCD
        if item is None:
            bwKey, sfKey = self.__genKey(idx)
            self.as_addEquipmentSlotS(idx, bwKey, sfKey, 0, 0, 0, None, EMPTY_EQUIPMENT_TOOLTIP, ANIMATION_TYPES.NONE)
            snap = self._cds[self._EQUIPMENT_START_IDX:self._EQUIPMENT_END_IDX + 1]
            if snap == self.__emptyEquipmentsSlice:
                self.as_showEquipmentSlotsS(False)
        else:
            tags = item.getTags()
            if tags:
                bwKey, sfKey = self.__genKey(idx)
                if item.isEntityRequired():
                    handler = partial(self.__handleEquipmentExpanded, intCD)
                else:
                    handler = partial(self.__handleEquipmentPressed, intCD)
                if item.getQuantity() > 0:
                    self.__extraKeys[idx] = self.__keys[bwKey] = handler
            else:
                bwKey, sfKey = (None, None)
            descriptor = item.getDescriptor()
            quantity = item.getQuantity()
            timeRemaining = item.getTimeRemaining()
            reloadingTime = item.getTotalTime()
            iconPath = self._getEquipmentIconPath() % descriptor.icon[0]
            animationType = item.getAnimationType()
            body = descriptor.description
            if reloadingTime > 0:
                tooltipStr = R.strings.ingame_gui.consumables_panel.equipment.cooldownSeconds()
                if isinstance(descriptor, SharedCooldownConsumableConfigReader):
                    cdSecVal = descriptor.cooldownTime
                else:
                    cdSecVal = descriptor.cooldownSeconds
                cooldownSeconds = str(int(cdSecVal))
                paramsString = backport.text(tooltipStr, cooldownSeconds=cooldownSeconds)
                body = '\n\n'.join((body, paramsString))
            toolTip = TOOLTIP_FORMAT.format(descriptor.userString, body)
            self.as_addEquipmentSlotS(idx, bwKey, sfKey, quantity, timeRemaining, reloadingTime, iconPath, toolTip, animationType)
        return

    def _addOptionalDeviceSlot(self, idx, optDeviceInBattle):
        self._cds[idx] = optDeviceInBattle.getIntCD()
        descriptor = optDeviceInBattle.getDescriptor()
        iconPath = descriptor.icon[0]
        self.as_addOptionalDeviceSlotS(idx, -1 if optDeviceInBattle.getStatus() else 0, iconPath, TOOLTIPS_CONSTANTS.BATTLE_OPT_DEVICE, True, optDeviceInBattle.getIntCD(), optDeviceInBattle.isUsed())

    def _updateShellSlot(self, idx, quantity):
        self.as_setItemQuantityInSlotS(idx, quantity)

    def _updateEquipmentSlot(self, idx, item):
        quantity = item.getQuantity()
        currentTime = item.getTimeRemaining()
        maxTime = item.getTotalTime()
        self.as_setItemTimeQuantityInSlotS(idx, quantity, currentTime, maxTime, item.getAnimationType())
        bwKey, _ = self.__genKey(idx)
        if item.getQuantity() > 0 and bwKey not in self.__keys:
            if item.isEntityRequired():
                handler = partial(self.__handleEquipmentExpanded, self._cds[idx])
            else:
                handler = partial(self.__handleEquipmentPressed, self._cds[idx])
            self.__keys[bwKey] = handler
        if item.isReusable or item.isAvatar() and item.getStage() != EQUIPMENT_STAGES.PREPARING:
            glowType = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL if item.isAvatar() else CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN
            if self.__canApplyingGlowEquipment(item):
                self._showEquipmentGlow(idx)
            elif item.becomeReady:
                self._showEquipmentGlow(idx, glowType)
            elif idx in self.__equipmentsGlowCallbacks:
                self.__clearEquipmentGlow(idx)
        if item.getStage() == EQUIPMENT_STAGES.PREPARING:
            self.__currentActivatedSlotIdx = idx
            self.as_setEquipmentActivatedS(idx, True)
        elif item.getStage() != EQUIPMENT_STAGES.PREPARING and self.__currentActivatedSlotIdx == idx:
            self.__currentActivatedSlotIdx = -1
            self.as_setEquipmentActivatedS(idx, False)

    def _updateOptionalDeviceSlot(self, idx, optDeviceInBattle):
        intCD = optDeviceInBattle.getIntCD()
        duration = -1 if optDeviceInBattle.getStatus() else 0
        idx = self._cds.index(intCD)
        self.as_setOptionalDeviceUsedS(idx, optDeviceInBattle.isUsed())
        if optDeviceInBattle.isNeedGlow():
            self.as_setGlowS(idx, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN)
        self.as_setCoolDownTimeS(self._cds.index(intCD), duration, duration, 0)

    def _showEquipmentGlow(self, equipmentIndex, glowType=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_ORANGE):
        if BigWorld.player().isObserver():
            return
        if equipmentIndex in self.__equipmentsGlowCallbacks:
            BigWorld.cancelCallback(self.__equipmentsGlowCallbacks[equipmentIndex])
            del self.__equipmentsGlowCallbacks[equipmentIndex]
        else:
            self.as_setGlowS(equipmentIndex, glowID=glowType)
        self.__equipmentsGlowCallbacks[equipmentIndex] = BigWorld.callback(_EQUIPMENT_GLOW_TIME, partial(self.__hideEquipmentGlowCallback, equipmentIndex))

    def _onShellsAdded(self, intCD, descriptor, quantity, _, gunSettings):
        idx = self.__genNextIdx(self.__ammoFullMask, self._AMMO_START_IDX)
        self._addShellSlot(idx, intCD, descriptor, quantity, gunSettings)

    def _onShellsUpdated(self, intCD, quantity, *args):
        if intCD in self._cds:
            self._updateShellSlot(self._cds.index(intCD), quantity)
        else:
            _logger.error('Ammo with cd=%d is not found in panel=%s', intCD, str(self._cds))

    def _onNextShellChanged(self, intCD):
        if intCD in self._cds:
            self.__delayedNextShellID = intCD
            self.as_setNextShellS(self._cds.index(intCD))
        else:
            _logger.error('Ammo with cd=%d is not found in panel=%s', intCD, str(self._cds))

    def _onCurrentShellChanged(self, intCD):
        if intCD in self._cds:
            self.as_setCurrentShellS(self._cds.index(intCD))
        else:
            _logger.error('Ammo with cd=%d is not found in panel=%s', intCD, str(self._cds))

    def _onGunSettingsSet(self, _):
        self._reset()

    def _onGunReloadTimeSet(self, currShellCD, state):
        if currShellCD not in self._cds:
            _logger.error('Ammo with cd=%d is not found in panel %s', currShellCD, str(self._cds))
            return
        shellIndex = self._cds.index(currShellCD)
        if self.delayedReload > 0:
            self.delayCallback(self.delayedReload, self.__startReloadDelayed, shellIndex, state)
            self.as_setCoolDownPosAsPercentS(shellIndex, 0)
        else:
            self.__startReload(shellIndex, state)

    def _onEquipmentAdded(self, intCD, item):
        if item is None:
            idx = self.__genNextIdx(self.__equipmentFullMask + self.__ordersFullMask, self._EQUIPMENT_START_IDX)
        elif self._isAvatarEquipment(item):
            idx = self.__genNextIdx(self.__ordersFullMask, self._ORDERS_START_IDX)
        else:
            idx = self.__genNextIdx(self.__equipmentFullMask, self._EQUIPMENT_START_IDX)
        self._addEquipmentSlot(idx, intCD, item)
        return

    def _isAvatarEquipment(self, item):
        return item.isAvatar()

    def _getEquipmentIconPath(self):
        return self._EQUIPMENT_ICON_PATH

    def __addListeners(self):
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onPostMortemSwitched += self._onPostMortemSwitched
            vehicleCtrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
            vehicleCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            self.__fillShells(ammoCtrl)
            ammoCtrl.onShellsAdded += self._onShellsAdded
            ammoCtrl.onShellsUpdated += self._onShellsUpdated
            ammoCtrl.onNextShellChanged += self._onNextShellChanged
            ammoCtrl.onCurrentShellChanged += self._onCurrentShellChanged
            ammoCtrl.onGunReloadTimeSet += self._onGunReloadTimeSet
            ammoCtrl.onGunSettingsSet += self._onGunSettingsSet
            ammoCtrl.onDebuffStarted += self.__onDebuffStarted
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            self.__fillEquipments(eqCtrl)
            eqCtrl.onEquipmentAdded += self._onEquipmentAdded
            eqCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
            eqCtrl.onEquipmentCooldownInPercent += self.__onEquipmentCooldownInPercent
            eqCtrl.onEquipmentCooldownTime += self.__onEquipmentCooldownTime
        optDevicesCtrl = self.sessionProvider.shared.optionalDevices
        if optDevicesCtrl is not None:
            self.__fillOptionalDevices(optDevicesCtrl)
            optDevicesCtrl.onOptionalDeviceAdded += self.__onOptionalDeviceAdded
            optDevicesCtrl.onOptionalDeviceUpdated += self.__onOptionalDeviceUpdated
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            currentSpgShotsState = self.sessionProvider.shared.crosshair.getSPGShotsIndicatorState()
            if vehicleCtrl is not None and ammoCtrl is not None and currentSpgShotsState:
                self.__onSPGShotsIndicatorStateChanged(currentSpgShotsState)
            crosshairCtrl.onSPGShotsIndicatorStateChanged += self.__onSPGShotsIndicatorStateChanged
            crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        CommandMapping.g_instance.onMappingChanged += self.__onMappingChanged
        g_eventBus.addListener(GameEvent.CHOICE_CONSUMABLE, self.__handleConsumableChoice, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def __removeListeners(self):
        g_eventBus.removeListener(GameEvent.CHOICE_CONSUMABLE, self.__handleConsumableChoice, scope=EVENT_BUS_SCOPE.BATTLE)
        CommandMapping.g_instance.onMappingChanged -= self.__onMappingChanged
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onSPGShotsIndicatorStateChanged -= self.__onSPGShotsIndicatorStateChanged
            crosshairCtrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onPostMortemSwitched -= self._onPostMortemSwitched
            vehicleCtrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
            vehicleCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellsAdded -= self._onShellsAdded
            ammoCtrl.onShellsUpdated -= self._onShellsUpdated
            ammoCtrl.onNextShellChanged -= self._onNextShellChanged
            ammoCtrl.onCurrentShellChanged -= self._onCurrentShellChanged
            ammoCtrl.onGunReloadTimeSet -= self._onGunReloadTimeSet
            ammoCtrl.onGunSettingsSet -= self._onGunSettingsSet
            ammoCtrl.onDebuffStarted -= self.__onDebuffStarted
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentAdded -= self._onEquipmentAdded
            eqCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
            eqCtrl.onEquipmentCooldownInPercent -= self.__onEquipmentCooldownInPercent
            eqCtrl.onEquipmentCooldownTime -= self.__onEquipmentCooldownTime
        optDevicesCtrl = self.sessionProvider.shared.optionalDevices
        if optDevicesCtrl is not None:
            optDevicesCtrl.onOptionalDeviceAdded -= self.__onOptionalDeviceAdded
            optDevicesCtrl.onOptionalDeviceUpdated -= self.__onOptionalDeviceUpdated
        return

    def __genNextIdx(self, full, start):
        bits = self._mask & full
        if not bits:
            idx = start
        else:
            idx = int(math.log(bits, 2)) + 1
        self._mask |= 1 << idx
        return idx

    def __genKey(self, idx):
        cmdMappingKey = COMMAND_AMMO_CHOICE_MASK.format(idx + 1 if idx < 9 else 0)
        bwKey = CommandMapping.g_instance.get(cmdMappingKey)
        sfKey = 0
        if bwKey is not None:
            sfKey = getScaleformKey(bwKey)
        return (bwKey, sfKey)

    def __makeShellTooltip(self, descriptor, piercingPower, shotSpeed):
        kind = descriptor.kind
        projSpeedFactor = vehicles.g_cache.commonConfig['miscParams']['projectileSpeedFactor']
        header = backport.text(R.strings.ingame_gui.shells_kinds.dyn(kind)(), caliber=backport.getNiceNumberFormat(descriptor.caliber), userString=descriptor.userString)
        if GUI_SETTINGS.technicalInfo:
            params = [backport.text(R.strings.ingame_gui.shells_kinds.params.damage(), value=backport.getNiceNumberFormat(descriptor.damage[0]))]
            if piercingPower != 0:
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.piercingPower(), value=backport.getNiceNumberFormat(piercingPower)))
            params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.shotSpeed(), value=backport.getIntegralFormat(shotSpeed / projSpeedFactor)))
            if kind == SHELL_TYPES.HIGH_EXPLOSIVE and descriptor.type.explosionRadius > 0.0:
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.explosionRadius(), value=backport.getNiceNumberFormat(descriptor.type.explosionRadius)))
            if descriptor.hasStun and self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
                stun = descriptor.stun
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.stunDuration(), minValue=backport.getNiceNumberFormat(stun.guaranteedStunDuration * stun.stunDuration), maxValue=backport.getNiceNumberFormat(stun.stunDuration)))
            body = text_styles.concatStylesToMultiLine(*params)
            fmt = TOOLTIP_FORMAT
        else:
            body = ''
            fmt = TOOLTIP_NO_BODY_FORMAT
        return fmt.format(header, body)

    def __getKeysGenerator(self):
        hasEquipment = self.sessionProvider.shared.equipments.hasEquipment
        getEquipment = self.sessionProvider.shared.equipments.getEquipment
        for idx, intCD in enumerate(self._cds):
            if not intCD:
                yield (idx,
                 None,
                 None,
                 None)
            bwKey, sfKey = self.__genKey(idx)
            handler = None
            if idx in self.__ammoRange:
                handler = partial(self.__handleAmmoPressed, intCD)
            elif (idx in self.__equipmentRange or idx in self.__ordersRange) and hasEquipment(intCD):
                item = getEquipment(intCD)
                if item is not None and item.getTags():
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
        extraKeys = {}
        slots = []
        for idx, bwKey, sfKey, handler in self.__getKeysGenerator():
            if handler:
                keys[bwKey] = handler
                extraKeys[idx] = handler
                slots.append((idx, bwKey, sfKey))

        self.as_setKeysToSlotsS(slots)
        self.__keys.clear()
        self.__keys = keys
        self.__extraKeys.clear()
        self.__extraKeys = extraKeys

    def __handleConsumableChoice(self, event):
        self.__handleBWKey(event.ctx['key'])

    def __handleBWKey(self, bwKey, idx=None):
        if bwKey == 0 and idx is not None:
            handler = self.__extraKeys.get(idx)
        else:
            handler = self.__keys.get(bwKey)
        if handler and callable(handler):
            handler()
        return

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
            if intCD not in self._cds:
                _logger.error('Equipment with cd=%d is not found in panel=%s', intCD, str(self._cds))
                return
            if not item:
                _logger.error('Equipment with cd=%d is not found in control', intCD)
                return
            slots = []
            keys = {}
            extraKeys = {}
            for entityIdx, (itemName, entityName, entityState) in enumerate(item.getGuiIterator()):
                bwKey, sfKey = self.__genKey(entityIdx)
                extraKeys[entityIdx] = keys[bwKey] = partial(self.__handleEquipmentPressed, intCD, entityName)
                slots.append({'bwKeyCode': bwKey,
                 'sfKeyCode': sfKey,
                 'entityName': itemName,
                 'entityState': entityState,
                 'entityIdx': entityIdx})

            self.__expandEquipmentSlot(self._cds.index(intCD), slots)
            self.__keys.clear()
            self.__keys = keys
            self.__extraKeys.clear()
            self.__extraKeys = extraKeys
            return

    def __onDebuffStarted(self, debuffTime=None):
        self.delayedReload = debuffTime

    def __startReloadDelayed(self, shellIndex, state):
        leftTimeDelayed = state.getActualValue() - self.delayedReload
        baseTimeDelayed = state.getBaseValue() - self.delayedReload
        if leftTimeDelayed > 0 and baseTimeDelayed > 0:
            shellReload = shellIndex
            if self.__delayedNextShellID is not None:
                shellReload = self._cds.index(self.__delayedNextShellID)
                self.__delayedNextShellID = None
            self.as_setCoolDownTimeS(shellReload, leftTimeDelayed, baseTimeDelayed, 0)
        else:
            _logger.error('Incorrect delayed reload timings: %f, %f', leftTimeDelayed, baseTimeDelayed)
        self.delayedReload = None
        return

    def __startReload(self, shellIndex, state):
        if self.__reloadTicker:
            self.__reloadTicker.startAnimation(shellIndex, state.getActualValue(), state.getBaseValue())
        else:
            self.as_setCoolDownTimeS(shellIndex, state.getActualValue(), state.getBaseValue(), state.getTimePassed())

    def __onEquipmentUpdated(self, intCD, item):
        if intCD in self._cds:
            self._updateEquipmentSlot(self._cds.index(intCD), item)
        else:
            _logger.error('Equipment with cd=%d is not found in panel=%s', intCD, str(self._cds))

    def __onEquipmentCooldownInPercent(self, intCD, percent):
        if intCD in self._cds:
            self.as_setCoolDownPosAsPercentS(self._cds.index(intCD), percent)

    def __onEquipmentCooldownTime(self, intCD, timeLeft, isBaseTime, isFlash):
        if intCD in self._cds:
            self.as_setCoolDownTimeSnapshotS(self._cds.index(intCD), timeLeft, isBaseTime, isFlash)

    def __onOptionalDeviceAdded(self, optDeviceInBattle):
        if optDeviceInBattle.getIntCD() not in self._cds:
            idx = self.__genNextIdx(self.__optDeviceFullMask, self._OPT_DEVICE_START_IDX)
            self._addOptionalDeviceSlot(idx, optDeviceInBattle)

    def __onOptionalDeviceUpdated(self, optDeviceInBattle):
        intCD = optDeviceInBattle.getIntCD()
        if intCD in self._cds:
            self._updateOptionalDeviceSlot(self._cds.index(intCD), optDeviceInBattle)
        else:
            _logger.error('Optional device with cd=%d is not found in panel=%s', intCD, str(self._cds))

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self._reset()
        if noRespawnPossible:
            if not BigWorld.player().isObserver():
                self.__removeListeners()

    def __onRespawnBaseMoving(self):
        self._reset()

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__clearAllEquipmentGlow()
            return
        elif self._cds.count(None) == self._PANEL_MAX_LENGTH:
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
                        self._showEquipmentGlow(self._cds.index(intCD))

                elif deviceState != DEVICE_STATE_DESTROYED:
                    for intCD, equipment in ctrl.iterEquipmentsByTag(equipmentTag):
                        if not self.__canApplyingGlowEquipment(equipment):
                            self.__clearEquipmentGlow(self._cds.index(intCD))

                idx = int(self.as_updateEntityStateS(itemName, actualState))
                if idx > 0 and idx < len(self._cds):
                    intCD = self._cds[idx]
                    if not ctrl.hasEquipment(intCD):
                        return
                    item = ctrl.getEquipment(intCD)
                    if item and item.isEntityRequired():
                        self.__replaceEquipmentKeyHandler(self.__keys, self._cds[idx], deviceName)
                        self.__replaceEquipmentKeyHandler(self.__extraKeys, self._cds[idx], deviceName)
            elif state == VEHICLE_VIEW_STATE.STUN:
                if value.duration > 0:
                    for intCD, _ in ctrl.iterEquipmentsByTag('medkit', _isEquipmentAvailableToUse):
                        self._showEquipmentGlow(self._cds.index(intCD))

                else:
                    for intCD, equipment in ctrl.iterEquipmentsByTag('medkit'):
                        if not self.__canApplyingGlowEquipment(equipment):
                            self.__clearEquipmentGlow(self._cds.index(intCD))

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
                            self._showEquipmentGlow(self._cds.index(cID))

                else:
                    for intCD, equipment in ctrl.iterEquipmentsByTag('extinguisher'):
                        if not equipment.getDescriptor().autoactivate:
                            self.__clearEquipmentGlow(self._cds.index(intCD))

            return

    def __replaceEquipmentKeyHandler(self, keysContainer, intCD, deviceName):
        tempDeviceName = VEHICLE_DEVICE_IN_COMPLEX_ITEM.get(deviceName, deviceName)
        for key in keysContainer:
            if tempDeviceName in keysContainer[key].args:
                keysContainer[key] = partial(self.__handleEquipmentPressed, intCD, deviceName)

    def __canApplyingGlowEquipment(self, equipment):
        equipmentTags = equipment.getTags()
        if 'extinguisher' in equipmentTags or 'regenerationKit' in equipmentTags:
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
        forEach(lambda args: self._onShellsAdded(*args), ctrl.getOrderedShellsLayout())
        shellCD = ctrl.getNextShellCD()
        if shellCD is not None:
            self._onNextShellChanged(shellCD)
        shellCD = ctrl.getCurrentShellCD()
        if shellCD is not None:
            self._onCurrentShellChanged(shellCD)
        return

    def __fillEquipments(self, ctrl):
        forEach(lambda args: self._onEquipmentAdded(*args), ctrl.getOrderedEquipmentsLayout())

    def __fillOptionalDevices(self, ctrl):
        forEach(lambda args: self.__onOptionalDeviceAdded(*args), ctrl.getOrderedOptionalDevicesLayout())

    def __onSPGShotsIndicatorStateChanged(self, shotStates):
        vehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
        ammoCtrl = self.sessionProvider.shared.ammo
        if vehicle is not None:
            vehicleDescriptor = vehicle.typeDescriptor
            for i, shotDescr in enumerate(vehicleDescriptor.gun.shots):
                intCD = shotDescr.shell.compactDescr
                if intCD in self._cds and ammoCtrl.shellInAmmo(intCD):
                    quantity, _ = ammoCtrl.getShells(intCD)
                    shotState, _ = shotStates.get(i, (-1, None)) if quantity > 0 else (-1, None)
                    self.as_setSPGShotResultS(self._cds.index(intCD), int(shotState))

        return

    def __onCrosshairViewChanged(self, viewID):
        vehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
        needClear = viewID not in (CROSSHAIR_VIEW_ID.STRATEGIC,)
        if vehicle is not None and needClear:
            vehicleDescriptor = vehicle.typeDescriptor
            for shotDescr in vehicleDescriptor.gun.shots:
                intCD = shotDescr.shell.compactDescr
                if intCD in self._cds:
                    self.as_setSPGShotResultS(self._cds.index(intCD), -1)

        return
