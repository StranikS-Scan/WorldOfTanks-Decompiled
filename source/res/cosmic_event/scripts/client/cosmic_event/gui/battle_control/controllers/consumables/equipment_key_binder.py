# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/battle_control/controllers/consumables/equipment_key_binder.py
import typing
import logging
import CommandMapping
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.shared.events import HasCtxEvent
    from gui.battle_control.controllers.consumables.equipment_ctrl import _EquipmentItem
    from cosmic_event.gui.battle_control.controllers.consumables.equipment_ctrl import CosmicEquipmentsController
    from gui.battle_control.controllers.vehicle_state_ctrl import VehicleStateController
_logger = logging.getLogger(__name__)

class EquipmentKeyBinder(object):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _commandStart = CommandMapping.CMD_AMMO_CHOICE_1

    def __init__(self):
        self._keyBindings = {}
        self._sessionProvider.onBattleSessionStart += self._onBattleSessionStart
        _logger.debug('KeyBinder for cosmic was created')

    @property
    def isActive(self):
        return True

    @property
    def keysOffset(self):
        return len(self._keyBindings)

    def handleAmmoKey(self, bwKey, idx=None):
        self._activateEquipment(bwKey)

    def setCurrentShellCD(self, shellCD):
        pass

    def setNextShellCD(self, shellCD):
        pass

    def _activateEquipment(self, bwKey):
        equipmentCtrl = self._sessionProvider.shared.equipments
        if not equipmentCtrl:
            _logger.warning('KeyBinder: trying reach equipments controller that is not created yet')
            return
        else:
            intCD = self._keyBindings.get(bwKey, None)
            if intCD is None:
                _logger.info('KeyBinder: cannot find bwKey=%s in keyBinding=%s', str(self._keyBindings), bwKey)
                return
            _logger.debug('KeyBinder: activate ability with intCD %s', intCD)
            equipmentCtrl.changeSetting(intCD)
            return

    def _handleConsumableChoice(self, event):
        self._activateEquipment(event.ctx['key'])

    def _getNewCommand(self):
        command = self._commandStart + self.keysOffset
        if command > CommandMapping.CMD_AMMO_CHOICE_0:
            _logger.warning('KeyBinder: have no free command slots. current keybinding = %s', self._keyBindings)
            return None
        else:
            return command

    def _onEquipmentAdded(self, intCD, item):
        self._rebindKeys()

    def _onEquipmentRemoved(self, intCD, item):
        bwKey = next((k for k, v in self._keyBindings.iteritems() if v == intCD), None)
        if bwKey:
            _logger.debug('KeyBinder: removing keybinding for the bwKey %s and %s', bwKey, intCD)
            self._keyBindings.pop(bwKey)
        return

    def _onBattleSessionStart(self):
        equipmentCtrl = self._sessionProvider.shared.equipments
        equipmentCtrl.onEquipmentAdded += self._onEquipmentAdded
        equipmentCtrl.onEquipmentRemoved += self._onEquipmentRemoved
        self._sessionProvider.onBattleSessionStop += self._onBattleSessionStop
        CommandMapping.g_instance.onMappingChanged += self._onMappingChanged
        vehicleCtrl = self._sessionProvider.shared.vehicleState
        vehicleCtrl.onPostMortemSwitched += self._onPostMortemSwitched
        g_eventBus.addListener(GameEvent.CHOICE_CONSUMABLE, self._handleConsumableChoice, scope=EVENT_BUS_SCOPE.BATTLE)

    def _onBattleSessionStop(self):
        equipmentCtrl = self._sessionProvider.shared.equipments
        equipmentCtrl.onEquipmentAdded -= self._onEquipmentAdded
        equipmentCtrl.onEquipmentRemoved -= self._onEquipmentRemoved
        vehicleCtrl = self._sessionProvider.shared.vehicleState
        vehicleCtrl.onPostMortemSwitched -= self._onPostMortemSwitched
        self._sessionProvider.onBattleSessionStart -= self._onBattleSessionStart
        self._sessionProvider.onBattleSessionStop -= self._onBattleSessionStop
        CommandMapping.g_instance.onMappingChanged -= self._onMappingChanged
        g_eventBus.removeListener(GameEvent.CHOICE_CONSUMABLE, self._handleConsumableChoice, scope=EVENT_BUS_SCOPE.BATTLE)
        self._keyBindings.clear()

    def _onMappingChanged(self, *args, **kwargs):
        self._rebindKeys()

    def _rebindKeys(self):
        equipmentCtrl = self._sessionProvider.shared.equipments
        self._keyBindings.clear()
        for equipmentCD, _ in equipmentCtrl.getOrderedEquipmentsLayout():
            if equipmentCD in self._keyBindings.values():
                continue
            self._createKeyBinding(equipmentCD)

        _logger.debug('KeyBinder: keys were rebinded %s', self._keyBindings)

    def _createKeyBinding(self, intCD):
        instance = CommandMapping.g_instance
        command = self._getNewCommand()
        keys = instance.getCommandKeys(command)
        if not keys:
            _logger.warning('KeyBinder: cant get a keybinding for this command')
            return
        bwKey, _ = keys
        self._keyBindings[bwKey] = intCD
        _logger.debug('KeyBinder: created keybinding=%s for equipment=%s, _keyBindings=%s', bwKey, intCD, self._keyBindings)

    def _onPostMortemSwitched(self, *args, **kwargs):
        self._keyBindings.clear()
