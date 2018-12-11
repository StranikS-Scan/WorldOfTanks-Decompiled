# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/reward_window.py
from frameworks.wulf import ViewFlags, WindowFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getMissionInfoData
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.genConsts.BARRACKS_CONSTANTS import BARRACKS_CONSTANTS
from gui.app_loader import sf_lobby
from gui.impl.gen.view_models.ui_kit.reward_renderer_model import RewardRendererModel
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import PackRentVehiclesAwardComposer, AnniversaryAwardComposer
from gui.impl.gen.view_models.windows.loot_box_reward_window_content_model import LootBoxRewardWindowContentModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.window_view import WindowView
from gui.prb_control import prbDispatcherProperty
from gui.server_events.awards_formatters import getPackRentVehiclesAwardPacker, getAnniversaryPacker
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.server_events.recruit_helper import getRecruitInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.reward_window_content_model import RewardWindowContentModel
from gui.impl.gen.view_models.windows.twitch_reward_window_content_model import TwitchRewardWindowContentModel
from gui.shared.event_dispatcher import showLootBoxEntry
from gui.shared.money import Currency
from gui.impl.backport_tooltip import TooltipData, BackportTooltipWindow
from gui.impl.pub import LobbyWindow
from helpers import dependency
from skeletons.gui.game_control import IFestivityController
BASE_EVENT_NAME = 'base'
ADDITIONAL_AWARDS_COUNT = 5

class RewardWindowContent(ViewImpl):
    __slots__ = ('__items', '_eventName', '_quest', '_vehicles')
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
     'goodies')

    def __init__(self, layoutID, viewModelClazz, ctx=None):
        super(RewardWindowContent, self).__init__(layoutID, ViewFlags.VIEW, viewModelClazz)
        self.__items = {}
        if ctx is not None:
            self._eventName = ctx.get('eventName', BASE_EVENT_NAME)
            self._quest = ctx.get('quest', None)
            self._vehicles = ctx.get('bonusVehicles', {})
        else:
            self._eventName = BASE_EVENT_NAME
            self._quest = None
            self._vehicles = {}
        return

    def handleNextButton(self):
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_BARRACKS, ctx={'location': BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED}), scope=EVENT_BUS_SCOPE.LOBBY)

    def createToolTip(self, event):
        if event.contentID == R.views.backportTooltipContent:
            tooltipId = event.getArgument('tooltipId')
            window = BackportTooltipWindow(self.__items[tooltipId], self.getParentWindow()) if tooltipId is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(RewardWindowContent, self).createToolTip(event)

    def _keySortOrder(self, bonus):
        return self._BONUSES_ORDER.index(bonus.getName()) if bonus.getName() in self._BONUSES_ORDER else len(self._BONUSES_ORDER)

    def _initialize(self, *args, **kwargs):
        super(RewardWindowContent, self)._initialize(*args, **kwargs)
        self.getViewModel().setEventName(self._eventName)
        self._initRewardsList()

    def _getAwardComposer(self):
        return PackRentVehiclesAwardComposer(ADDITIONAL_AWARDS_COUNT, getPackRentVehiclesAwardPacker())

    def _initRewardsList(self):
        with self.getViewModel().transaction() as tx:
            rewardsList = tx.rewardsList.getItems()
            if self._quest is not None:
                allBonuses = getMissionInfoData(self._quest).getSubstituteBonuses()
                bonuses = [ bonus for bonus in allBonuses if bonus.getName() != 'vehicles' ]
                vehBonus = getNonQuestBonuses('vehicles', self._vehicles)
                bonuses.extend(vehBonus)
                bonuses.sort(key=self._keySortOrder)
                formatter = self._getAwardComposer()
                for index, bonus in enumerate(formatter.getFormattedBonuses(bonuses)):
                    rendererModel = RewardRendererModel()
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

    def _finalize(self):
        super(RewardWindowContent, self)._finalize()
        self._quest = None
        return


class TwitchRewardWindowContent(RewardWindowContent):
    __slots__ = ()

    def handleNextButton(self):
        bonuses = self._quest.getBonuses('tokens')
        needContinue = False
        for bonus in bonuses:
            for tID in bonus.getTokens():
                if getRecruitInfo(tID) is not None:
                    needContinue = True
                    break

        if needContinue:
            super(TwitchRewardWindowContent, self).handleNextButton()
        return


