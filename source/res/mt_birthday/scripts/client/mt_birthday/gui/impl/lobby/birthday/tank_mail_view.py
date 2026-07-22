# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/tank_mail_view.py
import logging
from collections import namedtuple
import typing
import th_async
from frameworks.wulf import ViewFlags, ViewSettings
from gui.gift_system.constants import GifterResponseState
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from helpers import dependency
from mt_birthday.gui.birthday_helpers.birthday_model_helpers import getBirthdayBonusPacker, birthdayBonusesSortKeyFunc, getPlayerOnlineStatus, getIsPlayerWaitResponse
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.progression_level import ProgressionLevel
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.user_item import UserItem
from mt_birthday.gui.impl.lobby.birthday.player_select_view import PlayerSelectViewWindow
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.tank_mail_view_model import TankMailViewModel
from gui.impl.pub import ViewImpl
from mt_birthday.gui.impl.lobby.tooltips.golden_ticket_tooltip import GoldTicketTooltip
from mt_birthday.gui.impl.lobby.tooltips.post_stamp_tooltip import PostStampTooltip
from mt_birthday.gui.shared.event_dispatcher import showQuestsToEarnStamps
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from mt_birthday.birthday_constants import BIRTHDAY_STAMP_CODE
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from mt_birthday.gui.impl.lobby.birthday.player_select_view import PlayerData
    from gui.impl.pub.dialog_window import DialogResult
    from gui.gift_system.wrappers import SendGiftResponse
_logger = logging.getLogger(__name__)
ProgressionAnimationData = namedtuple('_ProgressionAnimationData', 'currentPoints deltaPoints')

