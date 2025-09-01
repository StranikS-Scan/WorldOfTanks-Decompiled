# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/reserves_entry_point_presenter.py
from __future__ import absolute_import
import logging
import typing
from goodies.goodie_constants import BoosterCategory
from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import addToReserveArrayByCategory
from gui.impl.gen import R
from gui.impl.gen.view_models.common.personal_reserves.booster_model import BoosterModel
from gui.impl.gen.view_models.views.lobby.personal_reserves.reserves_entry_point_model import ReservesEntryPointModel
from gui.impl.lobby.personal_reserves.personal_reserves_utils import getActiveBoosters, addDisabledCategories, getTotalReadyReserves, getTotalLimitedReserves, getNearestExpiryTimeForToday
from gui.impl.lobby.personal_reserves.tooltips.personal_reserves_tooltip_view import PersonalReservesTooltipView
from gui.impl.pub.view_component import ViewComponent
from gui.shared.event_dispatcher import showBoostersActivation
from helpers import dependency, time_utils
from skeletons.gui.game_control import IBoostersController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from frameworks.wulf.view.array import Array
    from gui.goodies.goodies_cache import GoodiesCache
    from gui.game_control.BoostersController import BoostersController
    from gui.wgcg.web_controller import WebController
    from frameworks.wulf.view.view import View, ViewEvent
_logger = logging.getLogger(__name__)

class ReservesEntryPointPresenter(ViewComponent[ReservesEntryPointModel]):
    __boosters = dependency.descriptor(IBoostersController)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __webCtrl = dependency.descriptor(IWebController)

    def __init__(self):
        super(ReservesEntryPointPresenter, self).__init__(model=ReservesEntryPointModel)

    @property
    def viewModel(self):
        return super(ReservesEntryPointPresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ReservesEntryPointPresenter, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def _getEvents(self):
        return ((self.__boosters.onPersonalReserveTick, self.__updateModel),
         (self.__boosters.onClanReserveTick, self.__updateClanReserves),
         (self.__boosters.onGameModeStatusChange, self.__updateModel),
         (self.__boosters.onBoostersDataUpdate, self.__updateModel),
         (self.viewModel.openBoosterNavigation, self.__openBoosterNavigation))

    def __updateClanReserves(self):
        self.__updateModel()

    def createToolTipContent(self, event, contentID):
        return PersonalReservesTooltipView() if contentID == R.views.lobby.personal_reserves.PersonalReservesTooltip() else super(ReservesEntryPointPresenter, self).createToolTipContent(event, contentID)

    def __updateModel(self):
        self._hasActiveBoosters = False
        with self.viewModel.transaction() as model:
            reservesArray = model.getReserves()
            reservesArray.clear()
            activeBoosters = getActiveBoosters(goodiesCache=self.__goodiesCache, webController=self.__webCtrl)
            self._hasActiveBoosters = active = bool(activeBoosters)
            if active:
                for category in BoosterCategory:
                    addToReserveArrayByCategory(reservesArray, activeBoosters, category, self.__goodiesCache)

            reservesArray.invalidate()
            addDisabledCategories(model.getDisabledCategories(), self.__boosters)
            model.setTotalReserves(getTotalReadyReserves(cache=self.__goodiesCache))
            model.setTotalLimitedReserves(getTotalLimitedReserves(cache=self.__goodiesCache))
            closestExpiration = getNearestExpiryTimeForToday(cache=self.__goodiesCache)
            model.setExpiringReserveWillExpireSoon(time_utils.getServerUTCTime() + time_utils.ONE_DAY > closestExpiration > 0)

    def __openBoosterNavigation(self):
        showBoostersActivation()
