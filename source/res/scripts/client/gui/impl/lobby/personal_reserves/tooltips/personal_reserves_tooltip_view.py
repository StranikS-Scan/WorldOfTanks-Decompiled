# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/tooltips/personal_reserves_tooltip_view.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_reserves.reserves_entry_point_model import ReservesEntryPointModel
from gui.impl.lobby.personal_reserves.personal_reserves_utils import getActiveBoosters, addToReserveArrayByCategory, getTotalReadyReserves, getTotalLimitedReserves
from gui.impl.pub import ViewImpl
from gui.goodies.goodies_constants import BoosterCategory
from helpers import dependency
from skeletons.gui.game_control import IBoostersController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.web import IWebController
from uilogging.personal_reserves.logging_constants import PersonalReservesLogKeys, PersonalReservesLogTooltips
from uilogging.personal_reserves.loggers import PersonalReservesMetricsLogger
if typing.TYPE_CHECKING:
    from gui.wgcg.web_controller import WebController
    from gui.goodies.goodies_cache import GoodiesCache
    from gui.game_control.BoostersController import BoostersController

class PersonalReservesTooltipView(ViewImpl):
    __slots__ = ('_uiLogger',)
    _webCtrl = dependency.descriptor(IWebController)
    _goodiesCache = dependency.descriptor(IGoodiesCache)
    _boosters = dependency.descriptor(IBoostersController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.personal_reserves.PersonalReservesTooltip())
        settings.model = ReservesEntryPointModel()
        super(PersonalReservesTooltipView, self).__init__(settings)
        self._uiLogger = PersonalReservesMetricsLogger(parent=PersonalReservesLogKeys.LOBBY_HEADER, item=PersonalReservesLogTooltips.RESERVES_WIDGET_TOOLTIP)

    @property
    def viewModel(self):
        return super(PersonalReservesTooltipView, self).getViewModel()

    def _initialize(self):
        super(PersonalReservesTooltipView, self)._initialize()
        self._boosters.onGameModeStatusChange += self._update
        self._uiLogger.onViewInitialize()

    def _finalize(self):
        self._boosters.onGameModeStatusChange -= self._update
        self._uiLogger.onViewFinalize()
        super(PersonalReservesTooltipView, self)._finalize()

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
            model.setIsDisabled(not self._boosters.isGameModeSupported())
            model.setTotalReserves(getTotalReadyReserves(cache=self._goodiesCache))
            model.setTotalLimitedReserves(getTotalLimitedReserves(cache=self._goodiesCache))
            model.setIsClanMember(self._isInClan())

    def _isInClan(self):
        clanProfile = self._webCtrl.getAccountProfile()
        return bool(clanProfile and clanProfile.isInClan())

    def _canAddEmptySection(self, category):
        return category == BoosterCategory.PERSONAL or category == BoosterCategory.CLAN and self._isInClan()
