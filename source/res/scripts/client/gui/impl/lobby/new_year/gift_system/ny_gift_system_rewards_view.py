# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/gift_system/ny_gift_system_rewards_view.py
import logging
import typing
from enum import Enum
from frameworks.wulf import ViewSettings, ViewStatus, WindowLayer
from gifts.gifts_common import GiftEventID
from gui import SystemMessages
from gui.clans.formatters import getClanAbbrevString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.gift_system.constants import HubUpdateReason
from gui.gift_system.mixins import GiftEventHubWatcher
from gui.gift_system.wrappers import OpenedGiftData
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_system.ny_gift_system_rewards_view_model import NyGiftSystemRewardsViewModel, State
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from gui.impl.lobby.new_year.tooltips.ny_shards_tooltip import NyShardsTooltip
from gui.impl.new_year.new_year_bonus_packer import packBonusModelAndTooltipData, getNewYearBonusPacker
from gui.impl.new_year.new_year_helper import backportTooltipDecorator, getGiftSystemCongratulationText
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import splitBonuses, getMergedBonusesFromDicts, getServiceBonuses
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.view_helpers import UsersInfoHelper
from gui.shared.utils import decorators
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from helpers.server_settings import serverSettingsChangeListener
from lootboxes_common import makeLootboxTokenID
from items.components.ny_constants import CurrentNYConstants
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from gui.impl.backport import TooltipData
_logger = logging.getLogger(__name__)
_MIN_BOXES_COUNT, _MAX_BOXES_COUNT = (1, 5)
_DEFAULT_GIFT_INFO = OpenedGiftData(0, {})
_BONUSES_ORDER = ('tmanToken',
 'customizations',
 CurrentNYConstants.FILLERS,
 'lootBox',
 CurrentNYConstants.TOY_FRAGMENTS)

def _keyBonusSortOrder(bonus):
    return _BONUSES_ORDER.index(bonus.getName()) if bonus.getName() in _BONUSES_ORDER else len(_BONUSES_ORDER)


def _getBonuses(rawBonuses):
    bonuses = []
    for name, value in rawBonuses.iteritems():
        bonuses.extend(getServiceBonuses(name, value))

    return bonuses


class RewardsTypes(Enum):
    GIFTS_OPENED = 'giftsOpened'
    SENDING_PROGRESSION = 'sendingProgression'
    SURPISE_FOR_SELF = 'surpriseforSelf'


