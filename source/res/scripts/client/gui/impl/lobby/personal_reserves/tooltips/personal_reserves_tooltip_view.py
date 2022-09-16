# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/tooltips/personal_reserves_tooltip_view.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_reserves.reserves_entry_point_model import ReservesEntryPointModel
from gui.impl.lobby.personal_reserves.personal_reserves_utils import getActiveBoosters, addToReserveArrayByCategory, getTotalReadyReserves, getTotalLimitedReserves
from gui.impl.pub import ViewImpl
from gui.goodies.goodies_constants import BoosterCategory
from gui.shared.ClanCache import g_clanCache
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from gui.clans.clan_account_profile import ClanAccountProfile
    from gui.wgcg.web_controller import WebController
    from gui.goodies.goodies_cache import GoodiesCache

class PersonalReservesTooltipView(ViewImpl):
    _webCtrl = dependency.descriptor(IWebController)
    _goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.personal_reserves.PersonalReservesTooltip())
        settings.model = ReservesEntryPointModel()
        super(PersonalReservesTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PersonalReservesTooltipView, self).getViewModel()

    def _onLoading(self):
        with self.viewModel.transaction() as model:
            reservesArray = model.getReserves()
            reservesArray.clear()
            boosters = getActiveBoosters(cache=self._goodiesCache)
            for category in BoosterCategory:
                canAddEmpty = self._canAddEmptySection(category)
                addToReserveArrayByCategory(reservesArray, boosters, category, self._goodiesCache, canAddEmpty)

            reservesArray.invalidate()
            model.setIsDisabled(False)
            model.setTotalReserves(getTotalReadyReserves(cache=self._goodiesCache))
            model.setTotalLimitedReserves(getTotalLimitedReserves(cache=self._goodiesCache))
            model.setIsClanMember(g_clanCache.isInClan)

    def _getAccountProfile(self):
        return self._webCtrl.getAccountProfile()

    def _canAddEmptySection(self, category):
        return category == BoosterCategory.PERSONAL or category == BoosterCategory.CLAN and self._getAccountProfile().isInClan()
