# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/schedule_presenter.py
from __future__ import absolute_import
from comp7.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_TOOLTIPS
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName
from comp7.gui.impl.gen.view_models.views.lobby.schedule_info_model import ScheduleInfoModel
from comp7.gui.impl.gen.view_models.views.lobby.season_model import SeasonState
from comp7.gui.impl.gen.view_models.views.lobby.year_model import YearState
from comp7_core.gui.impl.lobby.comp7_core_helpers import comp7_core_model_helpers
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class SchedulePresenter(ViewComponent[ScheduleInfoModel], IGlobalListener):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self):
        super(SchedulePresenter, self).__init__(model=ScheduleInfoModel)

    def _onLoading(self, *args, **kwargs):
        self.__onScheduleUpdated()

    def __addListeners(self):
        self.viewModel.scheduleInfo.season.pollServerTime += self.__onScheduleUpdated
        self.__comp7Controller.onModeConfigChanged += self.__onScheduleUpdated
        self.__comp7Controller.onStatusUpdated += self.__onStatusUpdated

    def __removeListeners(self):
        self.viewModel.scheduleInfo.season.pollServerTime -= self.__onScheduleUpdated
        self.__comp7Controller.onModeConfigChanged -= self.__onScheduleUpdated
        self.__comp7Controller.onStatusUpdated -= self.__onStatusUpdated

    @property
    def viewModel(self):
        return super(SchedulePresenter, self).getViewModel()

    def __onScheduleUpdated(self):
        comp7_core_model_helpers.setScheduleInfo(self.viewModel, self.__comp7Controller, COMP7_TOOLTIPS.COMP7_CALENDAR_DAY_INFO, SeasonState, YearState, SeasonName)
