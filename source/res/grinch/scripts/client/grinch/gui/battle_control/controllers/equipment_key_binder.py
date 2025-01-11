# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/battle_control/controllers/equipment_key_binder.py
import typing
import logging
import CommandMapping
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.controllers.consumables.ammo_ctrl import IAmmoListener
from grinch.gui.grinch_gui_constants import ABILITY_PANEL_COMMANDS_START
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.battle_control.controllers.consumables.equipment_ctrl import _EquipmentItem

class GrinchEquipmentKeyBinder(IAmmoListener):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, alias):
        self._keyBindings = {}
        self._alias = alias
        self._addListeners()

    def getAlias(self):
        return self._alias

    @property
    def isActive(self):
        return True

    @property
    def keysOffset(self):
        return len(self._keyBindings)

    def handleAmmoKey(self, bwKey):
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

    def _addListeners(self):
        equipmentCtrl = self._sessionProvider.shared.equipments
        equipmentCtrl.onEquipmentAdded += self._onEquipmentAdded
        CommandMapping.g_instance.onMappingChanged += self._onMappingChanged
        self._sessionProvider.onBattleSessionStop += self._removeListeners

    def _removeListeners(self):
        equipmentCtrl = self._sessionProvider.shared.equipments
        equipmentCtrl.onEquipmentAdded -= self._onEquipmentAdded
        self._sessionProvider.onBattleSessionStop -= self._removeListeners
        CommandMapping.g_instance.onMappingChanged -= self._onMappingChanged

    def _onEquipmentAdded(self, intCD, item):
        self._rebindKeys()

    def _onMappingChanged(self, *args, **kwargs):
        self._rebindKeys()

    def _rebindKeys(self):
        equipmentCtrl = self._sessionProvider.shared.equipments
        self._keyBindings.clear()
        for equipmentCD, _ in equipmentCtrl.getOrderedEquipmentsLayout():
            if equipmentCD in self._keyBindings.values():
                continue
            self._createKeyBinding(equipmentCD)

        _logger.debug('KeyBinder: keys were rebound %s', self._keyBindings)

    def _createKeyBinding(self, intCD):
        instance = CommandMapping.g_instance
        command = self._getNewCommand()
        keys = instance.getCommandKeys(command)
        if not keys:
            _logger.warning('KeyBinder: cant get a keybinding for this command')
            return
        bwKey, _ = keys
        self._keyBindings[bwKey] = intCD
        _logger.debug('KeyBinder: created keybinding=%s for equipment=%s, keyBindings=%s', bwKey, intCD, self._keyBindings)

    def _getNewCommand(self):
        command = ABILITY_PANEL_COMMANDS_START + self.keysOffset
        if command > CommandMapping.CMD_AMMO_CHOICE_0:
            _logger.warning('KeyBinder: have no free command slots. current keyBinding = %s', self._keyBindings)
            return None
        else:
            return command
