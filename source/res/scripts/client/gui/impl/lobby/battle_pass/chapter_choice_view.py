# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/chapter_choice_view.py
from functools import partial
import typing
from PlayerEvents import g_playerEvents
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from battle_pass_common import CurrencyBP
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBattlePassCoinProductsUrl, getBattlePassPointsProductsUrl
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.battle_pass.battle_pass_helpers import chaptersIDsComparator, getInfoPageURL, getStyleForChapter
from gui.impl import backport
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_choice_view_model import ChapterChoiceViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_model import ChapterModel, ChapterStates
from gui.impl.gen.view_models.views.lobby.vehicle_preview.top_panel.top_panel_tabs_model import TabID
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared.event_dispatcher import hideVehiclePreview, showBattlePassBuyWindow, showBattlePassHowToEarnPointsView, showBrowserOverlayView, showShop, showStyleProgressionPreview, showHangar, showStylePreview
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
from tutorial.control.game_vars import getVehicleByIntCD
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.shared.gui_items.customization.c11n_items import Style
_CHAPTER_STATES = {ChapterState.ACTIVE: ChapterStates.ACTIVE,
 ChapterState.COMPLETED: ChapterStates.COMPLETED,
 ChapterState.PAUSED: ChapterStates.PAUSED,
 ChapterState.NOT_STARTED: ChapterStates.NOTSTARTED}
_FULL_PROGRESS = 100

