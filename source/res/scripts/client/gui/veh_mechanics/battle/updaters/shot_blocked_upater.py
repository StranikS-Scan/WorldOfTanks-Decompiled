# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/shot_blocked_upater.py
import logging
import typing
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdater
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.ammo_ctrl import AmmoController
_logger = logging.getLogger(__name__)

class ShotBlockedUpdater(ViewUpdater):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def initialize(self):
        super(ShotBlockedUpdater, self).initialize()
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            _logger.error('No AmmoController found.')
            return
        else:
            ammoCtrl.onShotBlocked += self.__onShotBlocked
            return

    def finalize(self):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShotBlocked -= self.__onShotBlocked
        super(ShotBlockedUpdater, self).finalize()
        return

    def __onShotBlocked(self, error):
        self.view.onShotBlocked(error)
