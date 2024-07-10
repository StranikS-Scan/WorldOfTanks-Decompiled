# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/hangar_shells_counter_mapping.py
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS

class ShellCounterMapping(dict):

    def __init__(self, vehicle):
        super(ShellCounterMapping, self).__init__({vehicle.gun.isDamageMutable: UI_STORAGE_KEYS.MUTABLE_DAMAGE_SHELL_MARK_IS_SHOWN})
