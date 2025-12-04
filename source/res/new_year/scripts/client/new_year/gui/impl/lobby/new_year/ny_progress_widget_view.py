# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/ny_progress_widget_view.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.ny_progress_widget_model import NyProgressWidgetModel
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from new_year.gui.impl.lobby.new_year.sub_model_presenter import SubModelPresenter
from new_year.skeletons.new_year import INewYearController
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year_common.items.components.ny_constants import NewYearObjects

class NyProgressWidgetView(SubModelPresenter):
    __slots__ = ()
    __nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def initialize(self, *args, **kwargs):
        super(NyProgressWidgetView, self).initialize(*args, **kwargs)
        self.__updateProgress()

    def _getEvents(self):
        return ((self.__nyController.onDataUpdated, self.__onDataUpdate), (self.__nyController.onVariadicDiscountsUpdated, self.__onDiscountUpdate), (NewYearNavigation.onUpdateCurrentView, self.__updatePlaceEntrace))

    def __updateProgress(self):
        progress = NewYearAtmospherePresenter.getPercentsLevelProgress()
        with self.getViewModel().transaction() as ts:
            ts.setLevel(NewYearAtmospherePresenter.getLevel())
            ts.setProgress(progress)
            ts.setIsPlaceEntrance(False)
            ts.setRewardsCount(self.__nyController.getVariadicDiscountCount())

    def __onDataUpdate(self, _):
        self.__updateProgress()

    def __updatePlaceEntrace(self, *_, **__):
        with self.getViewModel().transaction() as ts:
            ts.setIsPlaceEntrance(NewYearNavigation.getCurrentObject() != NewYearObjects.CITY_VIEW)

    def __onDiscountUpdate(self):
        with self.getViewModel().transaction() as ts:
            ts.setRewardsCount(self.__nyController.getVariadicDiscountCount())