class NyGiftSystemBaseRewarsdView(ViewImpl, GiftEventHubWatcher):
    __slots__ = ('_tooltips', '__rewardState')
    __nyController = dependency.descriptor(INewYearController)
    _GIFT_EVENT_ID = GiftEventID.NY_HOLIDAYS

    def __init__(self, settings, rewardState, *_, **__):
        super(NyGiftSystemBaseRewarsdView, self).__init__(settings)
        self._tooltips = {}
        self.__rewardState = rewardState

    @property
    def viewModel(self):
        return super(NyGiftSystemBaseRewarsdView, self).getViewModel()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(NyGiftSystemBaseRewarsdView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return NyShardsTooltip() if contentID == R.views.lobby.new_year.tooltips.NyShardsTooltip() else super(NyGiftSystemBaseRewarsdView, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        setOverlayHangarGeneral(True)
        self._addListeners()

    def _finalize(self):
        setOverlayHangarGeneral(False)
        self._removeListeners()
        self._tooltips.clear()

    def _onLoading(self, bonuses, *args, **kwargs):
        self.catchGiftEventHub(autoSub=False)
        with self.viewModel.transaction() as model:
            model.setState(self.__rewardState)
            self._updateRewards(model.rewards.getItems(), bonuses)

    def _addListeners(self):
        self.catchGiftEventHub()
        self.__nyController.onStateChanged += self.__onEventStateChanged

    def _removeListeners(self):
        self.releaseGiftEventHub()
        self.__nyController.onStateChanged -= self.__onEventStateChanged

    def _onGiftHubUpdate(self, reason, _=None):
        if reason == HubUpdateReason.SETTINGS and self.isGiftEventDisabled():
            self.destroyWindow()

    def _updateRewards(self, rewards, bonuses):
        self._tooltips.clear()
        packer = getNewYearBonusPacker()
        bonuses = sorted(splitBonuses(bonuses), key=_keyBonusSortOrder)
        rewards.clear()
        packBonusModelAndTooltipData(bonuses, rewards, packer, self._tooltips)
        rewards.invalidate()

    def __onEventStateChanged(self):
        if not self.__nyController.isEnabled():
            self.destroyWindow()


class NyGiftSystemSendingProgressionView(NyGiftSystemBaseRewarsdView):

    def __init__(self, settings, *_, **__):
        super(NyGiftSystemSendingProgressionView, self).__init__(settings, State.PROGRESSIONGIFT)


class NyGiftSystemSurpriseForSelfView(NyGiftSystemBaseRewarsdView):

    def __init__(self, settings, *_, **__):
        super(NyGiftSystemSurpriseForSelfView, self).__init__(settings, State.FORSELF)


class NyGiftSystemGiftsOpenedView(NyGiftSystemBaseRewarsdView, UsersInfoHelper):
    __slots__ = ('__giftsInfo', '__initialOpenedCount', '__lootBoxID', '__lootBoxToken')
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, settings, _, giftsInfo, lootBoxItem, openedCount):
        super(NyGiftSystemGiftsOpenedView, self).__init__(settings, State.ONEGIFT)
        self.__giftsInfo = giftsInfo[0] if giftsInfo else _DEFAULT_GIFT_INFO
        self.__initialOpenedCount = openedCount
        self.__lootBoxToken = makeLootboxTokenID(lootBoxItem.getID())
        self.__lootBoxID = lootBoxItem.getID()

    def onUserNamesReceived(self, names):
        spaID = self.__giftsInfo.senderID
        if spaID in names:
            self.__invalidateGiftSenderName(names[spaID], self.getUserClanAbbrev(spaID))

    def _initialize(self, *args, **kwargs):
        super(NyGiftSystemGiftsOpenedView, self)._initialize(*args, **kwargs)
        self.__updateLootBoxInformation()

    def _finalize(self):
        self.__giftsInfo = None
        super(NyGiftSystemGiftsOpenedView, self)._finalize()
        return

    def _onLoading(self, bonuses, *args, **kwargs):
        self.catchGiftEventHub(autoSub=False)
        self.__updateAll(bonuses, self.__initialOpenedCount)

    def _addListeners(self):
        super(NyGiftSystemGiftsOpenedView, self)._addListeners()
        self.viewModel.onOpenGifts += self.__onOpenGifts
        self.viewModel.onOpenOneGift += self.__onOpenOneGift
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        g_clientUpdateManager.addCallback('tokens.' + self.__lootBoxToken, self.__onTokensUpdate)

    def _removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.viewModel.onOpenOneGift -= self.__onOpenOneGift
        self.viewModel.onOpenGifts -= self.__onOpenGifts
        super(NyGiftSystemGiftsOpenedView, self)._removeListeners()

    def _onGiftHubUpdate(self, reason, _=None):
        if reason == HubUpdateReason.SETTINGS:
            self.__updateLootBoxInformation()

    def __getGiftsCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.__lootBoxToken)

    def __onOpenOneGift(self):
        self.__openBox(_MIN_BOXES_COUNT)

    def __onOpenGifts(self):
        self.__openBox(min(_MAX_BOXES_COUNT, self.__getGiftsCount()))

    @serverSettingsChangeListener('lootBoxes_config', 'isLootBoxesEnabled')
    def __onServerSettingChanged(self, _):
        self.__updateLootBoxInformation()

    def __onTokensUpdate(self, *_):
        self.__updateLootBoxInformation()

    @decorators.process('updating')
    def __openBox(self, countToOpen):
        lootBox = self.__itemsCache.items.tokens.getLootBoxByID(self.__lootBoxID)
        if lootBox is None:
            _logger.warning('LootBox %s is not defined, so skip open cmd', self.__lootBoxID)
            return
        else:
            result = yield LootBoxOpenProcessor(lootBox, countToOpen).request()
            if self.viewStatus != ViewStatus.LOADED:
                return
            if result and result.success:
                giftsInfo = result.auxData['giftsInfo']
                self.__giftsInfo = giftsInfo[0] if giftsInfo else _DEFAULT_GIFT_INFO
                self.__updateAll(result.auxData['bonus'], countToOpen)
            else:
                errorText = backport.text(R.strings.ny.giftSystem.award.serverError())
                SystemMessages.pushMessage(errorText, type=SystemMessages.SM_TYPE.GiftSystemError)
                self.viewModel.setIsServerError(True)
            return

    @replaceNoneKwargsModel
    def __invalidateGiftSenderName(self, userName, clanAbbrev, model=None):
        clanAbbrev = getClanAbbrevString(clanAbbrev) if clanAbbrev else ''
        model.setUserClanAbbrev(clanAbbrev)
        model.setUserName(userName)

    @replaceNoneKwargsModel
    def __updateAll(self, bonuses, openedCount=1, model=None):
        bonuses = _getBonuses(getMergedBonusesFromDicts(bonuses))
        model.setState(State.MULTIGIFTS if openedCount > 1 else State.ONEGIFT)
        self._updateRewards(model.rewards.getItems(), bonuses)
        self.__updateLootBoxInformation(model=model)
        self.__updateGiftSenderInformation(model)

    def __updateGiftSenderInformation(self, model):
        giftsMetaInfo = self.__giftsInfo.metaInfo
        model.setCongratulation(getGiftSystemCongratulationText(giftsMetaInfo.get('message_id', 0)))
        self.__updateGiftSenderName(model)

    def __updateGiftSenderName(self, model):
        spaID = self.__giftsInfo.senderID
        self.__invalidateGiftSenderName(self.getUserName(spaID), self.getUserClanAbbrev(spaID), model=model)
        self.syncUsersInfo()

    @replaceNoneKwargsModel
    def __updateLootBoxInformation(self, model=None):
        settings = self.__lobbyContext.getServerSettings()
        isLootBoxEnabled = settings.isLootBoxesEnabled() and settings.isLootBoxEnabled(self.__lootBoxID)
        model.setIsOpeningBoxEnabled(isLootBoxEnabled and not self.isGiftEventDisabled())
        model.setGiftCount(self.__getGiftsCount())


_VIEW_BY_TYPE_MAP = {RewardsTypes.GIFTS_OPENED: NyGiftSystemGiftsOpenedView,
 RewardsTypes.SENDING_PROGRESSION: NyGiftSystemSendingProgressionView,
 RewardsTypes.SURPISE_FOR_SELF: NyGiftSystemSurpriseForSelfView}

class NyGiftSystemRewardsWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, rewardsType, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.GiftSystemRewardsView(), model=NyGiftSystemRewardsViewModel(), args=args, kwargs=kwargs)
        super(NyGiftSystemRewardsWindow, self).__init__(content=_VIEW_BY_TYPE_MAP[rewardsType](settings, *args, **kwargs), layer=WindowLayer.OVERLAY)
