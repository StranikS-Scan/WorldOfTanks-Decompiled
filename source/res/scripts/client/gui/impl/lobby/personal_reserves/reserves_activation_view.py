# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/reserves_activation_view.py
import logging
from typing import TYPE_CHECKING
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings, Array, ViewEvent, Window, ViewModel
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.game_control import BoostersController
from gui.goodies.goodie_items import ClanReservePresenter
from gui.goodies.goodies_constants import BoosterCategory
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.common.personal_reserves.personal_reserves_shared_constants import PERSONAL_RESOURCE_ORDER, GOODIES_TYPE_TO_CLAN_BOOSTERS
from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import getPersonalBoosterModelDataByResourceType, addPersonalBoostersGroup, addBoosterModel, addEventGroup
from gui.impl.lobby.personal_reserves import boosterActivationFlow
from gui.impl.lobby.personal_reserves.personal_reserves_utils import boostersInClientUpdate
from gui.impl.gen import R
from gui.impl.gen.view_models.common.personal_reserves.booster_model import BoosterModel
from gui.impl.gen.view_models.common.personal_reserves.reserves_activation_view_model import ReservesActivationViewModel
from gui.impl.gen.view_models.common.personal_reserves.reserves_group_model import ReservesGroupModel, GroupCategory
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl
from gui.shared.ClanCache import g_clanCache
from gui.shared.event_dispatcher import showPersonalReservesIntro, showBoostersActivation, showHangar
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IBoostersController, IEpicBattleMetaGameController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
_logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from typing import Dict, List, Optional
    from gui.game_control.epic_meta_game_ctrl import EpicBattleMetaGameController
    from gui.goodies.goodies_cache import GoodiesCache
    from gui.shared.items_cache import ItemsCache
    from gui.wgcg.web_controller import WebController
    from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import BoosterModelData

class ReservesActivationView(ViewImpl):
    __slots__ = ()
    goodiesCache = dependency.descriptor(IGoodiesCache)
    boosters = dependency.descriptor(IBoostersController)
    epicBattleMetaGameController = dependency.descriptor(IEpicBattleMetaGameController)
    itemsCache = dependency.descriptor(IItemsCache)
    webController = dependency.descriptor(IWebController)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, layoutID=R.views.lobby.personal_reserves.ReservesActivationView()):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ReservesActivationViewModel()
        super(ReservesActivationView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ReservesActivationView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(ReservesActivationView, self)._initialize(*args, **kwargs)
        self.initListeners()

    def _onLoaded(self, *args, **kwargs):
        super(ReservesActivationView, self)._onLoaded(*args, **kwargs)
        self.soundManager.setState('STATE_hangar_place', 'STATE_hangar_place_personal_reserves')

    def initListeners(self):
        self.viewModel.onInformationClicked += self.onInformationClicked
        self.viewModel.onClose += self.onClose
        self.viewModel.onBoosterActivate += self.onBoosterActivate
        self.__epicController.onUpdated += self.__onEpicUpdate
        g_clientUpdateManager.addCurrencyCallback(Currency.CREDITS, self.__onCurrencyBalanceChanged)
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self.__onCurrencyBalanceChanged)
        ReservesActivationView.boosters.onBoosterChangeNotify += self.onBoosterChangeNotify
        g_playerEvents.onClientUpdated += self.onItemsCacheChanged

    def _onLoading(self):
        super(ReservesActivationView, self)._onLoading()
        self.fillViewModel()

    def _finalize(self):
        self.viewModel.onInformationClicked -= self.onInformationClicked
        self.viewModel.onClose -= self.onClose
        self.viewModel.onBoosterActivate -= self.onBoosterActivate
        self.__epicController.onUpdated -= self.__onEpicUpdate
        g_clientUpdateManager.removeObjectCallbacks(self)
        ReservesActivationView.boosters.onBoosterChangeNotify -= self.onBoosterChangeNotify
        g_playerEvents.onClientUpdated -= self.onItemsCacheChanged
        super(ReservesActivationView, self)._finalize()

    def getClanBoostersByType(self):
        activeBoosters = ReservesActivationView.goodiesCache.getClanReserves()
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
        boosterModelsByType = getPersonalBoosterModelDataByResourceType(ReservesActivationView.goodiesCache)
        with self.viewModel.transaction() as model:
            groupsArray = model.getReserveGroups()
            groupsArray.clear()
            for resourceType in PERSONAL_RESOURCE_ORDER:
                addPersonalBoostersGroup(resourceType, boosterModelsByType, groupsArray)

            addEventGroup(groupsArray, ReservesActivationView.goodiesCache)
            if g_clanCache.isInClan:
                self.addClanGroup(groupsArray)
            model.setGold(int(ReservesActivationView.itemsCache.items.stats.money.getSignValue(Currency.GOLD)))
            model.setCanActivateClanReserves(ReservesActivationView.webController.getAccountProfile().getMyClanPermissions().canActivateReserves())
            groupsArray.invalidate()

    def addClanGroup(self, clanArray):
        group = ReservesGroupModel()
        group.setCategory(GroupCategory.CLAN)
        boostersGroup = group.getReserves()
        for resourceType, booster in self.getClanBoostersByType().iteritems():
            addBoosterModel(boostersGroup, resourceType, BoosterCategory.CLAN, booster, booster.count)

        clanArray.addViewModel(group)

    def onItemsCacheChanged(self, diff, _):
        if boostersInClientUpdate(diff):
            self.fillViewModel()

    def onBoosterChangeNotify(self, *args, **kwargs):
        self.fillViewModel()

    def onInformationClicked(self, *args, **kwargs):
        showPersonalReservesIntro(callbackOnClose=showBoostersActivation)

    def onClose(self, *args, **kwargs):
        showHangar()
        self.destroyWindow()

    @args2params(int)
    def onBoosterActivate(self, boosterId):
        boosterActivationFlow(boosterId)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            window = self._createBackportTooltip(event)
            if window:
                window.load()
                return window
        return super(ReservesActivationView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.personal_reserves.ReservesDisabledTooltip():
            settings = ViewSettings(layoutID=R.views.common.personal_reserves.ReservesDisabledTooltip(), model=ViewModel())
            return ViewImpl(settings)
        return super(ReservesActivationView, self).createToolTipContent(event, contentID)

    def _createBackportTooltip(self, event):
        if not event.hasArgument('specialAlias'):
            _logger.warning('Requested backport tooltip but specialAlias is missing!')
            return None
        elif event.getArgument('boosterId', 0) <= 0:
            _logger.warning('Missing booster ID!')
            return None
        else:
            specialAlias = event.getArgument('specialAlias')
            boosterId = int(event.getArgument('boosterId'))
            if specialAlias == TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO:
                specialArgs = [boosterId]
                return BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=specialAlias, specialArgs=specialArgs), self.getParentWindow())
            _logger.warning('Requested unsupported backport tooltip alias: %s', specialAlias)
            return None

    def __onCurrencyBalanceChanged(self, _):
        self.fillViewModel()

    def __onEpicUpdate(self, diff, *_):
        if 'isEnabled' in diff:
            self.fillViewModel()
