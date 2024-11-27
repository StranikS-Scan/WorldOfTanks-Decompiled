# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/quests/ny_quests_view.py
from collections import namedtuple
import random
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_DAILY_QUESTS_HOVERED, NY_WEEKLY_QUESTS_HOVERED, NY_DAILY_MEDIA, NY_GENERATION_TIME, NY_DAILY_VIDEO_DAY_VISITED, NY_DAILY_VIDEO_VISITED_AT, NY_FIRST_VIDEO_VISITED
from gui.impl.backport import BackportTooltipWindow
from helpers import dependency
from helpers.time_utils import ONE_DAY, ONE_WEEK, WEEK_END
from gui.impl.gen.resources import R
from gui.impl.gui_decorators import args2params
from skeletons.gui.server_events import IEventsCache
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.quests.ny_quests_model import NyQuestsModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.quests.ny_quest_card_model import NyQuestCardModel
from new_year.gui.impl.lobby.new_year.quests.ny_quest_helper import updateBattleModes, updateQuests, getDaysFromStart, getDaysFromGeneration, getWeekFromStart, getDaysFromVisitVideo
from new_year.helpers.server_settings import getNewYearGeneralConfig
from new_year.gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from new_year.ny_constants import InternalViewState
from new_year.gui.impl.lobby.new_year.tooltips.ny_currency_tooltip import NyCurrencyTooltip
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.gui.impl.new_year.new_year_bonus_packer import getNewYearBonusPacker
from gui.shared.missions.packers.events import BattleQuestUIDataPacker
from skeletons.gui.shared import IItemsCache
Media = namedtuple('Media', 'videoUrl,soundUrl')
VEHICLE_LVL_INDEX = 2
MAIN_VIDEO = R.videos.new_year.quests.quest_giver_first_entry()
MAIN_SOUND = R.sounds.gui_video_ny_quest_giver_daily_01()
DAILY_MEDIA = [Media(R.videos.new_year.quests.quest_giver_daily_1(), R.sounds.gui_video_ny_quest_giver_daily_02()),
 Media(R.videos.new_year.quests.quest_giver_daily_2(), R.sounds.gui_video_ny_quest_giver_daily_03()),
 Media(R.videos.new_year.quests.quest_giver_daily_3(), R.sounds.gui_video_ny_quest_giver_daily_04()),
 Media(R.videos.new_year.quests.quest_giver_daily_4(), R.sounds.gui_video_ny_quest_giver_daily_05()),
 Media(R.videos.new_year.quests.quest_giver_daily_5(), R.sounds.gui_video_ny_quest_giver_daily_06()),
 Media(R.videos.new_year.quests.quest_giver_daily_6(), R.sounds.gui_video_ny_quest_giver_daily_07())]
WEEKLY_MEDIA = [Media(R.videos.new_year.quests.quest_giver_weekly_1(), R.sounds.gui_video_ny_quest_giver_weekly_01()),
 Media(R.videos.new_year.quests.quest_giver_weekly_2(), R.sounds.gui_video_ny_quest_giver_weekly_02()),
 Media(R.videos.new_year.quests.quest_giver_weekly_3(), R.sounds.gui_video_ny_quest_giver_weekly_03()),
 Media(R.videos.new_year.quests.quest_giver_weekly_4(), R.sounds.gui_video_ny_quest_giver_weekly_04()),
 Media(R.videos.new_year.quests.quest_giver_weekly_5(), R.sounds.gui_video_ny_quest_giver_weekly_05()),
 Media(R.videos.new_year.quests.quest_giver_weekly_6(), R.sounds.gui_video_ny_quest_giver_weekly_06())]
_logger = logging.getLogger(__name__)