class RewardWindowBase(LobbyWindow):
    __slots__ = ()

    def __init__(self, content=None, parent=None):
        super(RewardWindowBase, self).__init__(wndFlags=WindowFlags.DIALOG, decorator=WindowView(), content=content, parent=parent)

    @property
    def windowModel(self):
        return super(RewardWindowBase, self)._getDecoratorViewModel()

    def _initialize(self):
        super(RewardWindowBase, self)._initialize()
        self.content.getViewModel().getContent().getViewModel().onConfirmBtnClicked += self._onConfirmBtnClicked
        with self.windowModel.transaction() as tx:
            tx.setAlignToCenter(True)
            self._setWindowTitle()
        self.windowModel.onClosed += self._onClosed

    def _setWindowTitle(self):
        self.windowModel.setTitle(R.strings.ingame_gui.rewardWindow.winHeaderText)

    def _finalize(self):
        super(RewardWindowBase, self)._finalize()
        self.content.getViewModel().getContent().getViewModel().onConfirmBtnClicked -= self._onConfirmBtnClicked
        self.windowModel.onClosed -= self._onClosed

    def _onClosed(self, _=None):
        self.destroy()

    def _onConfirmBtnClicked(self, _=None):
        self.content.getViewModel().getContent().handleNextButton()
        self._onClosed()


class RewardWindow(RewardWindowBase):
    __slots__ = ()

    def __init__(self, ctx=None, parent=None):
        super(RewardWindow, self).__init__(parent=parent, content=RewardWindowContent(layoutID=R.views.rewardWindowContent, viewModelClazz=RewardWindowContentModel, ctx=ctx))


class TwitchRewardWindow(RewardWindowBase):
    __slots__ = ()

    def __init__(self, ctx=None, parent=None):
        super(TwitchRewardWindow, self).__init__(parent=parent, content=TwitchRewardWindowContent(layoutID=R.views.twitchRewardWindowContent, viewModelClazz=TwitchRewardWindowContentModel, ctx=ctx))


class LootBoxRewardWindowContent(RewardWindowContent):
    _festivityController = dependency.descriptor(IFestivityController)
    __slots__ = ('_lootboxType', '_lootboxesCount', '_isFree')

    def __init__(self, layoutID, viewModelClazz, ctx):
        super(LootBoxRewardWindowContent, self).__init__(layoutID, viewModelClazz, ctx)
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
        if pyView.alias != VIEW_ALIAS.LOBBY_HANGAR and pyView.viewType == ViewTypes.LOBBY_SUB:
            self.destroyWindow()

    def __onEntryViewLoaded(self, _):
        self.destroyWindow()


class LootBoxRewardWindow(RewardWindowBase):
    __slots__ = ()

    def __init__(self, ctx=None, parent=None):
        super(LootBoxRewardWindow, self).__init__(parent=parent, content=LootBoxRewardWindowContent(layoutID=R.views.lootBoxRewardWindowContent, viewModelClazz=LootBoxRewardWindowContentModel, ctx=ctx))

    def _setWindowTitle(self):
        self.windowModel.setTitle(R.strings.ingame_gui.rewardWindow.lootbox.winHeaderText)


class GiveAwayRewardWindowContent(RewardWindowContent):
    __slots__ = ('__items', '_eventName', '_quest', '_vehicles')
    _BONUSES_ORDER = ('dossier',
     'badgesGroup',
     'vehicles',
     'items',
     Currency.CRYSTAL,
     Currency.CREDITS,
     'customizations')

    def handleNextButton(self):
        self.getParentWindow().destroy()

    def _getAwardComposer(self):
        return AnniversaryAwardComposer(ADDITIONAL_AWARDS_COUNT, getAnniversaryPacker())


class GiveAwayRewardWindow(RewardWindowBase):
    __slots__ = ()

    def __init__(self, ctx=None, parent=None):
        super(GiveAwayRewardWindow, self).__init__(parent=parent, content=GiveAwayRewardWindowContent(layoutID=R.views.twitchRewardWindowContent, viewModelClazz=RewardWindowContentModel, ctx=ctx))

    def _setWindowTitle(self):
        self.windowModel.setTitle(R.strings.ingame_gui.rewardWindow.anniversary_ga.winHeaderText)
