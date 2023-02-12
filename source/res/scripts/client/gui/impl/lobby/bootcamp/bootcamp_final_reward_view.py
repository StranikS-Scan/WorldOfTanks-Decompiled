# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bootcamp/bootcamp_final_reward_view.py
from bootcamp.Bootcamp import g_bootcamp
from items import vehicles
from nations import INDICES as NATIONS_INDICES
from gui.impl.gen import R
from gui.impl.gen.view_models.views.bootcamp.bootcamp_final_reward_model import BootcampFinalRewardModel
from gui.impl.gen.view_models.views.bootcamp.vehicle_model import VehicleModel
from gui.shared.gui_items.Vehicle import getIconResourceName
from helpers import dependency
from skeletons.gui.game_control import IBootcampController
from tutorial.gui.Scaleform.pop_ups import TutorialWulfWindowView

class BootcampFinalRewardView(TutorialWulfWindowView):
    __slots__ = ()
    __bootcampController = dependency.descriptor(IBootcampController)

    @property
    def viewModel(self):
        return super(BootcampFinalRewardView, self).getViewModel()

    def getLayoutID(self):
        return R.views.lobby.bootcamp.BootcampFinalRewardView()

    def _createModel(self):
        return BootcampFinalRewardModel()

    def _onLoading(self, *args, **kwargs):
        super(BootcampFinalRewardView, self)._onLoading(*args, **kwargs)
        nationsOrder = g_bootcamp.getNationsOrder('awarding')
        with self.viewModel.transaction() as model:
            model.setIsNeedAwarding(self.__bootcampController.needAwarding())
            modelVehicles = model.getVehicles()
            for nationId in nationsOrder:
                nationData = g_bootcamp.getNationData(NATIONS_INDICES[nationId])
                vehicleName = nationData['vehicle_reward']
                vehicleDescr = vehicles.VehicleDescr(typeName=vehicleName)
                modelVehicles.addViewModel(self.__createVehicleModel(R.images.gui.maps.icons.bootcamp.final_reward.vehicles.dyn(getIconResourceName(vehicleName))(), vehicleDescr.type.userString))

            model.onProceed += self.__onProceed

    def _finalize(self):
        self.viewModel.onProceed -= self.__onProceed
        super(BootcampFinalRewardView, self)._finalize()

    def __onProceed(self):
        self.submit()

    @staticmethod
    def __createVehicleModel(icon, name):
        vehicle = VehicleModel()
        vehicle.setIcon(icon)
        vehicle.setName(name)
        return vehicle
