# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/tank_setup/configuration.py
from gui.impl.lobby.tank_setup.configurations.consumable import ConsumableTabsController, ConsumableTabs
from last_stand.gui.impl.lobby.tank_setup.array_provider import LSConsumableProvider

class LastStandTabsController(ConsumableTabsController):
    __slots__ = ()

    def _getAllProviders(self):
        return {ConsumableTabs.DEFAULT: LSConsumableProvider}
