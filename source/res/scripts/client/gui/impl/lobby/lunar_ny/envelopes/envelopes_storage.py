# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/envelopes/envelopes_storage.py
import typing
from adisp import process
from constants import NC_MESSAGE_PRIORITY
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.store_envelopes.received_envelope_model import ReceivedEnvelopeModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.store_envelopes.store_envelopes_model import StoreEnvelopesModel
from gui.impl.lobby.lunar_ny.envelopes.storage_envelopes_pagination import StorageEnvelopesPaginator
from gui.impl.lobby.lunar_ny.lunar_ny_base_main_view_component import BaseLunarNYViewComponent
from gui.impl.lobby.lunar_ny.lunar_ny_helpers import showEnvelopesHistoryView, showOpenEnvelopesAwardView
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from helpers import dependency
from helpers.server_settings import serverSettingsChangeListener
from lunar_ny import ILunarNYController
from lunar_ny.envelopes_storage_users_helper import EnvelopesStorageUsersHelper
from lunar_ny.lunar_ny_constants import MAIN_VIEW_INIT_CONTEXT_ENVELOPE_TYPE, EnvelopeTypes, MAIN_VIEW_INIT_CONTEXT_ENVELOPE_SENDER_ID
from lunar_ny.lunar_ny_sounds import LUNAR_NY_STORAGE_ENV_SOUND_SPACE
from messenger.proto.events import g_messengerEvents
from skeletons.gui.shared import IItemsCache
from uilogging.lunar_ny.loggers import LunarOpenEnvelopeLogger, LunarOpenCommonBtnLogger, LunarHistoryLogger
if typing.TYPE_CHECKING:
    from gui.gift_system.wrappers import GiftStorageData
_TYPE_PRIORITY = (EnvelopeTypes.PREMIUM_PAID, EnvelopeTypes.PAID, EnvelopeTypes.FREE)

