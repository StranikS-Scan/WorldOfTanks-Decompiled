# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/presenters/vehicle_filters_presenter.py
import typing
import BigWorld
from account_helpers.settings_core import settings_constants
from battle_royale.gui.impl.gen.view_models.views.lobby.views.vehicles_filter_model import VehiclesFilterModel
from gui import GUI_NATIONS
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
if typing.TYPE_CHECKING:
    from typing import Any

class BattleRoyaleVehicleFiltersPresenter(ViewComponent[VehiclesFilterModel]):
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__rowCount = None
        super(BattleRoyaleVehicleFiltersPresenter, self).__init__(model=VehiclesFilterModel)
        return

    @property
    def viewModel(self):
        return super(BattleRoyaleVehicleFiltersPresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattleRoyaleVehicleFiltersPresenter, self)._onLoading(*args, **kwargs)
        self.__updateCarousel()

    def _getEvents(self):
        return ((self.__settingsCore.onSettingsChanged, self.__onCarouselSettingsChange),)

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            model.setCarouselRowCount(self.__rowCount)
            nationsOrder = model.getNationsOrder()
            nationsOrder.clear()
            for nation in GUI_NATIONS:
                nationsOrder.addString(nation)

    def __onCarouselSettingsChange(self, diff):
        if settings_constants.GAME.CAROUSEL_TYPE in diff and BigWorld.player() is not None:
            self.__updateCarousel()
        return

    def __updateCarousel(self):
        self.__readSettings()
        self.__updateModel()

    def __readSettings(self):
        setting = self.__settingsCore.options.getSetting(settings_constants.GAME.CAROUSEL_TYPE)
        self.__rowCount = setting.getRowCount()
