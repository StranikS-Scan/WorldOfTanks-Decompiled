# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/fun_random/fun_random_entry_point_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.fun_random.fun_random_entry_point_view_model import FunRandomEntryPointViewModel, State
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.periodic_battles.models import PeriodType
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from helpers import dependency, time_utils
from skeletons.gui.game_control import IFunRandomController

@dependency.replace_none_kwargs(funRandomCtrl=IFunRandomController)
def isFunRandomEntryPointAvailable(funRandomCtrl=None):
    return _isTimeSuitable() and funRandomCtrl.canGoToMode()


@dependency.replace_none_kwargs(funRandomCtrl=IFunRandomController)
def _isTimeSuitable(funRandomCtrl=None):
    periodInfo = funRandomCtrl.getPeriodInfo()
    return funRandomCtrl.isAvailable() and periodInfo.periodType not in (PeriodType.ALL_NOT_AVAILABLE_END, PeriodType.STANDALONE_NOT_AVAILABLE_END)


class FunRandomEntryPointView(ViewImpl):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.fun_random.FunRandomEntryPointView())
        settings.flags = flags
        settings.model = FunRandomEntryPointViewModel()
        super(FunRandomEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FunRandomEntryPointView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(FunRandomEntryPointView, self)._initialize(*args, **kwargs)
        self.__funRandomCtrl.onGameModeStatusTick += self.__update
        self.__funRandomCtrl.onGameModeStatusUpdated += self.__updateState
        self.viewModel.onActionClick += self.__onClick

    def _finalize(self):
        self.viewModel.onActionClick -= self.__onClick
        self.__funRandomCtrl.onGameModeStatusTick -= self.__update
        self.__funRandomCtrl.onGameModeStatusUpdated -= self.__updateState
        super(FunRandomEntryPointView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(FunRandomEntryPointView, self)._onLoading(*args, **kwargs)
        self.__update()

    def __onClick(self):
        self.__funRandomCtrl.selectFunRandomBattle()
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.FUN_RANDOM)

    def __updateState(self, _):
        self.__update()

    def __update(self):
        if not _isTimeSuitable():
            self.destroy()
            return
        with self.viewModel.transaction() as model:
            if not self.__funRandomCtrl.hasAvailablePrimeTimeServers():
                state = State.NOTPRIMETIME
                model.setLeftTime(self.__funRandomCtrl.getLeftTimeToPrimeTimesEnd() * time_utils.MS_IN_SECOND)
            else:
                state = State.ACTIVE
                periodInfo = self.__funRandomCtrl.getPeriodInfo()
                model.setEndTime(periodInfo.cycleBorderRight.timestamp)
            model.setState(state)
