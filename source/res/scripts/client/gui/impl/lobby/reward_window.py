# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/reward_window.py
import logging
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import WindowFlags, WindowLayer, ViewFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import PackRentVehiclesAwardComposer, AnniversaryAwardComposer, CurtailingAwardsComposer, RawLabelBonusComposer
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getMissionInfoData
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPremiumUrl
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl.backport import TooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.reward_renderer_model import RewardRendererModel
from gui.impl.gen.view_models.views.lobby.player_subscriptions.subscription_reward_view_model import SubscriptionRewardViewModel
from gui.impl.gen.view_models.windows.piggy_bank_reward_window_content_model import PiggyBankRewardWindowContentModel
from gui.impl.gen.view_models.windows.reward_window_content_model import RewardWindowContentModel
from gui.impl.lobby.player_subscriptions.player_subscriptions_reward_window_view import PlayerSubscriptionRewardWindowView
from gui.impl.pub import ViewImpl, WindowImpl, WindowView
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.awards_formatters import getPackRentVehiclesAwardPacker, getAnniversaryPacker, getDefaultAwardFormatter
from gui.server_events.bonuses import getTutorialBonuses, CreditsBonus, getNonQuestBonuses
from gui.shared.event_dispatcher import showClanQuestWindow
from gui.shared.event_dispatcher import showShop
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
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

    @property
    def viewModel(self):
        return self.getViewModel()

    def handleNextButton(self):
        pass

    def handleGoToButton(self):
        pass

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = int(event.getArgument('tooltipId'))
            window = BackportTooltipWindow(self.__items[tooltipId], self.getParentWindow()) if tooltipId is not None and tooltipId in self.__items else None
            if window is not None:
                window.load()
            return window
        else:
            return super(BaseRewardWindowContent, self).createToolTip(event)

    def _keySortOrder(self, bonus):
        return self._BONUSES_ORDER.index(bonus.getName()) if bonus.getName() in self._BONUSES_ORDER else len(self._BONUSES_ORDER)

    def _initialize(self, *args, **kwargs):
        super(BaseRewardWindowContent, self)._initialize(*args, **kwargs)
        self._setTitles()
        self._initRewardsList()

    def _setTitles(self):
        self.getViewModel().setEventName(self._eventName)

    def _getBonuses(self):
        return []

    def _getAwardComposer(self):
        return CurtailingAwardsComposer(_ADDITIONAL_AWARDS_COUNT, getDefaultAwardFormatter())

    def _getRewardRendererModelCls(self):
        return RewardRendererModel

    def _initRewardsList(self):
        with self.getViewModel().transaction() as tx:
            rewardsList = self._getRewardsModel(tx)
            bonuses = self._getBonuses()
            bonuses.sort(key=self._keySortOrder)
            formatter = self._getAwardComposer()
            for index, bonus in enumerate(formatter.getFormattedBonuses(bonuses)):
                rendererModel = self._getRewardRendererModelCls()()
                with rendererModel.transaction() as rewardTx:
                    self._setBonusModel(rewardTx, bonus, index)
                rewardsList.addViewModel(rendererModel)
                self._initTooltip(bonus, index)

            self._setShowRewards(tx)

    def _initTooltip(self, bonus, index):
        self.__items[index] = TooltipData(tooltip=bonus.get('tooltip', None), isSpecial=bonus.get('isSpecial', False), specialAlias=bonus.get('specialAlias', ''), specialArgs=bonus.get('specialArgs', None))
        return

    def _setShowRewards(self, tx):
        tx.setShowRewards(bool(self.__items))

    def _getRewardsModel(self, tx):
        return tx.rewardsList.getItems()

    def _setBonusModel(self, rewardTx, bonus, index):
        rewardTx.setIcon(bonus.get('imgSource', ''))
        rewardTx.setLabelStr(bonus.get('label', '') or '')
        rewardTx.setTooltipId(index)
        rewardTx.setHighlightType(bonus.get('highlightIcon', '') or '')
        rewardTx.setOverlayType(bonus.get('overlayIcon', '') or '')
        rewardTx.setHasCompensation(bonus.get('hasCompensation', False) or False)
        rewardTx.setLabelAlign(bonus.get('align', 'center') or 'center')


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


class RewardWindowBase(WindowImpl):
    appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ()

    def __init__(self, parent, content, layer=WindowLayer.UNDEFINED):
        if parent is None:
            app = self.appLoader.getApp()
            view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
            if view is not None:
                parent = view.getParentWindow()
        super(RewardWindowBase, self).__init__(WindowFlags.WINDOW, decorator=WindowView(), parent=parent, content=content, areaID=R.areas.default(), layer=layer)
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


class TwitchRewardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, ctx, parent=None):
        settings = ViewSettings(R.views.lobby.player_subscriptions.SubscriptionRewardView())
        settings.flags = ViewFlags.VIEW
        settings.model = SubscriptionRewardViewModel()
        super(TwitchRewardWindow, self).__init__(layer=WindowLayer.FULLSCREEN_WINDOW, content=PlayerSubscriptionRewardWindowView(settings, ctx), parent=parent)


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
