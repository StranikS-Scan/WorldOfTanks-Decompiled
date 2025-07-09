# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/reward_screen.py
import typing
from collections import namedtuple
from gui.shared.view_helpers.UsersInfoHelper import BatchUsersInfoHelper
from gui_lootboxes.gui.bonuses.bonuses_packers import getRewardsBonusPacker, getMainRewardsBonusPacker
from gui_lootboxes.gui.bonuses.bonuses_sorter import sortBonuses
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootboxes_rewards_view_model import LootboxesRewardsViewModel
from gui_lootboxes.gui.impl.lobby.gui_lootboxes import RegisteredTooltips
from gui_lootboxes.gui.impl.lobby.gui_lootboxes import gui_helpers
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.sound import LOOT_BOXES_OVERLAY_SOUND_SPACE
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.compensation_tooltip import LootBoxesCompensationTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_key_tooltip import LootboxKeyTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
from constants import LOOTBOX_TOKEN_PREFIX, LOOTBOX_KEY_PREFIX
from frameworks.wulf import WindowFlags, WindowLayer, ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.collection.tooltips.collection_item_tooltip_view import CollectionItemTooltipView
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses
from gui.shared.event_dispatcher import selectVehicleInHangar
from gui_lootboxes.gui.lb_gui_constants import SHOW_GIFT_PHRASE_TAG
from helpers import dependency
from shared_utils import findFirst, first
from skeletons.gui.game_control import IGuiLootBoxesController, IGiftSystemController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Tuple, Dict, Optional
    from helpers.server_settings import GiftSystemConfig, GiftEventConfig
    from gui.shared.gui_items.loot_box import LootBox
SECONDARY_REWARDS_PROCESSORS = []
PlayerData = namedtuple('_PlayerData', ('name', 'clanAbbrev', 'spaID', 'isNameLoading'))

