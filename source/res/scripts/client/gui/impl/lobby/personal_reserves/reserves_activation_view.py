# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/reserves_activation_view.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings, Array, ViewEvent, ViewModel
from goodies.goodie_constants import BoosterCategory
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPersonalReservesUrl
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.game_control import BoostersController
from gui.goodies.goodie_items import ClanReservePresenter
from gui.impl.common.personal_reserves.personal_reserves_shared_constants import PERSONAL_RESOURCE_ORDER, GOODIES_TYPE_TO_CLAN_BOOSTERS
from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import getPersonalBoosterModelDataByResourceType, addPersonalBoostersGroup, addBoosterModel, addEventGroup
from gui.impl.gen import R
from gui.impl.gen.view_models.common.personal_reserves.booster_model import BoosterModel
from gui.impl.gen.view_models.common.personal_reserves.reserves_activation_view_model import ReservesActivationViewModel
from gui.impl.gen.view_models.common.personal_reserves.reserves_group_model import ReservesGroupModel, GroupCategory
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.personal_reserves import boosterActivationFlow
from gui.impl.lobby.personal_reserves.booster_tooltip import BoosterTooltip
from gui.impl.lobby.personal_reserves.personal_reserves_utils import getNearestExpirationTimeAndCountForToday
from gui.impl.lobby.personal_reserves.reserves_constants import PERSONAL_RESERVES_SOUND_SPACE
from gui.impl.pub import ViewImpl
from gui.server_events.settings import getPersonalReservesSettings
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showPersonalReservesInfomationScreen, showStorage, showPersonalReservesIntro
from gui.shared.event_dispatcher import showShop
from gui.shared.money import Currency
from gui.shared.tooltips import contexts
from helpers import dependency
from skeletons.gui.game_control import IBoostersController, IEpicBattleMetaGameController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
from typing import TYPE_CHECKING
_logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from typing import Dict, List, Optional
    from gui.game_control.epic_meta_game_ctrl import EpicBattleMetaGameController
    from gui.goodies.goodies_cache import GoodiesCache
    from gui.shared.items_cache import ItemsCache
    from gui.wgcg.web_controller import WebController
    from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import BoosterModelData

