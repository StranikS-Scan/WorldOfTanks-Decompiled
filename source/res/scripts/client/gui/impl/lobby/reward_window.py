# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/reward_window.py
import logging
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import WindowFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import PackRentVehiclesAwardComposer, AnniversaryAwardComposer, CurtailingAwardsComposer, RawLabelBonusComposer
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getMissionInfoData
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPremiumUrl
from gui.Scaleform.framework import WindowLayer
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.BARRACKS_CONSTANTS import BARRACKS_CONSTANTS
from gui.app_loader import sf_lobby
from gui.impl.backport import TooltipData, BackportTooltipWindow
from gui.impl.gen.view_models.windows.loot_box_reward_window_content_model import LootBoxRewardWindowContentModel
from gui.impl.pub import ViewImpl, WindowImpl, WindowView
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.reward_renderer_model import RewardRendererModel
from gui.impl.gen.view_models.windows.piggy_bank_reward_window_content_model import PiggyBankRewardWindowContentModel
from gui.impl.gen.view_models.windows.reward_window_content_model import RewardWindowContentModel
from gui.prb_control import prbDispatcherProperty
from gui.server_events.awards_formatters import getPackRentVehiclesAwardPacker, getAnniversaryPacker, getDefaultAwardFormatter
from gui.server_events.bonuses import getTutorialBonuses, CreditsBonus, getNonQuestBonuses
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showShop, showLootBoxEntry
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from constants import OFFER_TOKEN_PREFIX
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.game_control import IFestivityController
from gui.shared.event_dispatcher import showOfferGiftsWindow, showClanQuestWindow
_logger = logging.getLogger(__name__)
BASE_EVENT_NAME = 'base'
_ADDITIONAL_AWARDS_COUNT = 5

class BaseRewardWindowContent(ViewImpl):
    __slots__ = ('__items', '_eventName')
    _BONUSES_ORDER = ('vehicles',
     'premium',
     Currency.CRYSTAL,
     Currency.GOLD,
     'freeXP',
     'freeXPFactor',
     Currency.CREDITS,
     'creditsFactor',
     'tankmen',
     'items',
     'slots',
     'berths',
     'dossier',
     'customizations',
     'tokens',
     'goodies',
     Currency.EVENT_COIN,
     Currency.BPCOIN)

    def __init__(self, settings, ctx=None):
        super(BaseRewardWindowContent, self).__init__(settings)
        self.__items = {}
        if ctx is not None:
            self._eventName = ctx.get('eventName', BASE_EVENT_NAME)
        else:
            self._eventName = BASE_EVENT_NAME
        return

    def handleNextButton(self):
        pass

    def handleGoToButton(self):
        pass

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = BackportTooltipWindow(self.__items[tooltipId], self.getParentWindow()) if tooltipId is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(BaseRewardWindowContent, self).createToolTip(event)

    def _keySortOrder(self, bonus):
        return self._BONUSES_ORDER.index(bonus.getName()) if bonus.getName() in self._BONUSES_ORDER else len(self._BONUSES_ORDER)

    def _initialize(self, *args, **kwargs):
        super(BaseRewardWindowContent, self)._initialize(*args, **kwargs)
        self.getViewModel().setEventName(self._eventName)
        self._initRewardsList()

    def _getBonuses(self):
        return []

    def _getAwardComposer(self):
        return CurtailingAwardsComposer(_ADDITIONAL_AWARDS_COUNT, getDefaultAwardFormatter())

    def _getRewardRendererModelCls(self):
        return RewardRendererModel

    def _initRewardsList(self):
        with self.getViewModel().transaction() as tx:
            rewardsList = tx.rewardsList.getItems()
            bonuses = self._getBonuses()
            bonuses.sort(key=self._keySortOrder)
            formatter = self._getAwardComposer()
            for index, bonus in enumerate(formatter.getFormattedBonuses(bonuses)):
                rendererModel = self._getRewardRendererModelCls()()
                with rendererModel.transaction() as rewardTx:
                    rewardTx.setIcon(bonus.get('imgSource', ''))
                    rewardTx.setLabelStr(bonus.get('label', '') or '')
                    rewardTx.setTooltipId(index)
                    rewardTx.setHighlightType(bonus.get('highlightIcon', '') or '')
                    rewardTx.setOverlayType(bonus.get('overlayIcon', '') or '')
                    rewardTx.setHasCompensation(bonus.get('hasCompensation', False) or False)
                    rewardTx.setLabelAlign(bonus.get('align', 'center') or 'center')
                rewardsList.addViewModel(rendererModel)
                self.__items[index] = TooltipData(tooltip=bonus.get('tooltip', None), isSpecial=bonus.get('isSpecial', False), specialAlias=bonus.get('specialAlias', ''), specialArgs=bonus.get('specialArgs', None))

            tx.setShowRewards(bool(self.__items))
        return


