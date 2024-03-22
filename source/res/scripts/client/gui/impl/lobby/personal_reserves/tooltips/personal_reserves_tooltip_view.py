# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/tooltips/personal_reserves_tooltip_view.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_reserves.reserves_entry_point_model import ReservesEntryPointModel
from gui.impl.lobby.personal_reserves.personal_reserves_utils import getActiveBoosters, getTotalReadyReserves, getTotalLimitedReserves, addDisabledCategories
from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import addToReserveArrayByCategory
from gui.impl.pub import ViewImpl
from goodies.goodie_constants import BoosterCategory
from helpers import dependency
from skeletons.gui.game_control import IBoostersController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    import Event
    from typing import Tuple, Callable, Optional
    from gui.wgcg.web_controller import WebController
    from gui.goodies.goodies_cache import GoodiesCache
    from gui.game_control.BoostersController import BoostersController

class PersonalReservesTooltipView(ViewImpl):
    _webCtrl = dependency.descriptor(IWebController)
    _goodiesCache = dependency.descriptor(IGoodiesCache)
    _boosters = dependency.descriptor(IBoostersController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.personal_reserves.PersonalReservesTooltip())
        settings.model = ReservesEntryPointModel()
        super(PersonalReservesTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PersonalReservesTooltipView, self).getViewModel()

    def _getEvents(self):
        return ((self._boosters.onGameModeStatusChange, self._update), (self._boosters.onBoostersDataUpdate, self._update))

    def _onLoading(self):
        self._update()

    def _update(self):
        with self.viewModel.transaction() as model:
            reservesArray = model.getReserves()
            reservesArray.clear()
            boosters = getActiveBoosters(goodiesCache=self._goodiesCache, webController=self._webCtrl)
            for category in BoosterCategory:
                canAddEmpty = self._canAddEmptySection(category)
                addToReserveArrayByCategory(reservesArray, boosters, category, self._goodiesCache, canAddEmpty)

            reservesArray.invalidate()
            addDisabledCategories(model.getDisabledCategories(), self._boosters)
            model.setTotalReserves(getTotalReadyReserves(cache=self._goodiesCache))
            model.setTotalLimitedReserves(getTotalLimitedReserves(cache=self._goodiesCache))
            model.setIsClanMember(self._isInClan())

    def _isInClan(self):
        clanProfile = self._webCtrl.getAccountProfile()
        return bool(clanProfile and clanProfile.isInClan())

    def _canAddEmptySection(self, category):
        return category == BoosterCategory.PERSONAL or category == BoosterCategory.CLAN and self._isInClan()
