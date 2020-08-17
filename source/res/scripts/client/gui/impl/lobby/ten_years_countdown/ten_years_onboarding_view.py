# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/ten_years_countdown/ten_years_onboarding_view.py
import typing
from enum import Enum
import BigWorld
import WWISE
from constants import IS_CHINA
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.ten_years_countdown.onboarding_calendar_block_model import OnboardingCalendarBlockModel
from gui.impl.gen.view_models.views.lobby.ten_years_countdown.onboarding_stage_info_block_model import OnboardingStageInfoBlockModel
from gui.impl.gen.view_models.views.lobby.ten_years_countdown.ten_years_onboarding_view_model import TenYearsOnboardingViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.bonuses import CustomizationsBonus
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from ten_year_countdown_config import EVENT_STYLE_MISSION_ID
from gui.Scaleform.daapi.view.lobby.ten_years_event.ten_years_event_sound_controller import TenYearsEventSounds
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.ten_years_countdown.onboarding_calendar_page_model import OnboardingCalendarPageModel
    from gui.impl.gen.view_models.views.lobby.ten_years_countdown.onboarding_stage_info_page_model import OnboardingStageInfoPageModel
    from gui.impl.gen.view_models.views.lobby.ten_years_countdown.onboarding_reward_page_model import OnboardingRewardPageModel

class BlockStates(Enum):
    PAST = 'past'
    CURRENT = 'current'
    FUTURE = 'future'


_STAGE_INFO_BLOCKS_COUNT = 3