class TankMailView(ViewImpl):
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__tooltipData', '__selectedPlayers', '__pervProgressionPoints', '__queueAnimations', '__isAnimationStarted')

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = TankMailViewModel()
        self.__tooltipData = {}
        self.__selectedPlayers = []
        self.__pervProgressionPoints = None
        self.__queueAnimations = []
        self.__isAnimationStarted = False
        super(TankMailView, self).__init__(settings)
        return

    def _getEvents(self):
        return ((self.viewModel.onPlayerSelect, self.__onPlayerSelect),
         (self.viewModel.onPhraseChange, self.__onPhraseChange),
         (self.viewModel.onSent, self.__onSent),
         (self.viewModel.onTasks, self.__onTasks),
         (self.viewModel.onComponentDestroyed, self.__onComponentDestroyed),
         (self.viewModel.onAnimationEnded, self.__onAnimationEnded),
         (self.__tankBirthdayController.progression.onProgressionUpdated, self.__onProgressionUpdated),
         (self.__tankBirthdayController.giftSystem.updateStampBalance, self.__onUpdateStampCount))

    def __onAnimationEnded(self):
        with self.viewModel.transaction() as tx:
            progression = tx.progression
            currPoints = progression.getCurrentPoints()
            if self.__tankBirthdayController.progression.isInfinityLevel():
                progression.setInfinityDeltaFrom(currPoints)
            else:
                progression.setPointsDeltaFrom(currPoints)
            if not self.__tankBirthdayController.progression.isInfinityLevel():
                level, _ = self.__tankBirthdayController.progression.getLevelByPoints(currPoints)
                if level > progression.getCurrentLevel():
                    progression.setCurrentLevel(level)
        animationCount = len(self.__queueAnimations)
        if animationCount > 0:
            self.__startAnimation(self.__queueAnimations.pop(0))
        self.__isAnimationStarted = False

    def __onProgressionUpdated(self):
        _, infLevelConfig = self.__tankBirthdayController.progression.getInfinityLevel()
        infLevelMaxPoints = infLevelConfig['maxProgressionPoints']
        isLevelUp = False
        currentPoints = self.__tankBirthdayController.progression.getProgressionTokensCount()
        pervPoints = self.__pervProgressionPoints
        self.__pervProgressionPoints = currentPoints
        deltaPoints = currentPoints - pervPoints
        if deltaPoints > 0:
            currentLevel, currentLevelConfig = self.__tankBirthdayController.progression.getCurrentProgressionLevel()
            pervLevel, _ = self.__tankBirthdayController.progression.getLevelByPoints(min(pervPoints, infLevelMaxPoints))
            if currentLevel is not None and currentLevel - pervLevel > 0:
                isLevelUp = True
            if not isLevelUp:
                progressionAnimationData = ProgressionAnimationData(currentPoints, pervPoints)
                self.__queueAnimations.append(progressionAnimationData)
            else:
                currentLevelMinProgressionPoints = currentLevelConfig['minProgressionPoints']
                progressionAnimationData = ProgressionAnimationData(currentLevelMinProgressionPoints, pervPoints)
                self.__queueAnimations.append(progressionAnimationData)
                progressionAnimationData = ProgressionAnimationData(currentPoints, currentLevelMinProgressionPoints)
                self.__queueAnimations.append(progressionAnimationData)
        elif deltaPoints < 0:
            _, levelConfig = self.__tankBirthdayController.progression.getLevelByPoints(min(currentPoints, infLevelMaxPoints - 1))
            minProgressPoints = levelConfig['minProgressionPoints']
            self.__queueAnimations.append(ProgressionAnimationData(minProgressPoints, pervPoints))
            self.__queueAnimations.append(ProgressionAnimationData(currentPoints, minProgressPoints - 1))
        if not self.__isAnimationStarted:
            if self.__queueAnimations:
                self.__isAnimationStarted = True
                self.__startAnimation(self.__queueAnimations.pop(0))
        return

    def __startAnimation(self, progressionAnimationData):
        with self.viewModel.transaction() as tx:
            progression = tx.progression
            progression.setCurrentPoints(progressionAnimationData.currentPoints)
            if self.__tankBirthdayController.progression.isInfinityLevel():
                progression.setInfinityDeltaFrom(progressionAnimationData.deltaPoints)
            else:
                progression.setPointsDeltaFrom(progressionAnimationData.deltaPoints)

    def __onUpdateStampCount(self):
        self.updateCurrency()

    def __onComponentDestroyed(self):
        self.__pervProgressionPoints = self.__tankBirthdayController.progression.getProgressionTokensCount()
        self.__isAnimationStarted = False

    def _onLoading(self, *args, **kwargs):
        super(TankMailView, self)._onLoading()
        if self.__tankBirthdayController.giftSystem.isWaitResponseNeedUpdate():
            updatedAtAfter = self.__tankBirthdayController.giftSystem.getLastPlayerUpdatedAt()
            self.__tankBirthdayController.giftSystem.requestWaitResponse(getUpdatedAtAfter=updatedAtAfter)
        if self.isGiftSystemWork():
            self.updateCurrency()
            self.__tankBirthdayController.shufflePhrases()
            self.setPhraseID()
            self.buildProgression()

    def isGiftSystemWork(self):
        if not self.__tankBirthdayController.giftSystem.isGiftEventActive():
            self.__showPostError()
            return False
        self.__hidePostError()
        return True

    def __showPostError(self):
        with self.viewModel.transaction() as tx:
            tx.setIsPostError(True)

    def __hidePostError(self):
        with self.viewModel.transaction() as tx:
            tx.setIsPostError(False)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mt_birthday.lobby.tooltips.PostStampTooltip():
            return PostStampTooltip()
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
        return super(TankMailView, self).createToolTipContent(event, contentID)

    def __updateProgressionLevel(self):
        with self.viewModel.transaction() as tx:
            levelIdx, _ = self.__tankBirthdayController.progression.getCurrentProgressionLevel()
            if levelIdx:
                tx.progression.setCurrentLevel(levelIdx)

    def __setProgressionLevel(self, level):
        with self.viewModel.transaction() as tx:
            tx.progression.setCurrentLevel(level)

    def setPhraseID(self):
        with self.viewModel.transaction() as tx:
            tx.setPhraseID(self.__tankBirthdayController.getNextPhraseID())

    def fillSelectedUsers(self, selectedPlayers):
        with self.viewModel.transaction() as tx:
            selectedUsers = tx.getSelectedUsers()
            selectedUsers.clear()
            self.__selectedPlayers = []
            for player in selectedPlayers:
                playerEntity = self.__tankBirthdayController.userInfoHelper.users.getUser(player.spaID)
                userItem = UserItem()
                userItem.setUserID(player.spaID)
                userItem.setUserNickName(player.name)
                userItem.setClanTag(player.clanAbbrev)
                userItem.setIsWaitResponse(getIsPlayerWaitResponse(player.spaID))
                userItem.playerOnlineStatus.setStatus(getPlayerOnlineStatus(playerEntity))
                selectedUsers.addViewModel(userItem)
                self.__selectedPlayers.append(player)

            selectedUsers.invalidate()

    def updateCurrency(self):
        with self.viewModel.transaction() as tx:
            tx.setCurrencyCount(self.getCurrencyCount())

    def buildProgression(self):
        packer = getBirthdayBonusPacker()
        with self.viewModel.transaction() as tx:
            progression = tx.progression
            currentPoints = self.__tankBirthdayController.progression.getProgressionTokensCount()
            self.__pervProgressionPoints = currentPoints
            progression.setCurrentPoints(currentPoints)
            progression.setPointsDeltaFrom(currentPoints)
            levelIdx, levelConfig = self.__tankBirthdayController.progression.getCurrentProgressionLevel()
            progression.setCurrentLevel(levelIdx)
            levels = progression.getLevels()
            levels.clear()
            for levelIdx, levelConfig in self.__tankBirthdayController.progression.getSimpleLevels():
                levelModel = ProgressionLevel()
                levelModel.setNumber(levelIdx)
                levelModel.setMaxPoints(levelConfig['maxProgressionPoints'])
                levelModel.setSubstagesCount(levelConfig['maxProgressionPoints'] - levelConfig['minProgressionPoints'])
                levelRewards = levelConfig['bonuses']
                levelRewards.sort(key=birthdayBonusesSortKeyFunc)
                rewardsModels = levelModel.getRewards()
                rewardsModels.clear()
                packBonusModelAndTooltipData(levelRewards, rewardsModels, tooltipData=self.__tooltipData, packer=packer)
                rewardsModels.invalidate()
                levels.addViewModel(levelModel)

            levels.invalidate()
            _, infinityLevelConfig = self.__tankBirthdayController.progression.getInfinityLevel()
            progression.setInfinityMaxPoints(infinityLevelConfig['maxProgressionPoints'])
            progression.setInfinityStartPoints(infinityLevelConfig['minProgressionPoints'])
            progression.setInfinityDeltaFrom(currentPoints)
            progression.setInfinitySubstagesCount(infinityLevelConfig['maxProgressionPoints'] - infinityLevelConfig['minProgressionPoints'])
            levelRewards = infinityLevelConfig['bonuses']
            levelRewards.sort(key=birthdayBonusesSortKeyFunc)
            infinityRewardsModels = progression.getInfinityRewards()
            infinityRewardsModels.clear()
            packBonusModelAndTooltipData(levelRewards, infinityRewardsModels, tooltipData=self.__tooltipData, packer=packer)
            infinityRewardsModels.invalidate()

    def getCurrencyCount(self):
        return self.__tankBirthdayController.getStampCount()

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    @th_async.th_async
    def __onPlayerSelect(self):
        window = PlayerSelectViewWindow(previouslySelectedPlayers=self.__selectedPlayers)
        window.load()
        result = yield th_async.th_await(window.wait())
        _logger.info('PlayerSelectView return result=%s', result)
        self.fillSelectedUsers(result.data)

    def __onPhraseChange(self):
        with self.viewModel.transaction() as tx:
            chosenPhrase = self.__tankBirthdayController.getNextPhraseID()
            tx.setPhraseID(chosenPhrase)

    def __setIsSending(self, value):
        with self.viewModel.transaction() as tx:
            tx.setIsSending(value)

    def __clearSelectedUsers(self):
        with self.viewModel.transaction() as tx:
            selectedPlayers = tx.getSelectedUsers()
            selectedPlayers.clear()
            selectedPlayers.invalidate()
        self.__selectedPlayers = []

    def __showErrorOnSent(self):
        with self.viewModel.transaction() as tx:
            tx.setIsSentError(True)

    def __hideErrorOnSending(self):
        with self.viewModel.transaction() as tx:
            tx.setIsSentError(False)

    def __onSent(self):
        self.__hideErrorOnSending()
        self.__setIsSending(True)
        playersToSend = set()
        with self.viewModel.transaction() as tx:
            phraseID = tx.getPhraseID()
            selectedPlayers = tx.getSelectedUsers()
            for player in selectedPlayers:
                playersToSend.add(player.getUserID())

        self.__tankBirthdayController.giftSystem.sendGifts(BIRTHDAY_STAMP_CODE, playersToSend, phraseID, self.__onSentCallback)

    def __onSentCallback(self, result):
        if result.state is GifterResponseState.WEB_SUCCESS:
            for declinedReceiver in result.declinedReceivers:
                self.__tankBirthdayController.addBannedPlayersID(declinedReceiver)

            self.__clearSelectedUsers()
        else:
            self.__showErrorOnSent()
        self.__setIsSending(False)

    @staticmethod
    def __onTasks():
        showQuestsToEarnStamps()

    @property
    def viewModel(self):
        return super(TankMailView, self).getViewModel()
