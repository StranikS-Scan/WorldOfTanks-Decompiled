# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/battle/abilities_panel_ctrl.py
import logging
import CommandMapping
from helpers import dependency
from helpers.events_handler import EventsHandler
from typing import TYPE_CHECKING
from constants import EQUIPMENT_STAGES
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared.utils.key_mapping import getReadableKey
from grinch.gui.impl.gen.view_models.views.battle.grinch_hud.ability_model import AbilityModel
from grinch.gui.impl.gen.view_models.views.battle.grinch_hud.ability_model import AbilityTypeEnum
from grinch.gui.grinch_gui_constants import ABILITY_PANEL_COMMANDS_START
from grinch_common.grinch_constants import GrinchAbilities, GrinchShells
_logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    import Event
    from typing import Optional, Any, Tuple, Callable, Sequence
    from grinch.gui.impl.gen.view_models.views.battle.grinch_hud_view_model import GrinchHudViewModel
    from grinch.gui.battle_control.controllers.equipment_ctrl import _GrinchVisualScriptItem
    from gui.battle_control.controllers.consumables.ammo_ctrl import ReloadingTimeSnapshot
    from items.vehicle_items import Shell
_ABILITY_TYPE_BY_EQUIP_NAME = {GrinchAbilities.GRINCH_REPAIR_KIT: AbilityTypeEnum.REPAIRKIT,
 GrinchAbilities.GRINCH_HEAL: AbilityTypeEnum.HEAL,
 GrinchAbilities.GRINCH_RAGE: AbilityTypeEnum.RAGE,
 GrinchAbilities.GRINCH_STEALTH: AbilityTypeEnum.STEALTH,
 GrinchAbilities.GRINCH_TURRET: AbilityTypeEnum.TURRET,
 GrinchAbilities.GRINCH_BLIZZARD: AbilityTypeEnum.BLIZZARD,
 GrinchAbilities.GRINCH_FLARE: AbilityTypeEnum.FLARE}
_SHELL_TYPE_BY_SHELL_NAME = {GrinchShells.SHELL_CARRIER: AbilityTypeEnum.SHELLCARRIER,
 GrinchShells.SHELL_ASSAULT: AbilityTypeEnum.SHELLASSAULT,
 GrinchShells.SHELL_SUPPORT: AbilityTypeEnum.SHELLSUPPORT}
_AMMO_START_IDX = 0
_AMMO_COUNT = 1
_EQUIPMENT_START_IDX = _AMMO_START_IDX + _AMMO_COUNT
_EQUIPMENT_COUNT = 3
_TOTAL_PANEL_SLOTS = _AMMO_COUNT + _EQUIPMENT_COUNT
_NO_BINDING = ''