class TenYearsOnboardingView(ViewImpl):
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__selectedPageId', '__pagesCount', '__currentStageNumber', '__isCurrentStageActive', '__stagesCount', '__months', '__callback', '__isLogOff')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.ten_years_countdown.TenYearsOnboardingView())
        settings.model = TenYearsOnboardingViewModel()
        settings.flags = ViewFlags.OVERLAY_VIEW
        settings.args = args
        settings.kwargs = kwargs
        super(TenYearsOnboardingView, self).__init__(settings)
        self.__selectedPageId = 0
        self.__pagesCount = 0
        self.__currentStageNumber = 0
        self.__isCurrentStageActive = False
        self.__months = {}
        self.__callback = None
        self.__isLogOff = False
        return

    @property
    def viewModel(self):
        return super(TenYearsOnboardingView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(TenYearsOnboardingView, self)._initialize(*args, **kwargs)
        self.viewModel.onForwardBtnClick += self.__onForwardBtnClick
        self.viewModel.onBackBtnClick += self.__onBackBtnClick
        WWISE.WW_eventGlobal(TenYearsEventSounds.EV_10Y_COUNTDOWN_WELCOME_SCREEN_OPEN)
        BigWorld.worldDrawEnabled(False)
        g_playerEvents.onDisconnected += self.__onDisconnected

    def _finalize(self):
        g_playerEvents.onDisconnected += self.__onDisconnected
        if not self.__isLogOff:
            BigWorld.worldDrawEnabled(True)
        WWISE.WW_eventGlobal(TenYearsEventSounds.EV_10Y_COUNTDOWN_WELCOME_SCREEN_CLOSE)
        self.viewModel.onForwardBtnClick -= self.__onForwardBtnClick
        self.viewModel.onBackBtnClick -= self.__onBackBtnClick
        super(TenYearsOnboardingView, self)._finalize()
        if self.__callback and callable(self.__callback):
            self.__callback()
            self.__callback = None
        return

    def _onLoading(self, currentStageNumber, isCurrentStageActive, months, blocksCount, callback):
        self.__currentStageNumber = currentStageNumber
        self.__isCurrentStageActive = isCurrentStageActive
        self.__months = months
        self.__stagesCount = blocksCount
        self.__callback = callback
        self.__pagesCount = 3 if self.__isCurrentStageActive and not IS_CHINA else 2
        self.__updateContent()

    def __updateContent(self):
        with self.viewModel.transaction() as model:
            model.setChapterNumber(self.__currentStageNumber)
            model.setSelectedPageId(self.__selectedPageId)
            model.setPagesCount(self.__pagesCount)
            model.setIsChina(IS_CHINA)
            if self.__selectedPageId == 0:
                self.__setCalendarPage(model.calendar)
            elif self.__selectedPageId == 1:
                if self.__isCurrentStageActive:
                    self.__setStageInfoPage(model.stageInfo)
                else:
                    self.__setRewardPage(model.reward)
            elif self.__selectedPageId == 2:
                self.__setRewardPage(model.reward)

    def __setCalendarPage(self, calendarModel):
        calendarModel.setTitle(R.strings.ten_year_countdown.on_boarding.calendar_title())
        calendarBlocks = calendarModel.getBlocks()
        calendarBlocks.clear()
        for stage in self.__months.iterkeys():
            calendarBlock = self.__packCalendarBlock(stage)
            calendarBlocks.addViewModel(calendarBlock)

        calendarBlocks.invalidate()

    def __setStageInfoPage(self, stageInfoModel):
        stageInfoModel.setTitle(R.strings.ten_year_countdown.on_boarding.stage_info.title())
        stageInfoModel.setSubTitle(R.strings.ten_year_countdown.on_boarding.stage_info.subTitle())
        stageInfoBlocks = stageInfoModel.getBlocks()
        stageInfoBlocks.clear()
        for index in range(1, _STAGE_INFO_BLOCKS_COUNT + 1):
            stageInfoBlock = OnboardingStageInfoBlockModel()
            infoBlockResource = R.strings.ten_year_countdown.on_boarding.stage_info.features.num(index)
            stageInfoBlock.setTitle(infoBlockResource.title())
            if 'description' in infoBlockResource.keys():
                stageInfoBlock.setDescription(infoBlockResource.description())
            imageName = 'stageInfo_{}'.format(index)
            if imageName in R.images.gui.maps.icons.tenYearsCountdown.onBoarding.keys():
                stageInfoBlock.setImage(R.images.gui.maps.icons.tenYearsCountdown.onBoarding.dyn(imageName)())
            stageInfoBlocks.addViewModel(stageInfoBlock)

        stageInfoBlocks.invalidate()

    def __setRewardPage(self, rewardModel):
        isStyleInQuest, isStyleInInventory = self.__getRewardInfo()
        if isStyleInInventory:
            rewardModel.setRewardSubTitle(R.strings.ten_year_countdown.on_boarding.reward.subTitle.rewarded())
            rewardModel.setRewardDescription(R.strings.ten_year_countdown.on_boarding.reward.description.rewarded())
            rewardModel.setIsRewardImageShown(False)
        else:
            rewardModel.setRewardSubTitle(R.strings.ten_year_countdown.on_boarding.reward.subTitle.notRewarded())
            rewardModel.setRewardDescription(R.strings.ten_year_countdown.on_boarding.reward.description.notRewarded())
            rewardModel.setIsRewardImageShown(True)
            if isStyleInQuest:
                rewardIcon = R.images.gui.maps.icons.tenYearsCountdown.onBoarding.reward()
            else:
                rewardIcon = R.images.gui.maps.icons.tenYearsCountdown.onBoarding.hiddenReward()
            rewardModel.setRewardImage(rewardIcon)

    def __packCalendarBlock(self, stageNumber):
        block = OnboardingCalendarBlockModel()
        defaultNumber = R.strings.ten_year_countdown.on_boarding.block_1
        if stageNumber < self.__currentStageNumber:
            blockState = BlockStates.PAST
        elif stageNumber == self.__currentStageNumber:
            blockState = BlockStates.CURRENT
        else:
            blockState = BlockStates.FUTURE
        block.setBlockState(blockState.value)
        monthNumber = self.__months[stageNumber]
        block.setMonth(R.strings.ten_year_countdown.on_boarding.timeline.dyn('month_{}'.format(monthNumber))())
        blockNumber = 'block_{}'.format(stageNumber)
        block.setTitleNumber(R.strings.ten_year_countdown.on_boarding.dyn(blockNumber, defaultNumber).number())
        block.setTitle(R.strings.ten_year_countdown.on_boarding.dyn(blockNumber, defaultNumber).title())
        block.setYears(R.strings.ten_year_countdown.on_boarding.dyn(blockNumber, defaultNumber).years())
        block.setFeaturesTitle(R.strings.ten_year_countdown.on_boarding.num(stageNumber, defaultNumber).features_title())
        features = block.getFeatures()
        for feature in R.strings.ten_year_countdown.on_boarding.dyn(blockNumber, defaultNumber).features.values():
            features.addResource(feature())

        features.invalidate()
        return block

    def __onForwardBtnClick(self):
        if self.__selectedPageId < self.__pagesCount - 1:
            self.__selectedPageId += 1
            self.__updateContent()
        else:
            self.destroyWindow()

    def __onBackBtnClick(self):
        if self.__selectedPageId > 0:
            self.__selectedPageId -= 1
            self.__updateContent()

    def __getRewardInfo(self):
        allQuests = self.__eventsCache.getAllQuests(filterFunc=lambda q: q.getID().startswith(EVENT_STYLE_MISSION_ID))
        isStyleInQuest = False
        isStyleInInventory = False
        for questData in allQuests.itervalues():
            questBonuses = questData.getBonuses()
            for bonus in questBonuses:
                if isinstance(bonus, CustomizationsBonus):
                    customizations = bonus.getCustomizations()
                    for bonusData in customizations:
                        customizationType = bonusData.get('custType')
                        if customizationType == 'style':
                            isStyleInQuest = True
                            item = bonus.getC11nItem(bonusData)
                            data = self.__itemsCache.items.inventory.getItems(GUI_ITEM_TYPE.CUSTOMIZATION, item.intCD)
                            invCount = sum([ count for count in data.itervalues() ])
                            if invCount:
                                isStyleInInventory = True
                            break

        return (isStyleInQuest, isStyleInInventory)

    def __onDisconnected(self):
        self.__isLogOff = True


class TenYearsOnboardingWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, currentStageNumber, isCurrentStageActive, months, blocksCount, callback=None):
        super(TenYearsOnboardingWindow, self).__init__(wndFlags=WindowFlags.OVERLAY, decorator=None, content=TenYearsOnboardingView(currentStageNumber, isCurrentStageActive, months, blocksCount, callback))
        return
