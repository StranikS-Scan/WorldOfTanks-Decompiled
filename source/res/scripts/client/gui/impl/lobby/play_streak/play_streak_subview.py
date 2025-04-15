# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/play_streak/play_streak_subview.py
import logging
from functools import partial
import typing
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import PlayStreak, AccountSettings
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.impl import backport
from gui.impl.backport.backport_tooltip import BackportTooltipWindow, TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_view_model import DailyTabs
from gui.impl.gen.view_models.views.lobby.daily.play_streak.play_streak_view_model import PlayStreakViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.play_streak.play_streak_bonus_packer import getPlayStreakBonusPacker
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
from gui.server_events.events_dispatcher import showDailyQuests
from gui.shared.event_dispatcher import showStylePreview, showStyleProgressionPreview, showVehiclePreview, showHangar
from helpers import dependency
from gui.impl.lobby.play_streak.play_streak_sounds import PLAYSTREAK_PREVIEW_SOUND_SPACE
from skeletons.gui.game_control import IGameSessionController, IPlayStreakController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional
    from frameworks.wulf.view.view_event import ViewEvent
    from frameworks.wulf.windows_system.window import Window
_logger = logging.getLogger(__name__)

class PlayStreakSubViewBase(ViewImpl):

    def activate(self):
        self._subscribe()
        self._update()

    def deactivate(self):
        self._unsubscribe()

    def _update(self):
        raise NotImplementedError


