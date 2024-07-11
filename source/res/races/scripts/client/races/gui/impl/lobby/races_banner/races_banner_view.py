# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/lobby/races_banner/races_banner_view.py
from races.gui.impl.gen.view_models.views.lobby.races_banner_view.races_banner_view_model import RacesBannerViewModel, State
from skeletons.gui.game_control import IRacesBattleController
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.utils.scheduled_notifications import Notifiable
from helpers import dependency, time_utils
from shared_utils import nextTick
from races.gui.impl.lobby.races_banner.races_banner_inactive_tooltip import RacesBannerInactiveTooltip

@dependency.replace_none_kwargs(racesCtrl=IRacesBattleController)
def isRacesBannerAvailable(racesCtrl=None):
    return racesCtrl.isEnabled


class RacesBannerView(ViewImpl, Notifiable):
    __END_NOTIFICATIONS_PERIOD_LENGTH = time_utils.ONE_DAY
    __racesCtrl = dependency.descriptor(IRacesBattleController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(layoutID=R.views.races.lobby.RacesBannerView(), flags=flags, model=RacesBannerViewModel())
        super(RacesBannerView, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        return RacesBannerInactiveTooltip() if contentID == R.views.races.lobby.tooltips.RacesBannerInactiveTooltipView() else super(RacesBannerView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(RacesBannerView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RacesBannerView, self)._onLoading(*args, **kwargs)
        self.__updateState()

    def _getEvents(self):
        return ((self.viewModel.onOpenRacesLobby, self.__onOpenRacesLobby),
         (self.__racesCtrl.onPrimeTimeStatusUpdated, self.__onStatusUpdated),
         (self.__racesCtrl.onStatusTick, self.__onStatusTick),
         (self.__racesCtrl.onRacesConfigChanged, self.__onConfigChanged))

    def __onStatusUpdated(self, _):
        self.__updateState()

    def __onStatusTick(self):
        self.__updateState()

    def __onConfigChanged(self):
        self.__updateState()

    def __updateState(self):
        if isRacesBannerAvailable():
            with self.viewModel.transaction() as tx:
                state, endTime, timeLeft = self.__getPeriodStateAndActualTime()
                tx.setState(state)
                tx.setEndTime(endTime or 0)
                tx.setTimeLeft(timeLeft or 0)
        else:
            nextTick(self.destroy)()

    def __getPeriodStateAndActualTime(self):
        if self.__racesCtrl.isFrozen() or not self.__racesCtrl.isBattleAvailable():
            return (State.DISABLED, 0, 0)
        periodInfo = self.__racesCtrl.getPeriodInfo()
        timeLeft = self.__racesCtrl.getEventEndTimestamp() - periodInfo.now
        return (State.ACTIVE, self.__racesCtrl.getEventEndTimestamp(), timeLeft)

    def __onOpenRacesLobby(self):
        self.__racesCtrl.selectRaces()
