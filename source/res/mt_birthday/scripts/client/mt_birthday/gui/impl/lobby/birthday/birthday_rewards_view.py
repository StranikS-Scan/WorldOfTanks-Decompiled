# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/birthday_rewards_view.py
import logging
from typing import Dict
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from helpers import dependency
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from mt_birthday.gui.birthday_helpers.birthday_model_helpers import makeRewardModels
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.birthday_rewards_view_model import BirthdayRewardsViewModel
from gui.impl.pub import ViewImpl
from mt_birthday.gui.impl.gen.view_models.views.lobby.tooltips.gold_ticket_tooltip_model import GoldTicketTooltipModel
from mt_birthday.gui.shared.event_dispatcher import showGoldWagon, showGoldWagonTankMail
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class BirthdayRewardsView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)
    __gui = dependency.descriptor(IGuiLoader)
    __slots__ = ('__tooltipData', '__rewards', '__bloggerName', '__stage', '__isRewardSeen', '__isFinalReward', '__phraseID', '__spaID', '__isNameLoading', '__userInfoHelper')

    def __init__(self, layoutID, rewards, bloggerName, stage, isRewardSeen, isFinalReward, phraseID, spaID, isNameLoading):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = BirthdayRewardsViewModel()
        self.__tooltipData = {}
        self.__rewards = rewards
        self.__bloggerName = bloggerName or ''
        self.__stage = stage or 0
        self.__isRewardSeen = isRewardSeen
        self.__isFinalReward = isFinalReward
        self.__phraseID = phraseID or 0
        self.__spaID = spaID or 0
        self.__isNameLoading = isNameLoading or None
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
         (self.__userInfoHelper.onNamesReceived, self.__onNamesReceived))

    def __onNamesReceived(self, receivedSpaIDs):
        _logger.info('Received names; names: %r', receivedSpaIDs)
        if self.__spaID in receivedSpaIDs:
            bloggerName = receivedSpaIDs[self.__spaID]
            clanAbbrev = self.__userInfoHelper.getUserClanAbbrev(self.__spaID)
            bloggerFullName = '{}{}'.format(bloggerName, clanAbbrev)
            _logger.info('Nick is found name: %s', bloggerFullName)
            with self.viewModel.transaction() as tx:
                tx.setIsNameLoading(False)
                tx.setBloggerName(bloggerFullName)

    def __onClose(self):
        self.destroyWindow()

    @staticmethod
    def __goToContainers():
        from gui_lootboxes.gui.shared.event_dispatcher import showStorageView
        from gui_lootboxes.gui.storage_context.context import ReturnPlaces
        showStorageView(returnPlace=ReturnPlaces.TO_HANGAR)

    def __goToGoldCarriage(self):
        birthdayView = self.__gui.windowsManager.getViewByLayoutID(R.views.mt_birthday.lobby.birthday.BirthdayMainView())
        self.__onClose()
        if birthdayView is not None:
            showGoldWagonTankMail()
        else:
            showGoldWagon()
        return

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BirthdayRewardsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mt_birthday.lobby.tooltips.GoldTicketTooltip():
            goldTicketTooltipModel = GoldTicketTooltipModel()
            settings = ViewSettings(layoutID=R.views.mt_birthday.lobby.tooltips.GoldTicketTooltip(), model=goldTicketTooltipModel)
            return ViewImpl(settings)
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip():
            from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
            tooltipData = self.getTooltipData(event)
            lootBoxID = tooltipData.get('lootBoxID')
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            return LootboxTooltip(lootBox)
        return super(BirthdayRewardsView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def __buildModel(self):
        if self.__isNameLoading:
            self.__userInfoHelper.syncUsersInfo()
        with self.viewModel.transaction() as tx:
            tx.setBloggerName(self.__bloggerName)
            tx.setStage(self.__stage)
            tx.setIsRewardSeen(self.__isRewardSeen)
            tx.setIsFinalReward(self.__isFinalReward)
            tx.setPhraseID(self.__phraseID)
            tx.setIsNameLoading(self.__isNameLoading)
            mainRewards = tx.getMainRewards()
            mainRewards.clear()
            rewards = tx.getRewards()
            rewards.clear()
            makeRewardModels(self.__rewards, mainRewards, rewards, self.__tooltipData)


class BirthdayRewardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, rewards, bloggerName=None, stage=None, isRewardSeen=True, isFinalReward=False, phraseID=None, spaID=None, isNameLoading=None, parent=None):
        super(BirthdayRewardsViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BirthdayRewardsView(R.views.mt_birthday.lobby.birthday.BirthdayRewardsView(), rewards, bloggerName, stage, isRewardSeen, isFinalReward, phraseID, spaID, isNameLoading), layer=WindowLayer.FULLSCREEN_WINDOW, parent=parent)
