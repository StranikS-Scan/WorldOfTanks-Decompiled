# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/mechanics/low_charge_shot_updater.py
from __future__ import absolute_import
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdater
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class LowChargeShotUpdater(ViewUpdater):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def initialize(self):
        super(LowChargeShotUpdater, self).initialize()
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellChangeTimeUpdated += self.__onShellChangeTimeUpdated
            ammoCtrl.onGunReloadTimeSet += self.__onGunReloadTimeSet
            self.__onShellChangeTimeUpdated(ammoCtrl.canQuickShellChange(), ammoCtrl.getQuickShellChangeTimes())
        return

    def finalize(self):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellChangeTimeUpdated -= self.__onShellChangeTimeUpdated
            ammoCtrl.onGunReloadTimeSet -= self.__onGunReloadTimeSet
        super(LowChargeShotUpdater, self).finalize()
        return

    def __onShellChangeTimeUpdated(self, isVisible, shellChangeTimes):
        self.view.setShellChangeTime(isVisible, shellChangeTimes)

    def __onGunReloadTimeSet(self, _, state, __):
        self.view.setBaseTimeBeforeBattleOrEmpty(state.getBaseValue())