class PiggyBankRewardWindowContent(BaseRewardWindowContent):
    __slots__ = ('_credits', '_isPremActive')

    def __init__(self, settings, ctx=None):
        super(PiggyBankRewardWindowContent, self).__init__(settings, ctx)
        if ctx is not None:
            self._isPremActive = ctx.get('isPremActive', False)
            self._credits = ctx.get('credits', 0)
        else:
            self._isPremActive = False
            self._credits = 0
        return

    def _initialize(self, *args, **kwargs):
        super(PiggyBankRewardWindowContent, self)._initialize(*args, **kwargs)
        self.getViewModel().onHyperLinkClicked += self.onHyperLinkClicked
        self.getViewModel().setShowDescription(not self._isPremActive)

    def _finalize(self):
        super(PiggyBankRewardWindowContent, self)._finalize()
        self.getViewModel().onHyperLinkClicked -= self.onHyperLinkClicked

    def _getBonuses(self):
        return [CreditsBonus('credits', self._credits)]

    def handleNextButton(self):
        self.getParentWindow().destroy()

    def onHyperLinkClicked(self):
        showShop(getBuyPremiumUrl())

    def _getAwardComposer(self):
        return RawLabelBonusComposer(getDefaultAwardFormatter())


class QuestRewardWindowContent(BaseRewardWindowContent):
    __slots__ = ('_quest', '_vehicles')

    def __init__(self, settings, ctx=None):
        super(QuestRewardWindowContent, self).__init__(settings, ctx)
        if ctx is not None:
            self._quest = ctx.get('quest', None)
            self._vehicles = ctx.get('bonusVehicles', {})
        else:
            self._quest = None
            self._vehicles = {}
        return

    def _getBonuses(self):
        if self._quest is not None:
            allBonuses = getMissionInfoData(self._quest).getSubstituteBonuses()
            bonuses = [ bonus for bonus in allBonuses if bonus.getName() != 'vehicles' ]
            vehBonus = getTutorialBonuses('vehicles', self._vehicles)
            bonuses.extend(vehBonus)
            return bonuses
        else:
            return []

    def _getAwardComposer(self):
        return PackRentVehiclesAwardComposer(_ADDITIONAL_AWARDS_COUNT, getPackRentVehiclesAwardPacker())

    def _finalize(self):
        super(QuestRewardWindowContent, self)._finalize()
        self._quest = None
        return


class TwitchRewardWindowContent(QuestRewardWindowContent):
    __slots__ = ()
    _offersProvider = dependency.descriptor(IOffersDataProvider)
    _BONUSES_ORDER = ('dossier',
     'customizations',
     'premium_plus',
     Currency.GOLD,
     'vehicles',
     'items',
     'crewBooks')

    def handleNextButton(self):
        bonuses = self._quest.getBonuses('tokens')
        hasCommander = False
        offerID = None
        for bonus in bonuses:
            for tID in bonus.getTokens():
                if getRecruitInfo(tID) is not None:
                    hasCommander = True
                    break
                if tID.startswith(OFFER_TOKEN_PREFIX):
                    for offer in self._offersProvider.getAvailableOffers(onlyVisible=True):
                        if offer.token == tID:
                            offerID = offer.id

        if hasCommander:
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_BARRACKS), ctx={'location': BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED}), scope=EVENT_BUS_SCOPE.LOBBY)
        elif offerID is not None:
            showOfferGiftsWindow(offerID)
        return