class NyQuestsView(HistorySubModelPresenter):
    __slots__ = ('__config', '__dailyPrefix', '__weeklyPrefix', '__tooltipData')
    _INTERNAL_VIEW_STATE = InternalViewState.CHALLENGE
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewModel, *args):
        super(NyQuestsView, self).__init__(viewModel, *args)
        self.__config = getNewYearGeneralConfig()
        self.__dailyPrefix = self.__config.getDailyPrefix()
        self.__weeklyPrefix = self.__config.getWeeklyPrefix()
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return self.getViewModel()

    def getSettings(self, settings):
        return AccountSettings.getNewYear(settings)

    def setSettings(self, settings, value):
        AccountSettings.setNewYear(settings, value)

    def __generateVideoOrder(self):
        if not self.getSettings(NY_FIRST_VIDEO_VISITED):
            random.shuffle(DAILY_MEDIA)
            self.setSettings(NY_FIRST_VIDEO_VISITED, True)
            self.setSettings(NY_DAILY_MEDIA, DAILY_MEDIA)
        if getDaysFromGeneration() >= 7:
            newDate = self.getSettings(NY_GENERATION_TIME) + ONE_WEEK * (getDaysFromStart() / 7)
            self.setSettings(NY_GENERATION_TIME, newDate)
            random.shuffle(DAILY_MEDIA)
            self.setSettings(NY_DAILY_MEDIA, DAILY_MEDIA)

    def __checkVideoVisitedToday(self):
        if self.getSettings(NY_DAILY_VIDEO_DAY_VISITED) and getDaysFromVisitVideo() > 0:
            self.setSettings(NY_DAILY_VIDEO_DAY_VISITED, False)
            self.setSettings(NY_DAILY_VIDEO_VISITED_AT, self.getSettings(NY_DAILY_VIDEO_VISITED_AT) + ONE_DAY * getDaysFromStart())

    def __getCurrentVideoInfo(self, checkVisit):
        currentDaysDiff = getDaysFromStart() % WEEK_END
        if getDaysFromVisitVideo() > 0:
            self.setSettings(NY_DAILY_VIDEO_DAY_VISITED, False)
            self.setSettings(NY_DAILY_VIDEO_VISITED_AT, self.getSettings(NY_DAILY_VIDEO_VISITED_AT) + ONE_DAY * getDaysFromStart())
        if checkVisit and self.getSettings(NY_DAILY_VIDEO_DAY_VISITED):
            return (R.invalid(), R.invalid())
        if getDaysFromStart() <= 0:
            self.setSettings(NY_FIRST_VIDEO_VISITED, True)
            return (MAIN_VIDEO, MAIN_SOUND)
        if currentDaysDiff == 0:
            currentIndex = getWeekFromStart() - 1
            media = WEEKLY_MEDIA[currentIndex if currentIndex <= 5 else -1]
        else:
            media = self.getSettings(NY_DAILY_MEDIA)[currentDaysDiff - 1]
        return (media.videoUrl, media.soundUrl)

    def initialize(self, *args, **kwargs):
        super(NyQuestsView, self).initialize(*args, **kwargs)
        self.__setUpSettings()
        self.__updateData()

    def __getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        questId = event.getArgument('questId')
        return self.__tooltipData.get(questId, {}).get(tooltipId)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.new_year.lobby.new_year.tooltips.NyCurrencyTooltip():
            return NyCurrencyTooltip(NyCurrencyType.NYGIFTMACHINETOKEN)
        if R.views.dyn('gui_lootboxes').isValid() and contentID == R.views.dyn('gui_lootboxes').lobby.gui_lootboxes.tooltips.LootboxTooltip():
            tooltipData = self.__getTooltipData(event)
            return tooltipData.tooltip(*tooltipData.specialArgs)
        return super(NyQuestsView, self).createToolTipContent(event, contentID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = None
            if tooltipId is not None:
                window = BackportTooltipWindow(self.__getTooltipData(event), self.getParentWindow())
                window.load()
            return window
        else:
            return super(NyQuestsView, self).createToolTip(event)

    def _getEvents(self):
        return ((self.viewModel.onQuestHover, self.__onQuestHover), (self.viewModel.onReplayVideo, self.__onReplayVideo), (self.viewModel.onVideoFinished, self.__onVideoFinished))

    def __updateData(self):
        self.__generateVideoOrder()
        videoUrl, soundUrl = self.__getCurrentVideoInfo(checkVisit=True)
        with self.viewModel.transaction() as model:
            self.__updateQuests(model, model.getDailyQuests(), self.__dailyPrefix, NY_DAILY_QUESTS_HOVERED)
            self.__updateQuests(model, model.getWeeklyQuests(), self.__weeklyPrefix, NY_WEEKLY_QUESTS_HOVERED)
            model.setVideoUrl(videoUrl)
            model.setSoundUrl(soundUrl)
            self.setSettings(NY_DAILY_VIDEO_DAY_VISITED, True)

    def __updateQuests(self, model, questsArray, questFilter, nySetting):
        questsArray.clear()
        for questID, quest in sorted(self.__eventsCache.getAllQuests().iteritems()):
            if not quest.isStarted():
                continue
            if questID.startswith(questFilter):
                packer = BattleQuestUIDataPacker(quest, bonusPackerGetter=getNewYearBonusPacker)
                questModel = packer.pack(NyQuestCardModel())
                if questID in self.getSettings(nySetting):
                    questModel.setIsNew(False)
                self.__setLevels(model, quest)
                updateQuests(model, quest, questsArray, questModel, questFilter)
                updateBattleModes(quest, model.getBattleMode())
                self.__tooltipData[quest.getID()] = packer.getTooltipData()

        questsArray.invalidate()

    def __setLevels(self, model, quest):
        levels = quest.vehicleReqs.getConditions().find('vehicleDescr').parseFilters()[VEHICLE_LVL_INDEX]
        model.setMinVehicleLevel(min(levels))
        model.setMaxVehicleLevel(max(levels))

    @args2params(str)
    def __onQuestHover(self, questId):
        settings = self.getSettings(NY_DAILY_QUESTS_HOVERED)
        if questId.startswith(self.__dailyPrefix) and questId not in settings:
            settings[questId] = True
            self.setSettings(NY_DAILY_QUESTS_HOVERED, settings)
        settings = self.getSettings(NY_WEEKLY_QUESTS_HOVERED)
        if questId.startswith(self.__weeklyPrefix) and questId not in settings:
            settings[questId] = True
            self.setSettings(NY_WEEKLY_QUESTS_HOVERED, settings)

    def __onReplayVideo(self):
        videoUrl, soundUrl = self.__getCurrentVideoInfo(checkVisit=False)
        with self.viewModel.transaction() as model:
            model.setVideoUrl(videoUrl)
            model.setSoundUrl(soundUrl)

    def __onVideoFinished(self):
        with self.viewModel.transaction() as model:
            model.setVideoUrl(R.invalid())
            model.setSoundUrl(R.invalid())

    def __setUpSettings(self):
        if self.getSettings(NY_DAILY_QUESTS_HOVERED) is None:
            self.setSettings(NY_DAILY_QUESTS_HOVERED, {})
        if self.getSettings(NY_WEEKLY_QUESTS_HOVERED) is None:
            self.setSettings(NY_WEEKLY_QUESTS_HOVERED, {})
        if self.getSettings(NY_DAILY_MEDIA) is None:
            self.setSettings(NY_DAILY_MEDIA, DAILY_MEDIA)
        if self.getSettings(NY_DAILY_VIDEO_DAY_VISITED) is None:
            self.setSettings(NY_DAILY_VIDEO_DAY_VISITED, False)
        if self.getSettings(NY_FIRST_VIDEO_VISITED) is None:
            self.setSettings(NY_FIRST_VIDEO_VISITED, False)
        if not self.getSettings(NY_GENERATION_TIME):
            self.setSettings(NY_GENERATION_TIME, self.__config.getQuestsStartDay())
        if not self.getSettings(NY_DAILY_VIDEO_VISITED_AT):
            self.setSettings(NY_DAILY_VIDEO_VISITED_AT, self.__config.getQuestsStartDay())
        return
