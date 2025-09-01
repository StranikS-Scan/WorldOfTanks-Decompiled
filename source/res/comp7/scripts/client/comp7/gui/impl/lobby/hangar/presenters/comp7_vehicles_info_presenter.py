# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/hangar/presenters/comp7_vehicles_info_presenter.py
from comp7_core.gui.impl.lobby.hangar.presenters.comp7_core_vehicles_info_presenter import Comp7CoreVehiclesInfoPresenter
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7VehiclesInfoPresenter(Comp7CoreVehiclesInfoPresenter):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @property
    def _modeController(self):
        return self.__comp7Controller