class RewardWindowBase(WindowImpl):
    appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ()

    def __init__(self, parent, content):
        if parent is None:
            app = self.appLoader.getApp()
            view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
            if view is not None:
                parent = view.getParentWindow()
        super(RewardWindowBase, self).__init__(WindowFlags.WINDOW, decorator=WindowView(), parent=parent, content=content, areaID=R.areas.default())
        return

    def _initialize(self):
        super(RewardWindowBase, self)._initialize()
        self.content.getViewModel().onConfirmBtnClicked += self._onConfirmBtnClicked
        self.content.getViewModel().onSecondBtnClicked += self._onSecondBtnClicked
        with self.windowModel.transaction() as tx:
            tx.setTitle(R.strings.ingame_gui.rewardWindow.winHeaderText())

    def _finalize(self):
        super(RewardWindowBase, self)._finalize()
        self.content.getViewModel().onConfirmBtnClicked -= self._onConfirmBtnClicked
        self.content.getViewModel().onSecondBtnClicked -= self._onSecondBtnClicked

    def _onConfirmBtnClicked(self, _=None):
        self.content.handleNextButton()
        self._onClosed()

    def _onDecoratorReady(self):
        super(RewardWindowBase, self)._onDecoratorReady()
        if self.area is not None and self.area.getPreviousNeighbor(self) is not None:
            self.cascade()
        else:
            self.center()
        return

    def _onSecondBtnClicked(self, _=None):
        self.content.handleGoToButton()


class RewardWindow(RewardWindowBase):
    __slots__ = ()

    def __init__(self, ctx=None, parent=None):
        contentSettings = ViewSettings(R.views.lobby.reward_window.reward_window_content.RewardWindowContent())
        contentSettings.model = RewardWindowContentModel()
        super(RewardWindow, self).__init__(parent=parent, content=QuestRewardWindowContent(contentSettings, ctx=ctx))


class TwitchRewardWindow(RewardWindowBase):
    __slots__ = ()

    def __init__(self, ctx=None, parent=None):
        contentSettings = ViewSettings(R.views.lobby.reward_window.twitch_reward_window_content.TwitchRewardWindowContent())
        contentSettings.model = RewardWindowContentModel()
        super(TwitchRewardWindow, self).__init__(parent=parent, content=TwitchRewardWindowContent(contentSettings, ctx=ctx))


class DynamicRewardWindowContent(BaseRewardWindowContent):
    __slots__ = ('__bonuses', '_eventName')
    _BONUSES_ORDER = (Currency.GOLD,
     'vehicles',
     'premium_plus',
     'dossier',
     'customizations',
     'slots',
     'goodies',
     'blueprints',
     'blueprintsAny',
     'items',
     Currency.CRYSTAL,
     Currency.CREDITS,
     'freeXP',
     'tokens')

    def __init__(self, settings, ctx=None):
        super(DynamicRewardWindowContent, self).__init__(settings, ctx)
        self.__bonuses = None
        if ctx is not None:
            self.__bonuses = ctx.get('bonuses', None)
        return

    def handleNextButton(self):
        self.destroyWindow()

    def handleGoToButton(self):
        showClanQuestWindow()
        self.destroyWindow()

    def _getBonuses(self):
        bonuses = []
        if self.__bonuses is None:
            return bonuses
        else:
            for key, value in self.__bonuses.items():
                bonus = getNonQuestBonuses(key, value)
                if bonus:
                    bonuses.extend(bonus)

            return bonuses

    def _finalize(self):
        super(DynamicRewardWindowContent, self)._finalize()
        self.__bonuses = None
        return


class DynamicRewardWindow(RewardWindowBase):
    __slots__ = ('_eventName',)

    def __init__(self, ctx=None, parent=None):
        self._eventName = ctx['eventName']
        contentSettings = ViewSettings(R.views.lobby.reward_window.clan_reward_window_content.ClanRewardWindowContent())
        contentSettings.model = RewardWindowContentModel()
        super(DynamicRewardWindow, self).__init__(parent=parent, content=DynamicRewardWindowContent(contentSettings, ctx=ctx))

    def _initialize(self):
        super(DynamicRewardWindow, self)._initialize()
        self.windowModel.setTitle(getattr(R.strings.ingame_gui.rewardWindow, self._eventName).winHeaderText())


