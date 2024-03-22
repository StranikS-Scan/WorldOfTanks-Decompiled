# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/booster_tooltip.py
from typing import TYPE_CHECKING
from frameworks.wulf import ViewSettings
from gui.goodies.goodie_items import ClanReservePresenter, getFullNameForBoosterIcon
from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import fillBoosterModelWithData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_reserves.booster_tooltip_model import BoosterTooltipModel
from gui.impl.lobby.personal_reserves.personal_reserves_utils import getBoostersInGroup
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IBoostersController
from skeletons.gui.goodies import IGoodiesCache
if TYPE_CHECKING:
    from typing import Union, Any
    from gui.goodies import GoodiesCache
    from gui.goodies.goodie_items import Booster
    from gui.shared.tooltips.contexts import BoosterInfoContext, ClanReserveContext
    from gui.game_control.BoostersController import BoostersController
    BOOSTER_CONTEXT_TYPE = Union[BoosterInfoContext, ClanReserveContext]
    BOOSTER_TYPE = Union[Booster, ClanReservePresenter]

class BoosterTooltip(ViewImpl):
    goodiesCache = dependency.descriptor(IGoodiesCache)
    _boosters = dependency.descriptor(IBoostersController)
    __slots__ = ('boosterID', 'context')

    def __init__(self, boosterID, context):
        settings = ViewSettings(R.views.lobby.personal_reserves.BoosterTooltip())
        settings.model = BoosterTooltipModel()
        super(BoosterTooltip, self).__init__(settings)
        self.boosterID = boosterID
        self.context = context

    @property
    def viewModel(self):
        return super(BoosterTooltip, self).getViewModel()

    def _loadExpirableBoosters(self, booster):
        boosters = getBoostersInGroup(booster, self.goodiesCache)
        if boosters:
            booster = boosters[0]
        with self.viewModel.transaction() as model:
            fillBoosterModelWithData(model, booster)
            model.setIconId(getFullNameForBoosterIcon(booster.boosterType, isPremium=booster.getIsPremium(), isExpirable=False))
            if boosters:
                model.setInDepot(sum((inDepotBooster.count for inDepotBooster in boosters)))
                model.setInDepotExpirableAmount(sum((inDepotBooster.getExpiringAmount() for inDepotBooster in boosters)))

    def _loadBoosterDefaults(self, booster):
        with self.viewModel.transaction() as model:
            fillBoosterModelWithData(model, booster)

    def _onLoading(self):
        super(BoosterTooltip, self)._onLoading()
        self.loadBooster()

    def loadBooster(self):
        booster = self.context.buildItem(self.boosterID)
        if isinstance(booster, ClanReservePresenter):
            self._loadBoosterDefaults(booster)
        else:
            self._loadExpirableBoosters(booster)

    def _getEvents(self):
        return ((self._boosters.onPersonalReserveTick, self.onBoosterChangeNotify), (self._boosters.onClanReserveTick, self.onBoosterChangeNotify), (self._boosters.onBoostersDataUpdate, self.onBoosterChangeNotify))

    def onBoosterChangeNotify(self):
        self.loadBooster()
