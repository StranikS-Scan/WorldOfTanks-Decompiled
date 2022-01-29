# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/sub_controllers/received_envelopes.py
import typing
import Event
import SoundGroups
from account_helpers import AccountSettings
from account_helpers.AccountSettings import LUNAR_NY_RECEIVED_ENVELOPES_VIEWED
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.gift_system.constants import GIFTS_STORAGE_KEY
from gui.shared.gui_items.loot_box import ALL_LUNAR_NY_LOOT_BOX_TYPES, LunarNYLootBoxTypes
from helpers import dependency
from helpers.server_settings import serverSettingsChangeListener
from lunar_ny.lunar_ny_constants import ENVELOPE_TYPE_TO_LOOT_BOXES, EnvelopeTypes, ALL_ENVELOPE_TYPES, LOOT_BOX_TYPE_TO_ENVELOPE_TYPE
from lunar_ny.lunar_ny_sounds import LunarNYSoundEvents
from lunar_ny.sub_controllers import IBaseLunarSubController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.loot_box import LootBox

class ReceivedEnvelopesSubController(IBaseLunarSubController):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ('__lootBoxesTypeToID', '__giftsCount', 'onReceivedEnvelopesUpdated')

    def __init__(self, eManager):
        self.onReceivedEnvelopesUpdated = Event.Event(eManager)
        self.onNewEnvelopesReceived = Event.Event(eManager)
        self.__lootBoxesTypeToID = {}
        self.__giftsCount = {}

    def start(self):
        g_clientUpdateManager.addCallback('cache.giftsData', self.__onGiftStorageUpdated)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__lootBoxesTypeToID = self.__createLootBoxesTypeToIDMap()
        self.onReceivedEnvelopesUpdated()

    def stop(self):
        self.__giftsCount.clear()
        self.__lootBoxesTypeToID.clear()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        g_clientUpdateManager.removeObjectCallbacks(self)

    def isOpenAvailability(self):
        return self.__lobbyContext.getServerSettings().isLootBoxesEnabled()

    def getReceivedEnvelopesCount(self):
        return sum((self.getReceivedEnvelopesCountByType(lType) for lType in ENVELOPE_TYPE_TO_LOOT_BOXES))

    def getReceivedEnvelopesCountByType(self, envelopeType):
        if envelopeType in self.__giftsCount and self.__giftsCount[envelopeType]:
            return self.__giftsCount[envelopeType]
        self.__giftsCount[envelopeType] = self.__itemsCache.items.giftSystem.getGiftStorageDataCount(self.getLootBoxIDByEnvelopeType(envelopeType))
        return self.__giftsCount[envelopeType]

    def getLootBoxByEnvelopeType(self, envelopeType):
        lootBoxID = self.__lootBoxesTypeToID.get(ENVELOPE_TYPE_TO_LOOT_BOXES[envelopeType].value, None)
        return self.__itemsCache.items.tokens.getLootBoxByID(lootBoxID) if lootBoxID else None

    def getLootBoxIDByEnvelopeType(self, envelopeType):
        return self.__lootBoxesTypeToID.get(ENVELOPE_TYPE_TO_LOOT_BOXES[envelopeType].value, -1)

    def getEnvelopeTypeByLootBoxID(self, lootBoxID):
        for lType, lID in self.__lootBoxesTypeToID.iteritems():
            if lID == lootBoxID:
                return LOOT_BOX_TYPE_TO_ENVELOPE_TYPE[LunarNYLootBoxTypes(lType)]

        return None

    def pushNewReceivedEnvelopes(self, senderIDs, count, giftIDs):
        SoundGroups.g_instance.playSound2D(LunarNYSoundEvents.NEW_ENVELOPES_RECEIVED)
        self.onNewEnvelopesReceived(senderIDs, count, giftIDs)

    def getCountNewEnvelopes(self):
        viewedCount = sum(AccountSettings.getSettings(LUNAR_NY_RECEIVED_ENVELOPES_VIEWED).itervalues())
        return max(0, self.getReceivedEnvelopesCount() - viewedCount)

    def markAllEnvelopesAsViewed(self):
        AccountSettings.setSettings(LUNAR_NY_RECEIVED_ENVELOPES_VIEWED, {eType.value:self.getReceivedEnvelopesCountByType(eType) for eType in ALL_ENVELOPE_TYPES})

    @serverSettingsChangeListener('lootBoxes_config', 'isLootBoxesEnabled')
    def __onServerSettingsChange(self, _):
        self.__lootBoxesTypeToID = self.__createLootBoxesTypeToIDMap()

    def __createLootBoxesTypeToIDMap(self):
        config = self.__lobbyContext.getServerSettings().getSettings().get('lootBoxes_config', {})
        return {lootBox['type']:lID for lID, lootBox in config.iteritems() if lootBox['type'] in ALL_LUNAR_NY_LOOT_BOX_TYPES}

    def __onGiftStorageUpdated(self, diff):
        if GIFTS_STORAGE_KEY in diff:
            self.__giftsCount.clear()
            self.onReceivedEnvelopesUpdated()