class LootBoxRewardWindowContent(BaseRewardWindowContent):
    _festivityController = dependency.descriptor(IFestivityController)
    __slots__ = ('_lootboxType', '_lootboxesCount', '_isFree')

    def __init__(self, settings, ctx):
        super(LootBoxRewardWindowContent, self).__init__(settings, ctx)
        if ctx is not None:
            self._lootboxType = ctx.get('lootboxType', '')
            self._lootboxesCount = ctx.get('lootboxesCount', 0)
            self._isFree = ctx.get('isFree', False)
        else:
            self._lootboxType = ''
            self._lootboxesCount = 0
            self._isFree = False
        return

    def handleNextButton(self):
        showLootBoxEntry(self._lootboxType)

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    @sf_lobby
    def app(self):
        pass

    def _initialize(self, *args, **kwargs):
        super(LootBoxRewardWindowContent, self)._initialize(*args, **kwargs)
        g_eventBus.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.LootboxesEvent.ON_ENTRY_VIEW_LOADED, self.__onEntryViewLoaded, scope=EVENT_BUS_SCOPE.LOBBY)
        self._festivityController.onStateChanged += self.__onStateChanged
        self.app.containerManager.onViewLoaded += self.__onViewLoaded
        with self.getViewModel().transaction() as tx:
            tx.setRewardsCount(self._lootboxesCount)
            tx.setLootboxType(self._lootboxType)
            tx.setIsFree(self._isFree)

    def _finalize(self):
        self._festivityController.onStateChanged -= self.__onStateChanged
        self.app.containerManager.onViewLoaded -= self.__onViewLoaded
        g_eventBus.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.LootboxesEvent.ON_ENTRY_VIEW_LOADED, self.__onEntryViewLoaded, scope=EVENT_BUS_SCOPE.LOBBY)
        super(LootBoxRewardWindowContent, self)._finalize()

    def _initRewardsList(self):
        pass

    def __onStateChanged(self):
        if not self._festivityController.isEnabled():
            self.destroyWindow()

    def __handleFightButtonUpdated(self, _):
        prbDispatcher = self.prbDispatcher
        if prbDispatcher is not None and prbDispatcher.getFunctionalState().isNavigationDisabled():
            self.destroyWindow()
        return

    def __onViewLoaded(self, pyView):
        if pyView.alias != VIEW_ALIAS.LOBBY_HANGAR and pyView.layer == WindowLayer.SUB_VIEW:
            self.destroyWindow()

    def __onEntryViewLoaded(self, _):
        self.destroyWindow()


class LootBoxRewardWindow(RewardWindowBase):
    __slots__ = ()

    def __init__(self, ctx=None, parent=None):
        contentSettings = ViewSettings(R.views.lobby.reward_window.loot_box_reward_window_content.LootBoxRewardWindowContent())
        contentSettings.model = LootBoxRewardWindowContentModel()
        super(LootBoxRewardWindow, self).__init__(parent=parent, content=LootBoxRewardWindowContent(contentSettings, ctx=ctx))

    def _initialize(self):
        super(LootBoxRewardWindow, self)._initialize()
        self.windowModel.setTitle(R.strings.ingame_gui.rewardWindow.lootbox.winHeaderText())


class GiveAwayRewardWindowContent(QuestRewardWindowContent):
    __slots__ = ('__items', '_eventName', '_quest', '_vehicles')
    _BONUSES_ORDER = (Currency.CRYSTAL,
     'badgesGroup',
     'dossier',
     'vehicles',
     Currency.CREDITS,
     'customizations',
     'items')

    def handleNextButton(self):
        self.destroyWindow()

    def _getAwardComposer(self):
        return AnniversaryAwardComposer(_ADDITIONAL_AWARDS_COUNT, getAnniversaryPacker())


class GiveAwayRewardWindow(RewardWindowBase):
    __slots__ = ()

    def __init__(self, ctx=None, parent=None):
        contentSettings = ViewSettings(R.views.lobby.reward_window.twitch_reward_window_content.TwitchRewardWindowContent())
        contentSettings.model = RewardWindowContentModel()
        super(GiveAwayRewardWindow, self).__init__(parent=parent, content=GiveAwayRewardWindowContent(contentSettings, ctx=ctx))

    def _initialize(self):
        super(GiveAwayRewardWindow, self)._initialize()
        self.windowModel.setTitle(R.strings.ingame_gui.rewardWindow.anniversary_ga.winHeaderText())


class PiggyBankRewardWindow(RewardWindowBase):
    __slots__ = ()

    def __init__(self, ctx=None, parent=None):
        contentSettings = ViewSettings(R.views.lobby.reward_window.piggy_bank_reward_window_content.PiggyBankRewardWindowContent())
        contentSettings.model = PiggyBankRewardWindowContentModel()
        super(PiggyBankRewardWindow, self).__init__(parent=parent, content=PiggyBankRewardWindowContent(contentSettings, ctx=ctx))

    def _initialize(self):
        super(PiggyBankRewardWindow, self)._initialize()
        self.windowModel.setTitle(R.strings.ingame_gui.rewardWindow.piggyBank.winHeaderText())
