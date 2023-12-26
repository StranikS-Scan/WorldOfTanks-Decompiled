# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/seniority_awards/__init__.py
from helpers import dependency
from skeletons.gui.game_control import ISeniorityAwardsController
from web.client_web_api.api import C2WHandler, c2w

class SeniorityAwardsEventHandler(C2WHandler):
    __seniorityAwardsCtrl = dependency.descriptor(ISeniorityAwardsController)

    def init(self):
        super(SeniorityAwardsEventHandler, self).init()
        self.__seniorityAwardsCtrl.onVehicleSelectionChanged += self.__seniorityAwardsVehicleSelectionUpdated

    def fini(self):
        self.__seniorityAwardsCtrl.onVehicleSelectionChanged -= self.__seniorityAwardsVehicleSelectionUpdated
        super(SeniorityAwardsEventHandler, self).fini()

    @c2w(name='seniority_awards_vehicle_selection_changed')
    def __seniorityAwardsVehicleSelectionUpdated(self, *args):
        return {'isVehicleSelectionAvailable': self.__seniorityAwardsCtrl.isVehicleSelectionAvailable}
