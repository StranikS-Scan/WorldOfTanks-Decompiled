# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/battle_royale_entry_point.py
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_royale_entry_point_model import BattleRoyaleEntryPointModel, State
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.periodic_battles.models import PeriodType
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from gui.shared import event_dispatcher
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

@dependency.replace_none_kwargs(battleRoyaleController=IBattleRoyaleController)
def isBattleRoyaleEntryPointAvailable(battleRoyaleController=None):
    return battleRoyaleController.isActive()


class BattleRoyaleEntryPoint(ViewImpl):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.battle_royale.lobby.views.BattleRoyaleEntryPoint())
        settings.flags = flags
        settings.model = BattleRoyaleEntryPointModel()
        self.__isSingle = True
        super(BattleRoyaleEntryPoint, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleRoyaleEntryPoint, self).getViewModel()

    def setIsSingle(self, value):
        self.__isSingle = value
        self.__updateViewModel()

    def _initialize(self, *args, **kwargs):
        super(BattleRoyaleEntryPoint, self)._initialize(*args, **kwargs)
        self.viewModel.onClick += self.__onClick
        self.__battleRoyaleController.onEntryPointUpdated += self.__onUpdate

    def _finalize(self):
        self.viewModel.onClick -= self.__onClick
        self.__battleRoyaleController.onEntryPointUpdated -= self.__onUpdate
        super(BattleRoyaleEntryPoint, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(BattleRoyaleEntryPoint, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def __updateViewModel(self):
        if isBattleRoyaleEntryPointAvailable():
            with self.viewModel.transaction() as tx:
                tx.setIsSingle(self.__isSingle)
                state, actualTime = self.__getPeriodStateAndActualTime()
                tx.setState(state)
                tx.setTimestamp(actualTime or 0)
        else:
            self.destroy()

    def __onUpdate(self, *_):
        self.__updateViewModel()

    def __getPeriodStateAndActualTime(self):
        periodInfo = self.__battleRoyaleController.getPeriodInfo()
        status = State.DISABLED
        actualTime = None
        if periodInfo.periodType in (PeriodType.BEFORE_SEASON, PeriodType.BEFORE_CYCLE, PeriodType.BETWEEN_SEASONS):
            actualTime = periodInfo.cycleBorderRight.timestamp
        elif periodInfo.periodType in (PeriodType.STANDALONE_NOT_AVAILABLE_END, PeriodType.ALL_NOT_AVAILABLE_END, PeriodType.NOT_AVAILABLE_END):
            status = State.POSTEVENT
            actualTime = periodInfo.cycleBorderRight.timestamp
        elif periodInfo.periodType in (PeriodType.ALL_NOT_AVAILABLE, PeriodType.STANDALONE_NOT_AVAILABLE):
            actualTime = periodInfo.primeDelta
        else:
            status = State.ACTIVE
            actualTime = periodInfo.cycleBorderRight.timestamp
        return (status, actualTime)

    def __onClick(self):
        brController = self.__battleRoyaleController
        if not brController.isInPrimeTime() and brController.hasAvailablePrimeTimeServers():
            event_dispatcher.showBattleRoyalePrimeTimeWindow()
        else:
            brController.selectRoyaleBattle()
            selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.BATTLE_ROYALE)
