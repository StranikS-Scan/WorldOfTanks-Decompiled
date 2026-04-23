# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/consumables_panel.py
from functools import partial
import logging
import typing
import BigWorld
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from constants import EQUIPMENT_STAGES
from gui import TANKMEN_ROLES_ORDER_DICT
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import TOOLTIP_FORMAT
from gui.battle_control.controllers.consumables.ammo_ctrl import AmmoController
from historical_battles.gui.Scaleform.daapi.view.meta.HBConsumablesPanelMeta import HBConsumablesPanelMeta
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from gui.Scaleform.genConsts.HBBATTLE_CONSUMABLES_PANEL_PASSIVE_STATES import HBBATTLE_CONSUMABLES_PANEL_PASSIVE_STATES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, getVehicleDeviceInComplexItemName, DEVICE_STATE_AS_DAMAGE, DEVICE_STATE_CRITICAL, DEVICE_STATE_DESTROYED
from gui.battle_control.controllers.consumables.equipment_ctrl import NeedEntitySelection, IgnoreEntitySelection
from gui.impl import backport
from gui.impl.gen import R
from items.artefacts import SharedCooldownConsumableConfigReader
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.equipment_ctrl import _EquipmentItem
_ACTIVE_EQUIPMENT_STAGES = (EQUIPMENT_STAGES.PREPARING, EQUIPMENT_STAGES.ACTIVE)
_logger = logging.getLogger(__name__)

def _isEquipmentAvailableToUse(eq):
    return eq.isAvailableToUse


