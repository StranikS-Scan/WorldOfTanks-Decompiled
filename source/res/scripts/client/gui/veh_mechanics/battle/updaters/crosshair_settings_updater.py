# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/crosshair_settings_updater.py
from __future__ import absolute_import
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdater
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class CrosshairSettingsUpdater(ViewUpdater):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def initialize(self):
        super(CrosshairSettingsUpdater, self).initialize()
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onGunSettingsSet += self.__onGunSettingsSet
        return

    def finalize(self):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onGunSettingsSet -= self.__onGunSettingsSet
        super(CrosshairSettingsUpdater, self).finalize()
        return

    def __onGunSettingsSet(self, gunSettings):
        self.view.setGunSettings(gunSettings)