class AbilitiesPanelCtrl(EventsHandler):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, hudRef):
        super(AbilitiesPanelCtrl, self).__init__()
        self.__hudRef = hudRef
        self._subscribe()
        self._initModel()

    @property
    def viewModel(self):
        return self.__hudRef.viewModel

    def dispose(self):
        self._unsubscribe()

    def _getEvents(self):
        events = []
        events.append((CommandMapping.g_instance.onMappingChanged, self._onMappingChanged))
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            events.extend(((eqCtrl.onEquipmentAdded, self._onEquipmentAdded), (eqCtrl.onEquipmentUpdated, self._onEquipmentUpdated), (eqCtrl.onEquipmentsCleared, self._onClearEquipmentTimers)))
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            events.extend(((ammoCtrl.onGunReloadTimeSet, self._onGunReloadTimeSet), (ammoCtrl.onShellsAdded, self._onShellsAdded)))
        return events

    def _initModel(self):
        abilitiesArray = self.viewModel.getAbilities()
        abilitiesArray.reserve(_TOTAL_PANEL_SLOTS)
        for i in range(_TOTAL_PANEL_SLOTS):
            model = AbilityModel()
            model.setType(AbilityTypeEnum.NONE)
            model.setReloadTimeLeft(0)
            model.setKeyBind(self._getKeyString(i))
            abilitiesArray.addViewModel(model)

        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            for args in ammoCtrl.getOrderedShellsLayout():
                self._onShellsAdded(*args)

        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            for args in eqCtrl.getOrderedEquipmentsLayout():
                self._onEquipmentAdded(*args)

        return

    def _getKeyString(self, idx):
        if _AMMO_START_IDX <= idx < _EQUIPMENT_START_IDX:
            _logger.debug('[GrinchHudView] Index is of an ammo slot, ammo slots should not have keybindings.')
            return _NO_BINDING
        relativeEquipmentIndex = idx - _EQUIPMENT_START_IDX
        command = ABILITY_PANEL_COMMANDS_START + relativeEquipmentIndex
        return getReadableKey(command)

    def _onShellsAdded(self, intCD, descriptor, *args):
        _logger.debug('[GrinchHudView] Shell added: %s, %s', str(intCD), descriptor)
        idx = self._getAmmoIdx(intCD)
        if idx is None:
            return
        else:

            def addShell(model):
                model.setReloadTime(0)
                model.setType(_SHELL_TYPE_BY_SHELL_NAME[descriptor.name])
                model.setReloadTimeLeft(0)
                model.setIsActive(False)
                model.setKeyBind('')

            self._updateAbilityModel(idx, addShell)
            return

    def _onGunReloadTimeSet(self, intCD, state, skipAutoLoader):
        _logger.debug('[GrinchHudView] Reload: %s, %s, %d', str(intCD), str(state), skipAutoLoader)
        timeLeft = state.getTimeLeft()
        reloadTime = state.getBaseValue()
        idx = self._getAmmoIdx(intCD)
        if idx is None:
            return
        else:
            with self.viewModel.transaction() as model:
                abilityArray = model.getAbilities()
                abilityModel = abilityArray[idx]
                abilityModel.setReloadTime(reloadTime)
                abilityModel.setReloadTimeLeft(timeLeft)
            return

    def _onEquipmentUpdated(self, intCD, item):
        timeLeft = item.getTimeRemaining()
        maxTime = item.getTotalTime()
        stage = item.getStage()
        _logger.debug('[GrinchHudView] Equipment updated: intCD: %s, name: %s, timeLeft: %s, maxtime: %s, stage: %s, quantity: %s', str(intCD), item.getDescriptor().name, timeLeft, maxTime, stage, item.getQuantity())
        idx = self._getEquipmentIdx(intCD)
        if idx is None:
            return
        else:

            def updateEquipment(model):
                model.setIsEnabled(not item.isLocked())
                model.setIsTargeting(stage == EQUIPMENT_STAGES.PREPARING)
                model.setIsActive(stage == EQUIPMENT_STAGES.ACTIVE)
                if stage in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.ACTIVE):
                    model.setReloadTimeLeft(timeLeft)
                    model.setReloadTime(maxTime)
                if stage == EQUIPMENT_STAGES.READY:
                    model.setReloadTimeLeft(0)

            self._updateAbilityModel(idx, updateEquipment)
            return

    def _onEquipmentAdded(self, intCD, item):
        equipmentName = item.getDescriptor().name
        _logger.debug('[GrinchHudView] Equipment added: intCD %s, name: %s, quantity: %s, totalTime: %s, stage: %s', str(intCD), equipmentName, item.getQuantity(), item.getTotalTime(), item.getStage())
        idx = self._getEquipmentIdx(intCD)
        if idx is None:
            return
        else:

            def addEquipment(model):
                model.setReloadTime(item.getTotalTime())
                model.setType(_ABILITY_TYPE_BY_EQUIP_NAME[equipmentName])
                model.setReloadTimeLeft(0)
                model.setIsActive(False)
                model.setIsEnabled(not item.isLocked())

            self._updateAbilityModel(idx, addEquipment)
            return

    def _getEquipmentIdx(self, intCD):
        eqCtrl = self.sessionProvider.shared.equipments
        idx = [ equipmentLayout[0] for equipmentLayout in eqCtrl.getOrderedEquipmentsLayout() ].index(intCD)
        if idx is None:
            return
        else:
            idx += _EQUIPMENT_START_IDX
            if idx >= _TOTAL_PANEL_SLOTS:
                _logger.warning('[GrinchHudView] Equipment %d at index %d. The index is out of the expected range. Equipment indices start at %d, total equipment slots %d', intCD, idx, _EQUIPMENT_START_IDX, _TOTAL_PANEL_SLOTS)
                return
            return idx

    def _getAmmoIdx(self, intCD):
        ammoCtrl = self.sessionProvider.shared.ammo
        if intCD not in ammoCtrl.getShellsOrderIter():
            _logger.warning('[GrinchHudView] Shell %d cannot be found in ammo controller. Ammo list %s', intCD, ammoCtrl.getShellsLayout())
            return None
        idx = list(ammoCtrl.getShellsOrderIter()).index(intCD)
        idx += _AMMO_START_IDX
        if idx >= _EQUIPMENT_START_IDX:
            _logger.info('[GrinchHudView] Additional shell %d cannot be displayed in model. Model only displays %d shell(s).', intCD, _AMMO_COUNT)
            return None
        else:
            return idx

    def _updateAbilityModel(self, idx, updateFunc):
        abilityArray = self.viewModel.getAbilities()
        if idx >= len(abilityArray):
            _logger.warning('[GrinchHudView] Index is out of range for the abilities array. Array length: %s, Expected number of abilities %s', len(abilityArray), _TOTAL_PANEL_SLOTS)
            return
        abilityModel = abilityArray[idx]
        with abilityModel.transaction() as model:
            updateFunc(model)
        abilityArray.invalidate()

    def _onClearEquipmentTimers(self):
        _logger.debug('[GrinchHudView] Clearing equipment timers in the panel.')
        abilityArray = self.viewModel.getAbilities()
        for model in abilityArray:
            model.setReloadTimeLeft(0)

        abilityArray.invalidate()

    def _onMappingChanged(self, *args):
        _logger.debug('[GrinchHudView] Ability panel: Updating key bindings.')
        with self.viewModel.transaction() as model:
            abilities = model.getAbilities()
            for i, ability in enumerate(abilities):
                ability.setKeyBind(self._getKeyString(i))

            abilities.invalidate()
