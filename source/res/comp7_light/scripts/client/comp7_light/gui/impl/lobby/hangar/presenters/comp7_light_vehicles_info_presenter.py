# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/hangar/presenters/comp7_light_vehicles_info_presenter.py
from comp7_core.gui.impl.lobby.hangar.presenters.comp7_core_vehicles_info_presenter import Comp7CoreVehiclesInfoPresenter
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

class Comp7LightVehiclesInfoPresenter(Comp7CoreVehiclesInfoPresenter):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    @property
    def _modeController(self):
        return self.__comp7LightController
