# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/personal_reserves_widget.py
import logging
import typing
import Event
from frameworks.wulf import ViewSettings, ViewFlags
from goodies.goodie_constants import BoosterCategory
from gui.impl.gen import R
from gui.impl.gen.view_models.common.personal_reserves.booster_model import BoosterModel
from gui.impl.gen.view_models.views.lobby.personal_reserves.reserves_entry_point_model import ReservesEntryPointModel
from gui.impl.lobby.personal_reserves.personal_reserves_utils import getActiveBoosters, getTotalReadyReserves, getTotalLimitedReserves, addDisabledCategories, getNearestExpiryTimeForToday
from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import addToReserveArrayByCategory
from gui.impl.pub import ViewImpl
from helpers import dependency, time_utils
from skeletons.gui.game_control import IBoostersController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from frameworks.wulf.view.array import Array
    from gui.shared.items_cache import ItemsCache
    from gui.goodies.goodies_cache import GoodiesCache
    from gui.game_control.BoostersController import BoostersController
    from gui.wgcg.web_controller import WebController
_logger = logging.getLogger(__name__)

class PersonalReservesWidget(ViewImpl):
    _boosters = dependency.descriptor(IBoostersController)
    _goodiesCache = dependency.descriptor(IGoodiesCache)
    _itemsCache = dependency.descriptor(IItemsCache)
    __webCtrl = dependency.descriptor(IWebController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.personal_reserves.PersonalReservesWidget())
        settings.flags = ViewFlags.VIEW
        settings.model = ReservesEntryPointModel()
        super(PersonalReservesWidget, self).__init__(settings)
        self._hasActiveBoosters = False
        self.onUpdate = Event.Event()

    @property
    def viewModel(self):
        return super(PersonalReservesWidget, self).getViewModel()

    @property
    def hasActiveBoosters(self):
        return self._hasActiveBoosters

    @property
    def activeBoostersCount(self):
        return len(self.viewModel.getReserves())

    def _getCallbacks(self):
        return (('stats.clanInfo', self._onClanInfoChanged),)

    def _getEvents(self):
        return ((self._boosters.onPersonalReserveTick, self._update),
         (self._boosters.onClanReserveTick, self._updateClanReserves),
         (self._boosters.onGameModeStatusChange, self._update),
         (self._boosters.onBoostersDataUpdate, self._update))

    def _finalize(self):
        self.onUpdate.clear()
        super(PersonalReservesWidget, self)._finalize()

    def _onLoading(self):
        super(PersonalReservesWidget, self)._onLoading()
        self._update()

    def _fillViewModel(self, model):
        reservesArray = model.getReserves()
        reservesArray.clear()
        activeBoosters = getActiveBoosters(goodiesCache=self._goodiesCache, webController=self.__webCtrl)
        self._hasActiveBoosters = active = bool(activeBoosters)
        if active:
            for category in BoosterCategory:
                addToReserveArrayByCategory(reservesArray, activeBoosters, category, self._goodiesCache)

        reservesArray.invalidate()
        addDisabledCategories(model.getDisabledCategories(), self._boosters)
        model.setTotalReserves(getTotalReadyReserves(cache=self._goodiesCache))
        model.setTotalLimitedReserves(getTotalLimitedReserves(cache=self._goodiesCache))
        closestExpiration = getNearestExpiryTimeForToday(cache=self._goodiesCache)
        model.setExpiringReserveWillExpireSoon(time_utils.getServerUTCTime() + 86400 > closestExpiration > 0)

    def _update(self):
        self._hasActiveBoosters = False
        with self.viewModel.transaction() as model:
            self._fillViewModel(model)
        self.onUpdate()

    def _onClanInfoChanged(self, _):
        clanProfile = self.__webCtrl.getAccountProfile()
        if clanProfile and clanProfile.isInClan():
            self._update()

    def _updateClanReserves(self):
        self._update()