class ReservesActivationView(ViewImpl, EventSystemEntity):
    _COMMON_SOUND_SPACE = PERSONAL_RESERVES_SOUND_SPACE
    _goodiesCache = dependency.descriptor(IGoodiesCache)
    _boosters = dependency.descriptor(IBoostersController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _webController = dependency.descriptor(IWebController)
    _epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, layoutID=R.views.lobby.personal_reserves.ReservesActivationView()):
        settings = ViewSettings(layoutID, flags=ViewFlags.LOBBY_TOP_SUB_VIEW, model=ReservesActivationViewModel())
        super(ReservesActivationView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ReservesActivationView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(ReservesActivationView, self)._initialize(*args, **kwargs)
        if not getPersonalReservesSettings().isIntroPageShown and self._boosters.getExpirableBoosters():
            showPersonalReservesIntro()

    def _onLoading(self):
        super(ReservesActivationView, self)._onLoading()
        self.fillViewModel()

    def getClanBoostersByType(self):
        activeBoosters = self._goodiesCache.getClanReserves()
        clanBoostersByType = {}
        for resourceType, fortOrderTypeIds in GOODIES_TYPE_TO_CLAN_BOOSTERS.iteritems():
            for fortOrderTypeId in fortOrderTypeIds:
                activeClanBooster = activeBoosters.get(fortOrderTypeId)
                if activeClanBooster:
                    clanBoostersByType[resourceType] = activeClanBooster
                    break
            else:
                clanBoostersByType[resourceType] = ClanReservePresenter(fortOrderTypeIds[0], 0, {}, 0)

        return clanBoostersByType

    def fillViewModel(self):
        boosterModelsByType = getPersonalBoosterModelDataByResourceType(self._goodiesCache, self._boosters)
        with self.viewModel.transaction() as model:
            groupsArray = model.getReserveGroups()
            groupsArray.clear()
            for resourceType in PERSONAL_RESOURCE_ORDER:
                addPersonalBoostersGroup(resourceType, boosterModelsByType, groupsArray)

            addEventGroup(groupsArray, self._goodiesCache)
            enabledBoosters = self._boosters.getExpirableBoosters().values()
            nextExpiryTime, counter = getNearestExpirationTimeAndCountForToday(enabledBoosters)
            model.setNextExpirationTime(nextExpiryTime)
            model.setNextExpirationAmount(counter)
            if self._webController.getAccountProfile().isInClan():
                self.addClanGroup(groupsArray)
            model.setGold(int(self._itemsCache.items.stats.money.getSignValue(Currency.GOLD)))
            model.setCanActivateClanReserves(self._webController.getAccountProfile().getMyClanPermissions().canActivateReserves())
            groupsArray.invalidate()

    def addClanGroup(self, groupsArray):
        group = ReservesGroupModel()
        group.setCategory(GroupCategory.CLAN)
        boostersGroup = group.getReserves()
        for resourceType, booster in self.getClanBoostersByType().iteritems():
            addBoosterModel(boostersGroup, resourceType, BoosterCategory.CLAN, booster, booster.count)

        groupsArray.addViewModel(group)

    def onBoostersDataUpdate(self):
        self.fillViewModel()

    def onPersonalReserveTick(self):
        self.fillViewModel()

    def onInformationClicked(self, *args, **kwargs):
        showPersonalReservesInfomationScreen()

    def onClose(self, *args, **kwargs):
        self.destroyWindow()

    @args2params(int)
    def onBoosterActivate(self, boosterId):
        boosterActivationFlow(boosterId)

    @args2params(int)
    def onCardHover(self, boosterId):
        if not self._boosters.shouldShowOnBoardingCardHint(boosterId):
            return
        self._boosters.setCardHintSeenFor(boosterId)
        self.fillViewModel()

    def onNavigateToStore(self):
        showShop(getBuyPersonalReservesUrl())
        self.destroyWindow()

    def onNavigateToDepot(self):
        showStorage(STORAGE_CONSTANTS.PERSONAL_RESERVES)
        self.destroyWindow()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.personal_reserves.ReservesDisabledTooltip():
            settings = ViewSettings(layoutID=R.views.common.personal_reserves.ReservesDisabledTooltip(), model=ViewModel())
            return ViewImpl(settings)
        else:
            if contentID == R.views.lobby.personal_reserves.BoosterTooltip():
                boosterId = int(event.getArgument('boosterId', 0))
                specialAlias = event.getArgument('specialAlias')
                if not specialAlias:
                    _logger.warning('Requested backport tooltip but specialAlias is missing!')
                    return None
                if not boosterId:
                    _logger.warning('Cannot open tooltip. Missing boosterId in tooltip params!')
                    return None
                if specialAlias == TOOLTIPS_CONSTANTS.CLAN_RESERVE_INFO:
                    hasClanReserve = bool(self._goodiesCache.getClanReserves().get(boosterId))
                    if not hasClanReserve:
                        _logger.warning('Cannot open clan tooltip. Such clan booster does not exists!')
                        return None
                    return BoosterTooltip(boosterId, contexts.ClanReserveContext())
                if specialAlias == TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO:
                    return BoosterTooltip(boosterId, contexts.BoosterInfoContext())
            return super(ReservesActivationView, self).createToolTipContent(event, contentID)

    def _getListeners(self):
        return ((events.LobbyHeaderMenuEvent.MENU_CLICK, self.__onHeaderMenuClick, EVENT_BUS_SCOPE.LOBBY),)

    def _getCallbacks(self):
        return ((Currency.CREDITS, self.__onCurrencyBalanceChanged), (Currency.GOLD, self.__onCurrencyBalanceChanged))

    def _getEvents(self):
        return ((self._epicController.onUpdated, self.__onEpicUpdate),
         (self._boosters.onPersonalReserveTick, self.onPersonalReserveTick),
         (self._boosters.onBoostersDataUpdate, self.onBoostersDataUpdate),
         (self.viewModel.onInformationClicked, self.onInformationClicked),
         (self.viewModel.onClose, self.onClose),
         (self.viewModel.onBoosterActivate, self.onBoosterActivate),
         (self.viewModel.onNavigateToStore, self.onNavigateToStore),
         (self.viewModel.onNavigateToDepot, self.onNavigateToDepot),
         (self.viewModel.onCardHover, self.onCardHover))

    def __onHeaderMenuClick(self, event):
        self.destroyWindow()

    def __onCurrencyBalanceChanged(self, _):
        self.fillViewModel()

    def __onEpicUpdate(self, diff, *_):
        if 'isEnabled' in diff:
            self.fillViewModel()
