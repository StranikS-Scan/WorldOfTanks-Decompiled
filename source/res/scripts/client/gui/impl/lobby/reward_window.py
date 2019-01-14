# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/reward_window.py
from frameworks.wulf import ViewFlags
from frameworks.wulf.gui_constants import WindowFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import PackRentVehiclesAwardComposer, AnniversaryAwardComposer
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getMissionInfoData
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.BARRACKS_CONSTANTS import BARRACKS_CONSTANTS
from gui.app_loader import g_appLoader
from gui.impl.backport import TooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.reward_renderer_model import RewardRendererModel
from gui.impl.gen.view_models.windows.reward_window_content_model import RewardWindowContentModel
from gui.impl.gen.view_models.windows.twitch_reward_window_content_model import TwitchRewardWindowContentModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.window_impl import WindowImpl
from gui.impl.pub.window_view import WindowView
from gui.server_events.awards_formatters import getPackRentVehiclesAwardPacker, getAnniversaryPacker
from gui.server_events.bonuses import getTutorialBonuses
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.money import Currency
BASE_EVENT_NAME = 'base'
_ADDITIONAL_AWARDS_COUNT = 5

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
        if event.contentID == R.views.backportTooltipContent():
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
        return PackRentVehiclesAwardComposer(_ADDITIONAL_AWARDS_COUNT, getPackRentVehiclesAwardPacker())

    def _initRewardsList(self):
        with self.getViewModel().transaction() as tx:
            rewardsList = tx.rewardsList.getItems()
            if self._quest is not None:
                allBonuses = getMissionInfoData(self._quest).getSubstituteBonuses()
                bonuses = [ bonus for bonus in allBonuses if bonus.getName() != 'vehicles' ]
                vehBonus = getTutorialBonuses('vehicles', self._vehicles)
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


class RewardWindowBase(WindowImpl):
    __slots__ = ()

    def __init__(self, parent, content):
        if parent is None:
            app = g_appLoader.getApp()
            view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
            if view is not None:
                parent = view.getParentWindow()
        super(RewardWindowBase, self).__init__(WindowFlags.DIALOG | WindowFlags.RESIZABLE, decorator=WindowView(), parent=parent, content=content, areaID=R.areas.default())
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
        super(RewardWindow, self).__init__(parent=parent, content=RewardWindowContent(layoutID=R.views.rewardWindowContent(), viewModelClazz=RewardWindowContentModel, ctx=ctx))


class TwitchRewardWindow(RewardWindowBase):
    __slots__ = ()

    def __init__(self, ctx=None, parent=None):
        super(TwitchRewardWindow, self).__init__(parent=parent, content=TwitchRewardWindowContent(layoutID=R.views.twitchRewardWindowContent(), viewModelClazz=TwitchRewardWindowContentModel, ctx=ctx))


class GiveAwayRewardWindowContent(RewardWindowContent):
    __slots__ = ('__items', '_eventName', '_quest', '_vehicles')
    _BONUSES_ORDER = (Currency.CRYSTAL,
     'badgesGroup',
     'dossier',
     'vehicles',
     Currency.CREDITS,
     'customizations',
     'items')

    def handleNextButton(self):
        self.getParentWindow().destroy()

    def _getAwardComposer(self):
        return AnniversaryAwardComposer(_ADDITIONAL_AWARDS_COUNT, getAnniversaryPacker())


class GiveAwayRewardWindow(RewardWindowBase):
    __slots__ = ()

    def __init__(self, ctx=None, parent=None):
        super(GiveAwayRewardWindow, self).__init__(parent=parent, content=GiveAwayRewardWindowContent(layoutID=R.views.twitchRewardWindowContent(), viewModelClazz=RewardWindowContentModel, ctx=ctx))

    def _initialize(self):
        super(GiveAwayRewardWindow, self)._initialize()
        self.windowModel.setTitle(R.strings.ingame_gui.rewardWindow.anniversary_ga.winHeaderText())
