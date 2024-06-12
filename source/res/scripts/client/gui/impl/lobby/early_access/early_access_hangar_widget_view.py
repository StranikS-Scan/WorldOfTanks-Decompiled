# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/early_access_hangar_widget_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.early_access.early_access_state_enum import State
from gui.impl.gen.view_models.views.lobby.early_access.early_access_widget_entry_point_view_model import EarlyAccessWidgetEntryPointViewModel
from gui.impl.gen import R
from gui.impl.lobby.early_access.early_access_window_events import showEarlyAccessQuestsView
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import IEarlyAccessController, IBootcampController

@dependency.replace_none_kwargs(ctrl=IEarlyAccessController)
def isEarlyAccessEntryPointAvailable(ctrl=None):
    return ctrl.isEnabled()


class EarlyAccessWidgetEntryPointView(ViewImpl):
    __slots__ = ()
    __earlyAccessCtrl = dependency.descriptor(IEarlyAccessController)
    __bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.early_access.EarlyAccessWidgetView(), flags=ViewFlags.VIEW, model=EarlyAccessWidgetEntryPointViewModel())
        super(EarlyAccessWidgetEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EarlyAccessWidgetEntryPointView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EarlyAccessWidgetEntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def _getEvents(self):
        return ((self.__earlyAccessCtrl.onQuestsUpdated, self.__updateModel), (self.__earlyAccessCtrl.onUpdated, self.__updateModel), (self.viewModel.onAction, showEarlyAccessQuestsView))

    def __updateModel(self, *_):
        with self.viewModel.transaction() as model:
            startProgressionTime, finishProgressionTime = self.__earlyAccessCtrl.getProgressionTimes()
            _, endSeasonDate = self.__earlyAccessCtrl.getSeasonInterval()
            state = self.__earlyAccessCtrl.getState()
            model.setStartTime(startProgressionTime)
            model.setEndTime(endSeasonDate if state == State.POSTPROGRESSION else finishProgressionTime)
            model.setCurrentTime(getServerUTCTime())
            model.setState(state.value)
