# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/shooting_updaters.py
import typing
from gui.battle_control.controllers.vehicle_passenger import hasVehiclePassengerCtrl, VehiclePassengerInfoWatcher
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdater
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from items.components.gun_installation_components import GunInstallationSlot

class IShootingReactionsView(object):

    def onDiscreteShotsDone(self, gunInstallationSlot, isCurrentVehicle):
        raise NotImplementedError


class ShootingReactionsUpdater(ViewUpdater, VehiclePassengerInfoWatcher):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def initialize(self):
        super(ShootingReactionsUpdater, self).initialize()
        feedbackCtrl = self.__sessionProvider.shared.feedback
        if feedbackCtrl is not None:
            feedbackCtrl.onDiscreteShotsDone += self.__onDiscreteShotsDone
        return

    def finalize(self):
        feedbackCtrl = self.__sessionProvider.shared.feedback
        if feedbackCtrl is not None:
            feedbackCtrl.onDiscreteShotsDone -= self.__onDiscreteShotsDone
        super(ShootingReactionsUpdater, self).finalize()
        return

    @hasVehiclePassengerCtrl()
    def __onDiscreteShotsDone(self, entityID, gunInstallationSlot, passengerCtrl=None):
        self.view.onDiscreteShotsDone(gunInstallationSlot, entityID == passengerCtrl.currentVehicleID)