class LootBoxesRewardScreen(ViewImpl):
    __slots__ = ('__rewards', '__tooltipData', '__mainVehicleCd', '__lootbox', '__clientData', '__bonusData', '__key', '__userInfoHelper', '__giftsInfo', '__spaIdOfReceivedName')
    __itemsCache = dependency.descriptor(IItemsCache)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    __giftSystemController = dependency.descriptor(IGiftSystemController)
    _COMMON_SOUND_SPACE = LOOT_BOXES_OVERLAY_SOUND_SPACE

    def __init__(self, layoutID, rewards, lootbox, clientData):
        settings = ViewSettings(layoutID)
        settings.model = LootboxesRewardsViewModel()
        self.__userInfoHelper = BatchUsersInfoHelper()
        self.__tooltipData = {}
        self.__mainVehicleCd = None
        self.__rewards = rewards
        self.__lootbox = lootbox
        self.__clientData = clientData
        self.__bonusData = []
        self.__key = None
        self.__giftsInfo = None
        self.__spaIdOfReceivedName = None
        if clientData and clientData.get('openWithKey'):
            self.__key = self.__guiLootBoxes.getKeyByID(first(clientData.get('usedKeys', {}).keys()))
        if clientData and clientData.get('giftsInfo'):
            self.__giftsInfo = clientData.get('giftsInfo')
        for rewardDict in self.__rewards:
            for token, value in rewardDict.get('tokens', {}).items():
                if token.startswith(LOOTBOX_TOKEN_PREFIX) and value.get('count') < 0:
                    rewardDict['tokens'].pop(token)
                if token.startswith(LOOTBOX_KEY_PREFIX) and value.get('count', 0) == 0:
                    rewardDict['tokens'].pop(token)

        super(LootBoxesRewardScreen, self).__init__(settings)
        return

    def _finalize(self):
        self.__userInfoHelper.clearInvalidData()
        super(LootBoxesRewardScreen, self)._finalize()

    @property
    def viewModel(self):
        return super(LootBoxesRewardScreen, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        tooltipData = self.getTooltipData(event)
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip() and tooltipData:
            lootBoxID = tooltipData.get('lootBoxID')
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            return LootboxTooltip(lootBox)
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxKeyTooltip() and tooltipData:
            lootBoxKeyID = tooltipData.get('lootBoxKeyID')
            lootBoxKey = self.__guiLootBoxes.getKeyByID(lootBoxKeyID)
            return LootboxKeyTooltip(lootBoxKey)
        if tooltipData and isinstance(tooltipData.tooltip, dict):
            if contentID in tooltipData.tooltip:
                return tooltipData.tooltip[contentID](*tooltipData.specialArgs)
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.CompensationTooltip():
            if tooltipData:
                return LootBoxesCompensationTooltip(*tooltipData.specialArgs)
        elif contentID == R.views.lobby.collection.tooltips.CollectionItemTooltipView():
            if tooltipData:
                return CollectionItemTooltipView(*tooltipData.specialArgs)
        elif contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            bonuses = self.__bonusData[LootboxesRewardsViewModel.MAX_VISIBLE_REWARDS - 1:]
            return AdditionalRewardsTooltip(bonuses)
        if contentID in RegisteredTooltips.REGISTERED_SIMPLE_TOOLTIPS:
            view = RegisteredTooltips.REGISTERED_SIMPLE_TOOLTIPS.get(contentID)
            return view()
        if contentID in RegisteredTooltips.REGISTERED_TOOLTIPS:
            view = RegisteredTooltips.REGISTERED_TOOLTIPS.get(contentID)
            return view(event)
        return super(LootBoxesRewardScreen, self).createToolTipContent(event, contentID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(LootBoxesRewardScreen, self).createToolTip(event)

    def getTooltipData(self, event):
        index = event.getArgument(LootboxesRewardsViewModel.ARG_REWARD_INDEX)
        return self.__tooltipData.get(index, None)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.showVehicleInHangar, self.__showVehicleInHangar),
         (self.__userInfoHelper.onNamesReceived, self.__onSenderNameReceived),
         (self.viewModel.onRepeatOpen, self.__onRepeatOpen))

    def __onSenderNameReceived(self, receivedNames):
        name = receivedNames.get(self.__spaIdOfReceivedName)
        if name:
            clanAbbrev = self.__userInfoHelper.getUserClanAbbrev(self.__spaIdOfReceivedName)
            with self.viewModel.transaction() as vm:
                vm.setSenderName('{}{}'.format(name, clanAbbrev))
                vm.setIsNameLoading(False)
            self.__spaIdOfReceivedName = None
        return

    def _processGifts(self):
        senders = set()
        isNameLoading = False
        firstGift = self.__giftsInfo[0]
        senderID, messageID = firstGift[0], firstGift[1].get('message_id', 0)
        senderName, clanAbbrev = self.getSenderNameAndClanAbbrev(senderID)
        if not senderName:
            isNameLoading = True
        for senderSpaID, _ in self.__giftsInfo:
            senders.add(senderSpaID)

        return (len(senders), messageID, PlayerData(senderName, clanAbbrev, senderID, isNameLoading))

    def getSenderNameAndClanAbbrev(self, senderID):
        name = self.__userInfoHelper.getUserName(senderID)
        clanAbbrev = ''
        if not name:
            self.__spaIdOfReceivedName = senderID
            self.__userInfoHelper.syncUsersInfo()
        else:
            clanAbbrev = self.__userInfoHelper.getUserClanAbbrev(senderID)
        return (name, clanAbbrev)

    def __getEventID(self, lootboxID):
        settings = self.__giftSystemController.getSettings()
        for eventData in settings.events.itervalues():
            if lootboxID in eventData.giftItemIDs:
                return eventData.eventID

    def __getPhraseRes(self, lootboxID, phraseID):
        eventID = self.__getEventID(lootboxID)
        if eventID is None:
            return
        else:
            keeper = self.__giftSystemController.getEventHub(eventID).getKeeper()
            return keeper.getPhraseByID(phraseID)()

    def _onLoading(self, *args, **kwargs):
        super(LootBoxesRewardScreen, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            if self.__lootbox is not None:
                vm.setLootboxID(self.__lootbox.getID())
                vm.setLootBoxName(R.strings.lootboxes.userName.dyn(self.__lootbox.getUserNameKey(), R.invalid)())
                vm.setLootBoxIconName(self.__lootbox.getIconName())
                vm.setLootBoxCount(self.__lootbox.getInventoryCount())
                vm.setLootBoxMaxOpenCount(self.__lootbox.getManualMaxOpenCount())
                vm.setIsHiddenCount(self.__lootbox.isHiddenCount())
            if self.__key is not None:
                vm.keyType.setValue(self.__key.keyType)
                gui_helpers.fillKeyModel(vm.lootboxKey, self.__key)
            if self.__giftsInfo is not None and self.__lootbox.isTagExist(SHOW_GIFT_PHRASE_TAG):
                sendersCount, phraseID, playerData = self._processGifts()
                vm.setMoreSendersCount(sendersCount - 1)
                vm.setIsNameLoading(playerData.isNameLoading)
                vm.setSenderName('{}{}'.format(playerData.name, playerData.clanAbbrev))
                vm.setPhraseRes(self.__getPhraseRes(self.__lootbox.getID(), phraseID))
            self.__fillRewardsModel(self.__rewards, model=vm)
            vm.setLootBoxOpenCount(self.__clientData.get('countOfOpened', 0))
        return

    def __onClose(self):
        self.destroyWindow()

    def __showVehicleInHangar(self):
        if self.__mainVehicleCd is not None:
            window = self.getParentWindow()
            if window and window.parent:
                window.parent.destroy()
            else:
                self.destroyWindow()
            selectVehicleInHangar(self.__mainVehicleCd)
        return

    def __onRepeatOpen(self, args=None):
        gui_helpers.repeatOpen(args)
        self.destroyWindow()

    @replaceNoneKwargsModel
    def __fillRewardsModel(self, bonuses, model=None):
        rewardsList = model.getRewards()
        mainRewardsList = model.getMainRewards()
        lootboxCategory = self.__lootbox.getCategory() if self.__lootbox else None
        rewards = []
        for bonusesDict in bonuses:
            for bonusType, bonusValue in bonusesDict.items():
                rewards.extend(getNonQuestBonuses(bonusType, bonusValue))

        rewards = sortBonuses(mergeBonuses(rewards), self.__guiLootBoxes.getBonusesOrder(lootboxCategory))
        vehicleBonus = findFirst(lambda bonus: bonus.getName() == 'vehicles', rewards)
        if vehicleBonus:
            vehicle, _ = vehicleBonus.getVehicles()[0]
            self.__mainVehicleCd = vehicle.intCD
        mainRewards = rewards[:LootboxesRewardsViewModel.MAX_MAIN_REWARDS]
        rewards = rewards[LootboxesRewardsViewModel.MAX_MAIN_REWARDS:]
        if len(mainRewards) == LootboxesRewardsViewModel.MAX_MAIN_REWARDS:
            mainRewards[0], mainRewards[1] = mainRewards[1], mainRewards[0]
        for processor in SECONDARY_REWARDS_PROCESSORS:
            rewards = processor(rewards)

        self.__bonusData = rewards
        packBonusModelAndTooltipData(mainRewards, mainRewardsList, self.__tooltipData, getMainRewardsBonusPacker())
        packBonusModelAndTooltipData(rewards, rewardsList, self.__tooltipData, getRewardsBonusPacker(), len(mainRewardsList))
        rewardsList.invalidate()
        mainRewardsList.invalidate()
        return


class LootBoxesRewardScreenWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, rewards=None, lootBox=None, clientData=None, parent=None):
        super(LootBoxesRewardScreenWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=LootBoxesRewardScreen(R.views.gui_lootboxes.lobby.gui_lootboxes.LootboxRewardsView(), rewards=rewards, lootbox=lootBox, clientData=clientData), layer=WindowLayer.OVERLAY, parent=parent)
