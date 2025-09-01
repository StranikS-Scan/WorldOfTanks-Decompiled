# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/current_shell_damage_updater.py
import logging
import typing
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdater
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Any
    from gui.battle_control.battle_session import BattleSessionProvider
    from gui.battle_control.controllers.consumables.ammo_ctrl import AmmoController
_logger = logging.getLogger(__name__)

class CurrentShellDamageUpdater(ViewUpdater):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, view):
        super(CurrentShellDamageUpdater, self).__init__(view)
        self.__currentDamage = 0

    def initialize(self):
        super(CurrentShellDamageUpdater, self).initialize()
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            _logger.error('No AmmoController found.')
            return
        else:
            ammoCtrl.onShellsUpdated += self.__onCurrentShellDamageChanged
            ammoCtrl.onCurrentShellChanged += self.__onCurrentShellDamageChanged
            ammoCtrl.onCurrentShellReset += self.__onCurrentShellDamageChanged
            self.__onCurrentShellDamageChanged()
            return

    def finalize(self):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellsUpdated -= self.__onCurrentShellDamageChanged
            ammoCtrl.onCurrentShellChanged -= self.__onCurrentShellDamageChanged
            ammoCtrl.onCurrentShellReset -= self.__onCurrentShellDamageChanged
        super(CurrentShellDamageUpdater, self).finalize()
        return

    def __getCurrentShellDamage(self):
        ammoCtrl = self.__sessionProvider.shared.ammo
        currentShellCD = ammoCtrl.getCurrentShellCD()
        if currentShellCD is None:
            return 0
        else:
            quantity, _ = ammoCtrl.getShells(currentShellCD)
            return 0 if quantity == 0 else ammoCtrl.getGunSettings().getShellDescriptor(currentShellCD).armorDamage[0]

    def __onCurrentShellDamageChanged(self, *_):
        newDamage = self.__getCurrentShellDamage()
        if newDamage == self.__currentDamage:
            return
        self.__currentDamage = newDamage
        self.view.onCurrentShellDamageChanged(newDamage)
