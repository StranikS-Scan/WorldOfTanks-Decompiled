# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/lobby/banner_entry_point/cosmic_banner_entry_point.py
from cosmic_event.gui.impl.gen.view_models.views.lobby.banner_entry_point.cosmic_banner_entry_point_model import CosmicBannerEntryPointModel, State
from cosmic_event.skeletons.battle_controller import ICosmicEventBattleController
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.utils.scheduled_notifications import Notifiable
from helpers import dependency, time_utils
from shared_utils import nextTick

@dependency.replace_none_kwargs(cosmicCtrl=ICosmicEventBattleController)
def isCosmicBannerEntryPointAvailable(cosmicCtrl=None):
    return cosmicCtrl.isEnabled


class CosmicBannerEntryPointView(ViewImpl, Notifiable):
    __END_NOTIFICATIONS_PERIOD_LENGTH = time_utils.ONE_DAY
    __cosmicController = dependency.descriptor(ICosmicEventBattleController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(layoutID=R.views.cosmic_event.lobby.banner_entry_point.CosmicBannerEntryPoint(), flags=flags, model=CosmicBannerEntryPointModel())
        super(CosmicBannerEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CosmicBannerEntryPointView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(CosmicBannerEntryPointView, self)._initialize(*args, **kwargs)
        self.viewModel.onOpen += self.__onOpen
        self.__cosmicController.onPrimeTimeStatusUpdated += self.__onStatusUpdated
        self.__cosmicController.onStatusTick += self.__onStatusTick
        self.__cosmicController.onCosmicConfigChanged += self.__onConfigChanged

    def _finalize(self):
        self.viewModel.onOpen -= self.__onOpen
        self.__cosmicController.onPrimeTimeStatusUpdated -= self.__onStatusUpdated
        self.__cosmicController.onStatusTick -= self.__onStatusTick
        self.__cosmicController.onCosmicConfigChanged -= self.__onConfigChanged
        super(CosmicBannerEntryPointView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(CosmicBannerEntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateState()

    def __onStatusUpdated(self, _):
        self.__updateState()

    def __onStatusTick(self):
        self.__updateState()

    def __onConfigChanged(self):
        self.__updateState()

    def __updateState(self):
        if isCosmicBannerEntryPointAvailable():
            with self.viewModel.transaction() as tx:
                state, actualTime = self.__getPeriodStateAndActualTime()
                tx.setState(state)
                tx.setTimestamp(actualTime or 0)
        else:
            nextTick(self.destroy)()

    def __getPeriodStateAndActualTime(self):
        if self.__cosmicController.isFrozen() or not self.__cosmicController.isBattleAvailable():
            return (State.DISABLED, 0)
        periodInfo = self.__cosmicController.getPeriodInfo()
        endTimeDelta = periodInfo.cycleBorderRight.delta(periodInfo.now)
        return (State.ACTIVE, endTimeDelta)

    def __onOpen(self):
        self.__cosmicController.switchPrb()
