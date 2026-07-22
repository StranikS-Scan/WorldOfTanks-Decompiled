# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/birthday_rewards_view.py
import logging
from typing import Dict
import SoundGroups
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from helpers import dependency
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from mt_birthday.gui.birthday_helpers.birthday_model_helpers import makeRewardModels
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.birthday_rewards_view_model import BirthdayRewardsViewModel
from gui.impl.pub import ViewImpl
from mt_birthday.gui.impl.lobby.tooltips.golden_ticket_tooltip import GoldTicketTooltip
from mt_birthday.gui.shared.event_dispatcher import showGoldWagon, showTicketExchange
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from mt_birthday.gui.impl.sounds import BIRTHDAY_REWARD_SCREEN_SOUND_SPACE, BirthdaySoundEvents
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class BirthdayRewardsView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)
    __gui = dependency.descriptor(IGuiLoader)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _COMMON_SOUND_SPACE = BIRTHDAY_REWARD_SCREEN_SOUND_SPACE
    __slots__ = ('__tooltipData', '__rewards', '__bloggerName', '__stage', '__isRewardSeen', '__isFinalReward', '__phraseID', '__spaID', '__isNameLoading', '__userInfoHelper', '__isAllChallengesComplete', '__isOnlyBadge', '__replyGiftsCount')

    def __init__(self, layoutID, rewards, bloggerName, stage, isRewardSeen, isFinalReward, phraseID, spaID, isNameLoading, isAllChallengesComplete, isOnlyBadge, replyGiftsCount):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = BirthdayRewardsViewModel()
        self.__tooltipData = {}
        self.__rewards = rewards
        self.__bloggerName = bloggerName or ''
        self.__stage = stage or 0
        self.__isRewardSeen = isRewardSeen
        self.__isFinalReward = isFinalReward
        self.__isAllChallengesComplete = isAllChallengesComplete
        self.__phraseID = phraseID or 1
        self.__spaID = spaID or 0
        self.__isNameLoading = isNameLoading or None
        self.__isOnlyBadge = isOnlyBadge or False
        self.__replyGiftsCount = replyGiftsCount or 0
        self.__userInfoHelper = self.__tankBirthdayController.userInfoHelper
        super(BirthdayRewardsView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BirthdayRewardsView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.__buildModel()
        super(BirthdayRewardsView, self)._onLoading(*args, **kwargs)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.goToContainers, self.__goToContainers),
         (self.viewModel.goToGoldCarriage, self.__goToGoldCarriage),
         (self.viewModel.goToTicketExchange, self.__goToTicketExchange),
         (self.__userInfoHelper.onNamesReceived, self.__onNamesReceived))

    def __onNamesReceived(self, receivedSpaIDs):
        _logger.info('Received names; names: %r', receivedSpaIDs)
        if self.__spaID in receivedSpaIDs:
            bloggerName = receivedSpaIDs[self.__spaID]
            clanAbbrev = self.__userInfoHelper.getUserClanAbbrev(self.__spaID)
            bloggerFullName = self.__lobbyContext.getPlayerFullName(bloggerName, clanAbbrev=clanAbbrev)
            _logger.info('Nick is found name: %s', bloggerFullName)
            with self.viewModel.transaction() as tx:
                tx.setIsNameLoading(False)
                tx.setBloggerName(bloggerFullName)

    def __onClose(self):
        self.destroyWindow()

    def __goToContainers(self):
        from gui_lootboxes.gui.shared.event_dispatcher import showStorageView
        from gui_lootboxes.gui.storage_context.context import ReturnPlaces
        view = self.gui.windowsManager.getViewByLayoutID(R.views.mt_birthday.lobby.birthday.BirthdayMainView())
        self.soundManager.setState(BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL, BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL_OFF)
        if view is None:
            showStorageView(returnPlace=ReturnPlaces.TO_HANGAR)
        else:
            showStorageView(returnPlace=ReturnPlaces.TO_BIRTHDAY, closeCallback=self.__lootboxCloseCallback)
        return

    def __lootboxCloseCallback(self):
        self.soundManager.setState(BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL, BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL_ON)
        self.__onClose()

    def __goToGoldCarriage(self):
        self.__onClose()
        showGoldWagon()

    def __goToTicketExchange(self):
        self.__onClose()
        showTicketExchange()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BirthdayRewardsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mt_birthday.lobby.tooltips.GoldTicketTooltip():
            return GoldTicketTooltip()
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip():
            from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
            from mt_birthday.gui.impl.lobby.tooltips.birthday_lootbox_tooltip_extended import BirthdayLootboxTooltipExtended
            tooltipData = self.getTooltipData(event)
            lootBoxID = tooltipData.get('lootBoxID')
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            if lootBox.isExtendedTooltip():
                return BirthdayLootboxTooltipExtended(lootBox)
            return LootboxTooltip(lootBox)
        return super(BirthdayRewardsView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def __buildModel(self):
        phraseID = self.__phraseID
        if 'c_{}'.format(phraseID) not in R.strings.player_phrases.player.keys():
            phraseID = 1
        if self.__isNameLoading:
            self.__userInfoHelper.syncUsersInfo()
        with self.viewModel.transaction() as tx:
            tx.setBloggerName(self.__bloggerName)
            tx.setStage(self.__stage)
            tx.setIsRewardSeen(self.__isRewardSeen)
            tx.setIsFinalReward(self.__isFinalReward)
            tx.setIsAllChallengesComplete(self.__isAllChallengesComplete)
            tx.setPhraseID(phraseID)
            tx.setIsNameLoading(self.__isNameLoading)
            tx.setIsOnlyBadge(self.__isOnlyBadge)
            tx.setReplyGiftsCount(self.__replyGiftsCount)
            tx.setIsGoldWagonEnabled(self.__tankBirthdayController.isGoldWagonEnabled())
            tx.setIsTicketExchangeEnabled(self.__tankBirthdayController.isTicketExchangeEnabled())
            mainRewards = tx.getMainRewards()
            mainRewards.clear()
            rewards = tx.getRewards()
            rewards.clear()
            makeRewardModels(self.__rewards, mainRewards, rewards, self.__tooltipData)

    def _finalize(self):
        SoundGroups.g_instance.playSound2D(BirthdaySoundEvents.REWARD_SCREEN_ANIMATION_SKIP)
        super(BirthdayRewardsView, self)._finalize()


class BirthdayRewardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, rewards, bloggerName=None, stage=None, isRewardSeen=True, isFinalReward=False, phraseID=None, spaID=None, isNameLoading=None, isAllChallengesComplete=False, isOnlyBadge=False, replyGiftsCount=None, parent=None):
        super(BirthdayRewardsViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BirthdayRewardsView(R.views.mt_birthday.lobby.birthday.BirthdayRewardsView(), rewards, bloggerName, stage, isRewardSeen, isFinalReward, phraseID, spaID, isNameLoading, isAllChallengesComplete, isOnlyBadge, replyGiftsCount), layer=WindowLayer.FULLSCREEN_WINDOW, parent=parent)
