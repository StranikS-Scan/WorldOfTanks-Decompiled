# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tank_setup/configuration.py
from __future__ import absolute_import
from gui.impl.lobby.tank_setup.configurations.consumable import ConsumableTabsController, ConsumableTabs
from halloween.gui.impl.lobby.tank_setup.array_provider import HalloweenConsumableProvider

class HalloweenTabsController(ConsumableTabsController):
    __slots__ = ()

    def _getAllProviders(self):
        return {ConsumableTabs.DEFAULT: HalloweenConsumableProvider}