class PlayStreakSubView(PlayStreakSubViewBase):
    eventsCache = dependency.descriptor(IEventsCache)
    gameSession = dependency.descriptor(IGameSessionController)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __playStreakController = dependency.descriptor(IPlayStreakController)
    __slots__ = ('__parent', '__tooltipData')

    def __init__(self, parent, layoutID):
        viewSettings = ViewSettings(layoutID, ViewFlags.VIEW, PlayStreakViewModel())
        super(PlayStreakSubView, self).__init__(viewSettings)
        self.__parent = parent
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(PlayStreakSubView, self).getViewModel()

    @property
    def currentTabIdx(self):
        return self.__parent.getCurrentTabID()

    @property
    def tooltipData(self):
        return self.__tooltipData

    def createToolTipContent(self, event, contentID):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId:
            lootBoxId = self.__tooltipData.get(tooltipId).get('lootBoxID')
            if lootBoxId:
                return LootboxTooltip(self.itemsCache.items.tokens.getLootBoxByID(lootBoxId))
        return super(PlayStreakSubView, self).createToolTipContent(event=event, contentID=contentID)

    def createToolTip(self, event):
        missionParam = event.getArgument('tooltipId', '')
        if not missionParam:
            return super(PlayStreakSubView, self).createToolTip(event)
        else:
            missionParams = missionParam.rsplit(':', 1)
            if len(missionParams) != 2:
                tooltipData = self.__tooltipData.get(missionParam)
            else:
                missionId, tooltipId = missionParams
                tooltipsData = self.__tooltipData.get(missionId, {})
                tooltipData = tooltipsData.get(tooltipId)
            if tooltipData and isinstance(tooltipData, TooltipData):
                window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
                if window is not None:
                    window.load()
            else:
                window = super(PlayStreakSubView, self).createToolTip(event)
            return window

    def _update(self):
        with self.viewModel.transaction() as tx:
            self._updateModel(tx)

    def finalize(self):
        self._finalize()

    def _updateModel(self, model):
        with model.transaction() as tx:
            tx.setStreakLength(self.__playStreakController.getStreakProgress())
            self.__setIsFirstAppearance(model=tx)
            tx.setSkipDayCount(self.__playStreakController.getSkipDayCount())
            tx.setDailyWin(self.itemsCache.items.playStreak.getDailyConditionCompleted())
            tx.setIsPaused(self.lobbyContext.getServerSettings().playStreakConfig.isPaused)
            tx.setRedemptionDayCount(self.itemsCache.items.playStreak.getRedemptionDay())
            tx.setIsBlocked(self.__playStreakController.getIsBlocked())
            tx.setRedemptionMaxDayCount(self.lobbyContext.getServerSettings().playStreakConfig.daySkipSettings.get('freezeModeLength'))
            tx.setIsEnabled(self.lobbyContext.getServerSettings().playStreakConfig.isEnabled)
            modelBattleTypes = tx.getBattleTypes()
            modelBattleTypes.clear()
            modelBattleTypes.reserve(len(self.__playStreakController.getBattleTypes()))
            for battleType in self.__playStreakController.getBattleTypes():
                modelBattleTypes.addNumber(battleType)

            modelBattleTypes.invalidate()
            rewardsCalendar = self.__playStreakController.getRewardsCalendar()
            calendarArray = tx.getRewardsCalendar()
            calendarArray.clear()
            for day, bonuses, tags, additionalInfo in rewardsCalendar:
                calendarItemModel = tx.getRewardsCalendarType()()
                calendarItemModel.setDay(day)
                bonusArray = calendarItemModel.getRewards()
                bonusArray.reserve(len(bonuses))
                tagArray = calendarItemModel.getTags()
                tagArray.reserve(len(tags))
                additionalInfoArray = calendarItemModel.getAdditionalInfo()
                additionalInfoArray.reserve(len(tags))
                for tag in tags:
                    tagArray.addString(tag)

                for info in additionalInfo:
                    additionalInfoArray.addString(str(info))

                packBonusModelAndTooltipData(bonuses, bonusArray, self.__tooltipData, getPlayStreakBonusPacker())
                calendarArray.addViewModel(calendarItemModel)

            calendarArray.invalidate()

    def _onSyncCompleted(self, *_):
        with self.viewModel.transaction() as tx:
            self._updateModel(tx)

    def _getCallbacks(self):
        return (('tokens', self._onSyncCompleted),)

    def _getEvents(self):
        return ((self.eventsCache.onSyncCompleted, self._onSyncCompleted),
         (self.__playStreakController.onDataUpdated, self._update),
         (self.viewModel.onVehiclePreviewClick, self.__onVehiclePreviewClick),
         (self.viewModel.onShowVehicle, self.__onShowVehicle),
         (self.viewModel.onStylePreviewClick, self.__onStylePreviewClick))

    def __onVehiclePreviewClick(self, args):
        vehicleCD = int(args.get('vehicleCD', 0))
        if vehicleCD is None:
            return
        else:
            showVehiclePreview(vehicleCD, backBtnLabel=backport.text(R.strings.play_streak.window.playStreakPreview.backBtnLabel()), previewBackCb=self.__getPreviewCallback(), soundSpace=PLAYSTREAK_PREVIEW_SOUND_SPACE)
            return

    @args2params(int)
    def __onShowVehicle(self, vehCD):
        vehicle = self.itemsCache.items.getItemByCD(vehCD)
        if vehicle.isInInventory:
            showHangar()
            g_currentVehicle.selectVehicle(vehicle.invID)
            self.destroyWindow()

    def __onStylePreviewClick(self, args):
        styleCD = int(args.get('styleCD', 0))
        if styleCD == 0:
            return
        style = self.itemsCache.items.getItemByCD(styleCD)
        vehicleCD = getVehicleCDForStyle(style, itemsCache=self.itemsCache)
        if style.isProgressive:
            showStyleProgressionPreview(vehicleCD, style, style.getDescription(), backCallback=self.__getPreviewCallback(), backBtnDescrLabel=backport.text(R.strings.play_streak.window.playStreakPreview.backBtnLabel()), soundSpace=PLAYSTREAK_PREVIEW_SOUND_SPACE)
        else:
            showStylePreview(vehicleCD, style, style.getDescription(), backCallback=self.__getPreviewCallback(), backBtnDescrLabel=backport.text(R.strings.play_streak.window.playStreakPreview.backBtnLabel()), soundSpace=PLAYSTREAK_PREVIEW_SOUND_SPACE)

    def __getPreviewCallback(self):
        return partial(showDailyQuests, subTab=DailyTabs.SERIAL)

    @replaceNoneKwargsModel
    def __setIsFirstAppearance(self, model=None):
        streakProgress = self.__playStreakController.getStreakProgress()
        lastSeenCount = AccountSettings.getPlayStreak(PlayStreak.PLAY_STREAK_LAST_LEVEL_SEEN)
        if streakProgress != lastSeenCount and streakProgress:
            AccountSettings.setPlayStreak(PlayStreak.PLAY_STREAK_LAST_LEVEL_SEEN, streakProgress)
            model.setIsFirstAppearance(True)
        else:
            model.setIsFirstAppearance(False)