class ChapterChoiceView(ViewImpl):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_pass.ChapterChoiceView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = ChapterChoiceViewModel()
        super(ChapterChoiceView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ChapterChoiceView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ChapterChoiceView, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _getEvents(self):
        return ((self.viewModel.onAboutClick, self.__showAboutView),
         (self.viewModel.onChapterSelect, self.__selectChapter),
         (self.viewModel.onPreviewClick, self.__showPreview),
         (self.viewModel.onPointsInfoClick, self.__showPointsInfoView),
         (self.viewModel.onBuyClick, self.__buyBattlePass),
         (self.viewModel.onBpcoinClick, self.__showCoinsShop),
         (self.viewModel.onBpbitClick, self.__showPointsShop),
         (self.viewModel.onTakeRewardsClick, self.__takeAllRewards),
         (self.viewModel.onClose, self.__close),
         (self.__battlePassController.onBattlePassSettingsChange, self.__checkBPState),
         (self.__battlePassController.onExtraChapterExpired, self.__checkBPState),
         (self.__battlePassController.onPointsUpdated, self.__onPointsUpdated),
         (self.__battlePassController.onSelectTokenUpdated, self.__updateRewardChoice),
         (self.__battlePassController.onOffersUpdated, self.__updateRewardChoice),
         (self.__battlePassController.onSeasonStateChanged, self.__checkBPState),
         (g_playerEvents.onClientUpdated, self.__onBpBitUpdated))

    def _getCallbacks(self):
        return (('stats.bpcoin', self.__updateBalance),)

    def _fillModel(self):
        with self.viewModel.transaction() as model:
            self.__updateChapters(model.getChapters())
            self.__updateBalance(model=model)
            self.__updateRewardChoice(model=model)
            self.__updateBPBitCount(model=model)
            self.__updateFreePoints(model=model)
            model.setIsBattlePassCompleted(self.__battlePassController.isCompleted())

    def __updateChapters(self, chapters):
        chapters.clear()
        for chapterID in sorted(self.__battlePassController.getChapterIDs(), cmp=chaptersIDsComparator):
            style = getStyleForChapter(chapterID)
            model = ChapterModel()
            model.setChapterID(chapterID)
            model.setIsBought(self.__battlePassController.isBought(chapterID=chapterID))
            model.setStyleName(style.userName)
            model.setIsExtra(self.__battlePassController.isExtraChapter(chapterID))
            self.__fillProgression(chapterID, model)
            self.__fillVehicle(style, model)
            chapters.addViewModel(model)

        chapters.invalidate()

    def __fillVehicle(self, style, model):
        vehicleCD = getVehicleCDForStyle(style, itemsCache=self.__itemsCache)
        vehicle = getVehicleByIntCD(vehicleCD)
        fillVehicleInfo(model.vehicleInfo, vehicle)
        model.setIsVehicleInHangar(vehicle.isInInventory)

    def __fillProgression(self, chapterID, model):
        model.setChapterState(_CHAPTER_STATES.get(self.__battlePassController.getChapterState(chapterID)))
        model.setCurrentLevel(self.__battlePassController.getLevelInChapter(chapterID) + 1)
        points, maxPoints = self.__battlePassController.getLevelProgression(chapterID)
        model.setLevelProgression(_FULL_PROGRESS * points / (maxPoints or _FULL_PROGRESS))

    def __updateChaptersProgression(self, chapters):
        for chapter in chapters:
            chapterID = chapter.getChapterID()
            self.__fillProgression(chapterID, chapter)

        chapters.invalidate()

    @replaceNoneKwargsModel
    def __updateBalance(self, value=None, model=None):
        model.setBpcoinCount(self.__itemsCache.items.stats.bpcoin)

    @replaceNoneKwargsModel
    def __updateRewardChoice(self, model=None):
        model.setNotChosenRewardCount(self.__battlePassController.getNotChosenRewardCount())
        model.setIsChooseRewardsEnabled(self.__battlePassController.canChooseAnyReward())

    @replaceNoneKwargsModel
    def __updateBPBitCount(self, model=None):
        model.setBpbitCount(self.__itemsCache.items.stats.dynamicCurrencies.get(CurrencyBP.BIT.value, 0))

    @replaceNoneKwargsModel
    def __updateFreePoints(self, model=None):
        model.setFreePoints(self.__battlePassController.getFreePoints())

    def __onPointsUpdated(self, *_):
        with self.viewModel.transaction() as model:
            self.__updateChaptersProgression(model.getChapters())
            self.__updateFreePoints(model=model)
            model.setIsBattlePassCompleted(self.__battlePassController.isCompleted())

    def __onBpBitUpdated(self, *data):
        if data[0].get('cache', {}).get('dynamicCurrencies', {}).get(CurrencyBP.BIT.value, ''):
            self.__updateBPBitCount()

    def __checkBPState(self, *_):
        if self.__battlePassController.isPaused():
            showMissionsBattlePass()
            return
        if not self.__battlePassController.isActive():
            showHangar()
            return
        if len(self.__battlePassController.getChapterIDs()) != len(self.viewModel.getChapters()):
            showMissionsBattlePass(R.views.lobby.battle_pass.ChapterChoiceView())

    @staticmethod
    def __buyBattlePass(_):
        showBattlePassBuyWindow()

    def __showPreview(self, args):
        chapterID = args.get('chapterID')
        if chapterID is None:
            return
        else:
            hideVehiclePreview(back=False)
            style = getStyleForChapter(chapterID, battlePass=self.__battlePassController)
            vehicleCD = getVehicleCDForStyle(style, itemsCache=self.__itemsCache)
            if self.__battlePassController.isExtraChapter(chapterID):
                self.__showStylePreview(style, vehicleCD)
            else:
                self.__showProgressionStylePreview(style, vehicleCD)
            self.destroyWindow()
            return

    def __showStylePreview(self, style, vehicleCD):
        showStylePreview(vehicleCD, style=style, topPanelData={'linkage': VEHPREVIEW_CONSTANTS.TOP_PANEL_TABS_LINKAGE,
         'tabIDs': (TabID.VEHICLE, TabID.STYLE),
         'currentTabID': TabID.STYLE}, backCallback=self.__getPreviewCallback())

    @staticmethod
    def __getPreviewCallback():
        return partial(showMissionsBattlePass, R.views.lobby.battle_pass.ChapterChoiceView())

    def __showProgressionStylePreview(self, style, vehicleCD):
        showStyleProgressionPreview(vehicleCD, style, style.getDescription(), self.__getPreviewCallback(), backport.text(R.strings.battle_pass.chapterChoice.stylePreview.backLabel()), styleLevel=style.getMaxProgressionLevel())

    def __selectChapter(self, args):
        chapterID = int(args.get('chapterID', 0))
        settings = self.__settingsCore.serverSettings
        needShowExtraIntro = settings.getBPStorage().get(BattlePassStorageKeys.EXTRA_CHAPTER_INTRO_SHOWN)
        if self.__battlePassController.isExtraChapter(chapterID) and not needShowExtraIntro:
            layoutID = R.views.lobby.battle_pass.ExtraIntroView()
        else:
            layoutID = R.views.lobby.battle_pass.BattlePassProgressionsView()
        showMissionsBattlePass(layoutID, chapterID)

    @staticmethod
    def __showAboutView():
        showBrowserOverlayView(getInfoPageURL(), VIEW_ALIAS.BATTLE_PASS_BROWSER_VIEW)

    def __showPointsInfoView(self):
        showBattlePassHowToEarnPointsView(parent=self.getParentWindow())

    def __takeAllRewards(self):
        self.__battlePassController.takeAllRewards()

    @staticmethod
    def __showCoinsShop():
        showShop(getBattlePassCoinProductsUrl())

    @staticmethod
    def __showPointsShop():
        showShop(getBattlePassPointsProductsUrl())

    @staticmethod
    def __close():
        showHangar()
