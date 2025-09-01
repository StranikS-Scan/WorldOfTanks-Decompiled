# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/crosshair_type_updater.py
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdater
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class CrosshairTypeUpdater(ViewUpdater):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def initialize(self):
        super(CrosshairTypeUpdater, self).initialize()
        crosshairCtrl = self.__sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
            self.__onCrosshairViewChanged(crosshairCtrl.getViewID())
        return

    def finalize(self):
        crosshairCtrl = self.__sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        return

    def __onCrosshairViewChanged(self, viewID):
        self.view.setCrosshairType(viewID)