class HistoricalBattlesConsumablesPanel(HBConsumablesPanelMeta):
    _ORDERS_START_IDX = 0
    _ORDERS_END_IDX = 2
    _AMMO_START_IDX = 6
    _AMMO_END_IDX = 8
    _PASSIVE_START_IDX = 9
    _PASSIVE_END_IDX = 11

    def __init__(self):
        super(HistoricalBattlesConsumablesPanel, self).__init__()
        self._permanentGlows = set()
        self.__passivesOffset = 0

    def _populate(self):
        super(HistoricalBattlesConsumablesPanel, self)._populate()
        self.__addListeners()

    def _dispose(self):
        self.__removeListeners()
        super(HistoricalBattlesConsumablesPanel, self)._dispose()

    def setCurrentShellCD(self, _):
        pass

    def setNextShellCD(self, _):
        pass

    def handleAmmoKey(self, key):
        super(HistoricalBattlesConsumablesPanel, self).handleAmmoKey(key)

    def _showPermanentGlow(self, idx, glowID=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL):
        if BigWorld.player().isObserver():
            return
        self._permanentGlows.add(idx)
        self.as_setGlowS(idx, glowID)

    def _hidePermanentGlow(self, idx):
        if idx in self._permanentGlows:
            self._permanentGlows.remove(idx)
            if idx not in self._equipmentsGlowCallbacks:
                self.as_hideGlowS(idx)

    def _isGlowShown(self, idx):
        return idx in self._permanentGlows or idx in self._equipmentsGlowCallbacks

    def _clearEquipmentGlow(self, equipmentIndex, cancelCallback=True):
        if equipmentIndex in self._equipmentsGlowCallbacks:
            if equipmentIndex not in self._permanentGlows:
                self.as_hideGlowS(equipmentIndex)
            if cancelCallback:
                BigWorld.cancelCallback(self._equipmentsGlowCallbacks[equipmentIndex])
            del self._equipmentsGlowCallbacks[equipmentIndex]

    def _getEquipmentIcon(self, idx, item, iconName):
        iconDynAcc = R.images.historical_battles.gui.maps.icons.artefact.dyn(iconName)
        if not iconDynAcc:
            iconDynAcc = R.images.gui.maps.icons.artefact.dyn(iconName)
        return backport.image(iconDynAcc())

    def _isAvatarEquipment(self, item):
        return self._isAbility(item)

    def _addEquipmentSlot(self, idx, intCD, item):
        if item is None:
            return
        else:
            if self._isAbility(item):
                self._cds[idx] = intCD
                bwKey, sfKey = self._genKey(idx)
                handler = partial(self._handleEquipmentPressed, intCD)
                if item.getQuantity() > 0:
                    self._keys[bwKey] = handler
                descriptor = item.getDescriptor()
                quantity = item.getQuantity()
                timeRemaining = item.getTimeRemaining()
                reloadingTime = item.getTotalTime()
                iconPath = self._getEquipmentIcon(idx, None, descriptor.icon[0])
                toolTip = self.__getTooltip(descriptor)
                abilityData = {'keyCode': bwKey,
                 'sfKeyCode': sfKey,
                 'quantity': quantity,
                 'timeRemaining': timeRemaining,
                 'reloadingTime': reloadingTime,
                 'iconPath': iconPath,
                 'tooltipText': toolTip}
                if not self._isPassiveAbility(item):
                    self.as_addAbilitySlotS(idx, abilityData)
                else:
                    self.as_addPassiveAbilitySlotS(idx, iconPath, HBBATTLE_CONSUMABLES_PANEL_PASSIVE_STATES.UNAVAILABLE, toolTip)
                self._updateEquipmentSlot(idx, item)
            else:
                super(HistoricalBattlesConsumablesPanel, self)._addEquipmentSlot(idx, intCD, item)
            return

    def _clearAllEquipmentGlow(self):
        super(HistoricalBattlesConsumablesPanel, self)._clearAllEquipmentGlow()
        self._permanentGlows.clear()
        for idx in xrange(self._EQUIPMENT_START_IDX, self._ORDERS_END_IDX + 1):
            self.as_hideGlowS(idx)

    def _handleAbilityGlow(self, currStage, prevStage, idx):
        if currStage in (EQUIPMENT_STAGES.DEPLOYING,
         EQUIPMENT_STAGES.COOLDOWN,
         EQUIPMENT_STAGES.NOT_RUNNING,
         EQUIPMENT_STAGES.UNAVAILABLE):
            self.as_hideGlowS(idx)
            self.as_setEquipmentActivatedS(idx, False)
        elif currStage == EQUIPMENT_STAGES.READY and (prevStage == EQUIPMENT_STAGES.COOLDOWN or prevStage == EQUIPMENT_STAGES.NOT_RUNNING):
            self.as_setGlowS(idx, glowID=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL)
        elif currStage == EQUIPMENT_STAGES.READY and prevStage == EQUIPMENT_STAGES.READY:
            self.as_setGlowS(idx, glowID=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN)
        elif currStage in _ACTIVE_EQUIPMENT_STAGES and prevStage not in _ACTIVE_EQUIPMENT_STAGES:
            self.as_setEquipmentActivatedS(idx, True)
        elif currStage not in _ACTIVE_EQUIPMENT_STAGES and prevStage in _ACTIVE_EQUIPMENT_STAGES:
            self.as_setEquipmentActivatedS(idx, False)

    def _handlePassiveAbilityGlow(self, currStage, idx, toolTip):
        if currStage == EQUIPMENT_STAGES.NOT_RUNNING:
            self.as_updatePassiveAbilityS(idx, HBBATTLE_CONSUMABLES_PANEL_PASSIVE_STATES.UNAVAILABLE, toolTip)
        else:
            self.as_updatePassiveAbilityS(idx, HBBATTLE_CONSUMABLES_PANEL_PASSIVE_STATES.ACTIVE, toolTip)

    def _updateEquipmentSlot(self, idx, item):
        if not self._isAbility(item):
            super(HistoricalBattlesConsumablesPanel, self)._updateEquipmentSlot(idx, item)
            return
        currStage = item.getStage()
        if not self._isPassiveAbility(item):
            prevStage = item.getPrevStage()
            currentTime = item.getTimeRemaining()
            maxTime = item.getTotalTime()
            self.as_updateAbilityS(idx, currStage, currentTime, maxTime)
            self._handleAbilityGlow(currStage, prevStage, idx)
        else:
            descriptor = item.getDescriptor()
            toolTip = self.__getTooltip(descriptor)
            self.as_updatePassiveAbilityS(idx, HBBATTLE_CONSUMABLES_PANEL_PASSIVE_STATES.UNAVAILABLE, toolTip)
            self._handlePassiveAbilityGlow(currStage, idx, toolTip)
        bwKey, _ = self._genKey(idx)
        quantity = item.getQuantity()
        if quantity > 0 and bwKey not in self._keys:
            self._keys[bwKey] = partial(self._handleEquipmentPressed, self._cds[idx])

    def _onEquipmentAdded(self, intCD, item):
        if self._isPassiveAbility(item):
            if self._PASSIVE_START_IDX + self.__passivesOffset > self._PASSIVE_END_IDX:
                _logger.error("Cannot generate idx for %s item. Consumables panel's passive section already full", intCD)
                return
            idx = self._PASSIVE_START_IDX + self.__passivesOffset
            self.__passivesOffset += 1
            self._addEquipmentSlot(idx, intCD, item)
        else:
            super(HistoricalBattlesConsumablesPanel, self)._onEquipmentAdded(intCD, item)

    def _resetEquipments(self):
        for idx in xrange(self._PASSIVE_START_IDX, self._PASSIVE_END_IDX):
            self._cds[idx] = None

        self.__passivesOffset = 0
        super(HistoricalBattlesConsumablesPanel, self)._resetEquipments()
        return

    def _addShellSlot(self, idx, intCD, descriptor, quantity, gunSettings):
        super(HistoricalBattlesConsumablesPanel, self)._addShellSlot(idx, intCD, descriptor, quantity, gunSettings)
        arenaBonusType = BigWorld.player().arenaBonusType
        if arenaBonusType and BONUS_CAPS.checkAny(arenaBonusType, BONUS_CAPS.INFINITE_AMMO) and quantity > 0:
            self.as_setShellInfinityS(idx, True)

    @staticmethod
    def _isAbility(item):
        return 'hb_ability' in item.getDescriptor().tags

    @staticmethod
    def _isPassiveAbility(item):
        return 'hb_passive_ability' in item.getDescriptor().tags

    def _onVehicleStateUpdated(self, state, value):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is None:
            return
        else:
            if state == VEHICLE_VIEW_STATE.DEVICES:
                deviceName, _, actualState = value
                itemName = getVehicleDeviceInComplexItemName(deviceName)
                equipmentTag = 'medkit' if itemName in TANKMEN_ROLES_ORDER_DICT['enum'] else 'repairkit'
                if actualState in DEVICE_STATE_AS_DAMAGE:
                    for intCD, equipment in ctrl.iterEquipmentsByTag(equipmentTag, _isEquipmentAvailableToUse):
                        idx = self._cds.index(intCD)
                        if actualState == DEVICE_STATE_CRITICAL:
                            if not self._isGlowShown(idx):
                                self._showEquipmentGlow(idx)
                            if not self._canApplyingGlowEquipment(equipment, (DEVICE_STATE_DESTROYED,)):
                                self._hidePermanentGlow(idx)
                        self._showPermanentGlow(idx)

                else:
                    for intCD, equipment in ctrl.iterEquipmentsByTag(equipmentTag):
                        if not self._canApplyingGlowEquipment(equipment):
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
                super(HistoricalBattlesConsumablesPanel, self)._onVehicleStateUpdated(state, value)
            return

    def _canApplyingGlowEquipment(self, equipment, checkDeviceStates=None):
        equipmentTags = equipment.getTags()
        if 'extinguisher' in equipmentTags or 'regenerationKit' in equipmentTags or 'repairkit' in equipmentTags:
            correction = True
            entityName = None
        elif equipment.isAvatar():
            correction = False
            entityName = None
        else:
            availableStates = checkDeviceStates
            if not availableStates:
                availableStates = DEVICE_STATE_AS_DAMAGE
            entityNames = [ name for name, state in equipment.getEntitiesIterator() if state in availableStates ]
            correction = hasDestroyed = len(entityNames)
            entityName = entityNames[0] if hasDestroyed else None
        canActivate, info = equipment.canActivate(entityName)
        infoType = type(info)
        return correction and (canActivate or infoType == NeedEntitySelection) or infoType == IgnoreEntitySelection

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        super(HistoricalBattlesConsumablesPanel, self)._onPostMortemSwitched(noRespawnPossible, respawnAvailable)
        self.as_resetPassiveAbilitiesS()

    def __getTooltip(self, descriptor):
        body = descriptor.description
        if isinstance(descriptor, SharedCooldownConsumableConfigReader):
            cdSecVal = descriptor.cooldownTime
        else:
            cdSecVal = descriptor.cooldownSeconds
        if cdSecVal:
            tooltipStr = R.strings.ingame_gui.consumables_panel.equipment.cooldownSeconds()
            cooldownSeconds = str(int(cdSecVal))
            paramsString = backport.text(tooltipStr, cooldownSeconds=cooldownSeconds)
            body = '\n\n'.join((body, paramsString))
        return TOOLTIP_FORMAT.format(descriptor.userString, body)

    def __addListeners(self):
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.setViewComponents(self)
        return

    def __removeListeners(self):
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.clearViewComponents()
        return