class EnvelopesStorageView(BaseLunarNYViewComponent[StoreEnvelopesModel]):
    __slots__ = ('__currentType', '__dataPaginators', '__currentPageIdx', '__userInfoHelper')
    __lunarNYController = dependency.descriptor(ILunarNYController)
    __itemsCache = dependency.descriptor(IItemsCache)
    _SOUND_SPACE_SETTINGS = LUNAR_NY_STORAGE_ENV_SOUND_SPACE

    def __init__(self, viewModel, view):
        super(EnvelopesStorageView, self).__init__(viewModel, view)
        self.__currentType = _TYPE_PRIORITY[0]
        self.__dataPaginators = {}
        for envelopeType in _TYPE_PRIORITY:
            self.__dataPaginators[envelopeType] = StorageEnvelopesPaginator(envelopeType)

        self.__currentPageIdx = 0
        self.__userInfoHelper = EnvelopesStorageUsersHelper()

    def onLoading(self, initCtx, isActive):
        initialType = initCtx.get(MAIN_VIEW_INIT_CONTEXT_ENVELOPE_TYPE, None)
        self.__initHeader(initialType)
        initialSenderID = initCtx.get(MAIN_VIEW_INIT_CONTEXT_ENVELOPE_SENDER_ID, None)
        if isActive:
            self.__itemsCache.items.giftSystem.sortGiftStorage(self.__lunarNYController.receivedEnvelopes.getLootBoxIDByEnvelopeType(self.__currentType))
        if initialType is not None and initialSenderID is not None:
            self.__initWithSelect(initialSenderID)
        else:
            self.__defaultInit()
        super(EnvelopesStorageView, self).onLoading(initCtx, isActive)
        self.__lunarNYController.receivedEnvelopes.onReceivedEnvelopesUpdated += self.__onReceivedEnvelopesUpdated
        self.__userInfoHelper.onNamesReceived += self.__onUserNameReceived
        g_messengerEvents.onPluginConnected += self.__onChatPluginConnected
        return

    def update(self):
        self.__updateEnvelopesArray()
        with self._viewModel.transaction() as model:
            for envelopeType in _TYPE_PRIORITY:
                self.__setEnvelopesCount(envelopeType, self.__lunarNYController.receivedEnvelopes.getReceivedEnvelopesCountByType(self.__currentType), model=model)

    def setActive(self, isActive):
        if self._isActive != isActive and not isActive:
            self.__initHeader()
            self.__defaultInit()
        elif self._isActive != isActive and isActive:
            self.__updateViewedEnvelopesCount()
            self.__itemsCache.items.giftSystem.sortGiftStorage(self.__lunarNYController.receivedEnvelopes.getLootBoxIDByEnvelopeType(self.__currentType))
        super(EnvelopesStorageView, self).setActive(isActive)

    def finalize(self):
        super(EnvelopesStorageView, self).finalize()
        self.__userInfoHelper.clearInvalidData()

    def _addListeners(self):
        self._viewModel.onOpenHistoryView += self.__openHistoryView
        self._viewModel.onOpenEnvelopes += self.__openEnvelopes
        self._viewModel.onOpenEnvelopesByID += self.__openEnvelopesByID
        self._viewModel.onChangeEnvelopeType += self.__onChangeEnvelopeType
        self._viewModel.onSetPageIndex += self.__onSetPageIndex

    def _removeListeners(self):
        g_messengerEvents.onPluginConnected -= self.__onChatPluginConnected
        self.__userInfoHelper.onNamesReceived -= self.__onUserNameReceived
        self.__lunarNYController.receivedEnvelopes.onReceivedEnvelopesUpdated -= self.__onReceivedEnvelopesUpdated
        self._viewModel.onSetPageIndex -= self.__onSetPageIndex
        self._viewModel.onChangeEnvelopeType -= self.__onChangeEnvelopeType
        self._viewModel.onOpenEnvelopesByID -= self.__openEnvelopesByID
        self._viewModel.onOpenEnvelopes -= self.__openEnvelopes
        self._viewModel.onOpenHistoryView -= self.__openHistoryView

    def __openHistoryView(self):
        showEnvelopesHistoryView(parent=self._mainViewRef.getParentWindow())
        LunarHistoryLogger().logClick()

    @process
    def __openEnvelopes(self, args):
        count = args.get('count', 1)
        lootBox = self.__lunarNYController.receivedEnvelopes.getLootBoxByEnvelopeType(self.__currentType)
        if self.__lunarNYController.receivedEnvelopes.isOpenAvailability() and lootBox is not None:
            LunarOpenCommonBtnLogger().logOpenFromStorage(count, lootBox)
            result = yield LootBoxOpenProcessor(lootBox, count).request()
            if result.success:
                showOpenEnvelopesAwardView(result.auxData, self.__currentType)
            else:
                self.__pushOpenErrorSystemMsg()
        return

    @process
    def __openEnvelopesByID(self, args):
        count = args.get('count', 1)
        senderID = args.get('playerID', 0)
        lootBox = self.__lunarNYController.receivedEnvelopes.getLootBoxByEnvelopeType(self.__currentType)
        if self.__lunarNYController.receivedEnvelopes.isOpenAvailability() and lootBox is not None:
            LunarOpenEnvelopeLogger().logOpenFromStorage(count, lootBox)
            result = yield LootBoxOpenProcessor(lootBox, count, senderID).request()
            if result.success:
                showOpenEnvelopesAwardView(result.auxData, self.__currentType)
            else:
                self.__pushOpenErrorSystemMsg()
        return

    def __pushOpenErrorSystemMsg(self):
        text = backport.text(R.strings.lunar_ny.systemMessage.openEnvelopesAwards.error())
        SystemMessages.pushMessage(text, SM_TYPE.Error, priority=NC_MESSAGE_PRIORITY.MEDIUM)

    def __onChangeEnvelopeType(self, args):
        self.__currentType = EnvelopeTypes(args.get('envelopeType', _TYPE_PRIORITY[0].value))
        self.__currentPageIdx = 0
        self.__itemsCache.items.giftSystem.sortGiftStorage(self.__lunarNYController.receivedEnvelopes.getLootBoxIDByEnvelopeType(self.__currentType))
        self.__updateEnvelopesArray()
        with self._viewModel.transaction() as model:
            model.setPageIndex(self.__currentPageIdx)
            model.setPageCount(self.__getCurrentDataStorage().getPagesCount())
            model.setCurrentEnvelopeType(self.__currentType)

    def __updateEnvelopesArray(self):
        self.__userInfoHelper.clearInvalidData()
        with self._viewModel.transaction() as model:
            envelopesModel = model.getReceivedEnvelopes()
            paginator = self.__getCurrentDataStorage()
            envelopesModel.clear()
            for envelope in paginator.getDataFromPage(self.__currentPageIdx):
                envelopeModel = self.__getReceivedEnvelopeModel(envelope)
                envelopesModel.addViewModel(envelopeModel)

            if self.__userInfoHelper.hasInvalidName() and self.__userInfoHelper.proto.isConnected():
                self.__userInfoHelper.syncUsersInfo()
            envelopesModel.invalidate()

    def __initHeader(self, initialType=None):
        for envelopeType in reversed(_TYPE_PRIORITY):
            envelopeCount = self.__lunarNYController.receivedEnvelopes.getReceivedEnvelopesCountByType(envelopeType)
            if envelopeCount > 0:
                self.__currentType = envelopeType
            self.__setEnvelopesCount(envelopeType, envelopeCount, model=self._viewModel)

        if initialType is not None:
            self.__currentType = initialType
        self._viewModel.setCurrentEnvelopeType(self.__currentType)
        return

    def __setEnvelopesCount(self, envelopeType, envelopeCount, model):
        if envelopeType == EnvelopeTypes.PREMIUM_PAID:
            model.setPremiumPaidEnvelopesCount(envelopeCount)
        elif envelopeType == EnvelopeTypes.PAID:
            model.setPaidEnvelopesCount(envelopeCount)
        elif envelopeType == EnvelopeTypes.FREE:
            model.setFreeEnvelopesCount(envelopeCount)

    def __defaultInit(self):
        self.__currentPageIdx = 0
        self._viewModel.setPageIndex(self.__currentPageIdx)
        self._viewModel.setPageCount(self.__getCurrentDataStorage().getPagesCount())
        self.__updateEnvelopesArray()

    def __initWithSelect(self, initialSenderID):
        paginator = self.__getCurrentDataStorage()
        self.__currentPageIdx = paginator.findPageById(initialSenderID)
        self._viewModel.setPageIndex(self.__currentPageIdx)
        self._viewModel.setPageCount(paginator.getPagesCount())
        self.__updateEnvelopesArray()
        self._viewModel.setInitialSenderID(initialSenderID)

    def __onSetPageIndex(self, args):
        self.__currentPageIdx = int(args.get('pageIndex', 0))
        self.__updateEnvelopesArray()
        self._viewModel.setPageIndex(self.__currentPageIdx)

    def __updateViewedEnvelopesCount(self):
        self.__lunarNYController.receivedEnvelopes.markAllEnvelopesAsViewed()

    def __onReceivedEnvelopesUpdated(self):
        for paginator in self.__dataPaginators.values():
            paginator.update()

        self.__updateEnvelopesArray()
        with self._viewModel.transaction() as model:
            for envelopeType in _TYPE_PRIORITY:
                self.__setEnvelopesCount(envelopeType, self.__lunarNYController.receivedEnvelopes.getReceivedEnvelopesCountByType(envelopeType), model=model)
                if self._isActive:
                    self.__updateViewedEnvelopesCount()
                model.setPageCount(self.__getCurrentDataStorage().getPagesCount())

    @serverSettingsChangeListener('lootBoxes_config', 'isLootBoxesEnabled')
    def __onServerSettingsChange(self, diff):
        self._viewModel.setIsOpeningFeatureEnabled(self.__lunarNYController.receivedEnvelopes.isOpenAvailability())

    def __onUserNameReceived(self, name):
        with self._viewModel.transaction() as model:
            envelopesModel = model.getReceivedEnvelopes()
            for envelope in envelopesModel:
                playerID = envelope.getPlayerID()
                if playerID in name:
                    envelope.setPlayerName(name[playerID])

            envelopesModel.invalidate()

    def __getCurrentDataStorage(self):
        return self.__dataPaginators[self.__currentType]

    def __getReceivedEnvelopeModel(self, envelope):
        envelopeModel = ReceivedEnvelopeModel()
        envelopeModel.setPlayerID(envelope.senderID)
        envelopeModel.setPlayerName(self.__userInfoHelper.getUserName(envelope.senderID, withEmptyName=True))
        envelopeModel.setAmount(envelope.giftsCount)
        return envelopeModel

    def __onChatPluginConnected(self, _):
        if self.__userInfoHelper.proto.isConnected() and self.__userInfoHelper.hasInvalidName():
            self.__userInfoHelper.syncUsersInfo()
