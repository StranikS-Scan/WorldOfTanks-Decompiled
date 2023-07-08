# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/feature/fun_random_entry_point_view.py
import typing
from adisp import adisp_process
from frameworks.wulf import ViewFlags, ViewSettings
from fun_random.gui.feature.fun_constants import FunSubModesState
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasAnySubMode, avoidSubModesStates
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_entry_point_view_model import FunRandomEntryPointViewModel
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_entry_point_view_model import State
from fun_random.gui.impl.lobby.tooltips.fun_random_alert_tooltip_view import FunRandomAlertTooltipView
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.utils.scheduled_notifications import Notifiable, TimerNotifier
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController
if typing.TYPE_CHECKING:
    from frameworks.wulf import View, ViewEvent
_ENTRY_POINT_STATE_MAP = {FunSubModesState.BEFORE_SEASON: State.BEFORE,
 FunSubModesState.BETWEEN_SEASONS: State.BEFORE,
 FunSubModesState.NOT_AVAILABLE: State.NOTPRIMETIME,
 FunSubModesState.AVAILABLE: State.ACTIVE}

@dependency.replace_none_kwargs(funRandomCtrl=IFunRandomController)
def isFunRandomEntryPointAvailable(funRandomCtrl=None):
    return funRandomCtrl.subModesInfo.isEntryPointAvailable()


class FunRandomEntryPointView(ViewImpl, FunAssetPacksMixin, FunSubModesWatcher, Notifiable):

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(layoutID=R.views.fun_random.lobby.feature.FunRandomEntryPointView(), flags=flags, model=FunRandomEntryPointViewModel())
        super(FunRandomEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FunRandomEntryPointView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return FunRandomAlertTooltipView() if contentID == R.views.fun_random.lobby.tooltips.FunRandomAlertTooltipView() else super(FunRandomEntryPointView, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(FunRandomEntryPointView, self)._initialize(*args, **kwargs)
        self.addNotificator(TimerNotifier(self.__getTimer, self.__invalidateAll))
        self.startSubStatusListening(self.__invalidateAll, tickMethod=self.__invalidateAll)
        self.startSubSettingsListening(self.__invalidateAll)

    def _finalize(self):
        self.clearNotification()
        self.stopSubStatusListening(self.__invalidateAll, tickMethod=self.__invalidateAll)
        self.stopSubSettingsListening(self.__invalidateAll)
        super(FunRandomEntryPointView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(FunRandomEntryPointView, self)._onLoading(*args, **kwargs)
        self.__invalidate(self.getSubModesStatus())

    def _getEvents(self):
        return ((self.viewModel.onActionClick, self.__onSelectFunRandom),)

    @hasAnySubMode(defReturn=0)
    def __getTimer(self):
        if self.viewModel.getState() != State.NOTPRIMETIME:
            return 0
        notSetSubModes = [ sm for sm in self.getSubModes() if sm.isNotSet() ]
        if not notSetSubModes:
            return 0
        notSetTimer = self._funRandomCtrl.subModesInfo.getLeftTimeToPrimeTimesEnd(subModes=notSetSubModes)
        return notSetTimer + 1 if notSetTimer != 0 else notSetTimer

    @adisp_process
    def __onSelectFunRandom(self):
        yield self.selectFunRandomBattle()

    @avoidSubModesStates(states=FunSubModesState.HIDDEN_ENTRY_STATES, abortAction='destroy')
    def __invalidateAll(self, status, *_):
        self.__invalidate(status)

    def __invalidate(self, status):
        with self.viewModel.transaction() as model:
            model.setAssetsPointer(self.getModeAssetsPointer())
            model.setState(_ENTRY_POINT_STATE_MAP.get(status.state, State.AFTER))
            model.setStartTime(status.rightBorder)
            model.setLeftTime(status.primeDelta)
            model.setEndTime(status.rightBorder)
        self.startNotification()
