# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/reward_window.py
import logging
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import WindowFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import PackRentVehiclesAwardComposer, AnniversaryAwardComposer, CurtailingAwardsComposer, RawLabelBonusComposer
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getMissionInfoData
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.BARRACKS_CONSTANTS import BARRACKS_CONSTANTS
from gui.impl.backport import TooltipData, BackportTooltipWindow
from gui.impl.pub import ViewImpl, WindowImpl, WindowView
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.reward_renderer_model import RewardRendererModel
from gui.impl.gen.view_models.windows.piggy_bank_reward_window_content_model import PiggyBankRewardWindowContentModel
from gui.impl.gen.view_models.windows.reward_window_content_model import RewardWindowContentModel
from gui.server_events.awards_formatters import getPackRentVehiclesAwardPacker, getAnniversaryPacker, getDefaultAwardFormatter
from gui.server_events.bonuses import getTutorialBonuses, CreditsBonus
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE, event_dispatcher
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
     Currency.EVENT_COIN)

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

    @event_dispatcher.leaveEventMode
    def onHyperLinkClicked(self):
        event_dispatcher.showPremiumDialog()

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
    _BONUSES_ORDER = ('dossier',
     'customizations',
     'premium_plus',
     Currency.GOLD,
     'vehicles',
     'items',
     'crewBooks')

    def handleNextButton(self):
        bonuses = self._quest.getBonuses('tokens')
        needContinue = False
        for bonus in bonuses:
            for tID in bonus.getTokens():
                if getRecruitInfo(tID) is not None:
                    needContinue = True
                    break

        if needContinue:
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_BARRACKS, ctx={'location': BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED}), scope=EVENT_BUS_SCOPE.LOBBY)
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
        super(RewardWindowBase, self).__init__(WindowFlags.DIALOG, decorator=WindowView(), parent=parent, content=content, areaID=R.areas.default())
        return

    def _initialize(self):
        super(RewardWindowBase, self)._initialize()
        self.content.getViewModel().onConfirmBtnClicked += self._onConfirmBtnClicked
        with self.windowModel.transaction() as tx:
            tx.setTitle(R.strings.ingame_gui.rewardWindow.winHeaderText())
        self.center()

    def _finalize(self):
        super(RewardWindowBase, self)._finalize()
        self.content.getViewModel().onConfirmBtnClicked -= self._onConfirmBtnClicked

    def _onConfirmBtnClicked(self, _=None):
        self.content.handleNextButton()
        self._onClosed()


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
