# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/collection/account_settings.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COLLECTIONS_INTRO_SHOWN, COLLECTIONS_NOTIFICATIONS, COLLECTIONS_SECTION, COLLECTIONS_TAB_SHOWN_IDS, COLLECTIONS_TAB_SHOWN_NEW_ITEMS, COLLECTION_SHOWN_NEW_ITEMS, COLLECTION_SHOWN_NEW_ITEMS_COUNT, COLLECTION_SHOWN_NEW_REWARDS, COLLECTION_TUTORIAL_COMPLETED, LAST_SHOWN_NEW_COLLECTION, SHOWN_COMPLETED_COLLECTIONS, LAST_SHOWN_COLLECTION_BALANCE
from gui.collection.collections_constants import COLLECTIONS_UPDATED_ENTRY_SEEN, COLLECTION_RENEW_SEEN, COLLECTION_START_SEEN
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from helpers.dependency import replace_none_kwargs
from skeletons.gui.game_control import ICollectionsSystemController

def getCollectionsSettings():
    return AccountSettings.getUIFlag(COLLECTIONS_SECTION)


def setCollectionSettings(settings):
    AccountSettings.setUIFlag(COLLECTIONS_SECTION, settings)


def existsInCollectionsSection(settingName, collectionId, itemId):
    settings = getCollectionsSettings()
    settings[settingName].setdefault(collectionId, set())
    return itemId in settings[settingName][collectionId]


def addIntoCollectionsSection(settingName, collectionId, itemId):
    settings = getCollectionsSettings()
    settings[settingName].setdefault(collectionId, set())
    settings[settingName][collectionId].add(itemId)
    setCollectionSettings(settings)


def isRewardNew(collectionId, requiredCount):
    return not existsInCollectionsSection(COLLECTION_SHOWN_NEW_REWARDS, collectionId, requiredCount)


def setRewardShown(collectionId, requiredCount):
    addIntoCollectionsSection(COLLECTION_SHOWN_NEW_REWARDS, collectionId, requiredCount)


def isItemNew(collectionId, itemId):
    return not existsInCollectionsSection(COLLECTION_SHOWN_NEW_ITEMS, collectionId, itemId)


def setItemShown(collectionId, itemId):
    addIntoCollectionsSection(COLLECTION_SHOWN_NEW_ITEMS, collectionId, itemId)
    g_eventBus.handleEvent(events.CollectionsEvent(events.CollectionsEvent.NEW_ITEM_SHOWN), scope=EVENT_BUS_SCOPE.LOBBY)


def getShownNewItemsCount(collectionId):
    settings = getCollectionsSettings()
    settings[COLLECTION_SHOWN_NEW_ITEMS_COUNT].setdefault(collectionId, 0)
    return settings[COLLECTION_SHOWN_NEW_ITEMS_COUNT][collectionId]


def setShownNewItemsCount(collectionId, itemCount):
    settings = getCollectionsSettings()
    settings[COLLECTION_SHOWN_NEW_ITEMS_COUNT][collectionId] = itemCount
    setCollectionSettings(settings)


def isTutorialCompleted(collectionId):
    settings = getCollectionsSettings()
    return collectionId in settings[COLLECTION_TUTORIAL_COMPLETED]


def setCollectionTutorialCompleted(collectionId):
    settings = getCollectionsSettings()
    settings[COLLECTION_TUTORIAL_COMPLETED].add(collectionId)
    setCollectionSettings(settings)


def isIntroShown():
    settings = getCollectionsSettings()
    return settings.get(COLLECTIONS_INTRO_SHOWN, False)


def setIntroShown():
    settings = getCollectionsSettings()
    settings[COLLECTIONS_INTRO_SHOWN] = True
    setCollectionSettings(settings)


@replace_none_kwargs(collectionsSystem=ICollectionsSystemController)
def getCollectionsTabCounter(collectionsSystem=None):
    settings = getCollectionsSettings()
    collectionIDs = collectionsSystem.getCollectionIDs()
    newItemsSettings = settings.setdefault(COLLECTIONS_TAB_SHOWN_NEW_ITEMS, {})
    for collectionID in collectionIDs:
        newItemsSettings.setdefault(collectionID, 0)

    if settings.get(COLLECTIONS_TAB_SHOWN_IDS, set()).symmetric_difference(collectionIDs):
        return True
    for collectionID in collectionIDs:
        if newItemsSettings[collectionID] != collectionsSystem.getReceivedItemCount(collectionID):
            return True

    return False


@replace_none_kwargs(collectionsSystem=ICollectionsSystemController)
def resetCollectionsTabCounter(collectionsSystem=None):
    settings = getCollectionsSettings()
    collectionIDs = collectionsSystem.getCollectionIDs()
    settings.setdefault(COLLECTIONS_TAB_SHOWN_IDS, set())
    settings.setdefault(COLLECTIONS_TAB_SHOWN_NEW_ITEMS, {})
    settings[COLLECTIONS_TAB_SHOWN_IDS] = set(collectionIDs)
    for collectionID in collectionIDs:
        settings[COLLECTIONS_TAB_SHOWN_NEW_ITEMS][collectionID] = collectionsSystem.getReceivedItemCount(collectionID)

    setCollectionSettings(settings)
    g_eventBus.handleEvent(events.CollectionsEvent(events.CollectionsEvent.TAB_COUNTER_UPDATED), scope=EVENT_BUS_SCOPE.LOBBY)


def isCompletedCollectionShown(collectionId):
    settings = getCollectionsSettings()
    return collectionId in settings.get(SHOWN_COMPLETED_COLLECTIONS, set())


def setShownCompletedCollection(collectionId):
    settings = getCollectionsSettings()
    settings.setdefault(SHOWN_COMPLETED_COLLECTIONS, set())
    settings[SHOWN_COMPLETED_COLLECTIONS].add(collectionId)
    setCollectionSettings(settings)


@replace_none_kwargs(collectionsSystem=ICollectionsSystemController)
def isNewCollection(collectionId, collectionsSystem=None):
    settings = getCollectionsSettings()
    return settings.get(LAST_SHOWN_NEW_COLLECTION, 0) < collectionId == max(collectionsSystem.getCollectionIDs())


def setLastShownNewCollection(collectionId):
    settings = getCollectionsSettings()
    settings[LAST_SHOWN_NEW_COLLECTION] = collectionId
    setCollectionSettings(settings)


def isCollectionStartedSeen(collectionID):
    settings = AccountSettings.getNotifications(COLLECTIONS_NOTIFICATIONS)
    return collectionID in settings.get(COLLECTION_START_SEEN, [])


def setCollectionStartedSeen(collectionID):
    settings = AccountSettings.getNotifications(COLLECTIONS_NOTIFICATIONS)
    settings.setdefault(COLLECTION_START_SEEN, [])
    settings[COLLECTION_START_SEEN].append(collectionID)
    AccountSettings.setNotifications(COLLECTIONS_NOTIFICATIONS, settings)


def isCollectionsUpdatedEntrySeen():
    settings = AccountSettings.getNotifications(COLLECTIONS_NOTIFICATIONS)
    return settings.get(COLLECTIONS_UPDATED_ENTRY_SEEN, False)


def setCollectionsUpdatedEntrySeen():
    settings = AccountSettings.getNotifications(COLLECTIONS_NOTIFICATIONS)
    settings.setdefault(COLLECTIONS_UPDATED_ENTRY_SEEN, False)
    settings[COLLECTIONS_UPDATED_ENTRY_SEEN] = True
    AccountSettings.setNotifications(COLLECTIONS_NOTIFICATIONS, settings)


def isCollectionRenewSeen(collectionID):
    settings = AccountSettings.getNotifications(COLLECTIONS_NOTIFICATIONS)
    return collectionID in settings.get(COLLECTION_RENEW_SEEN, {}) and settings.get(COLLECTION_RENEW_SEEN, {}).get(collectionID, False)


def setCollectionRenewSeen(collectionID):
    settings = AccountSettings.getNotifications(COLLECTIONS_NOTIFICATIONS)
    settings.setdefault(COLLECTION_RENEW_SEEN, {})
    settings[COLLECTION_RENEW_SEEN][collectionID] = True
    AccountSettings.setNotifications(COLLECTIONS_NOTIFICATIONS, settings)


def getLastShownCollectionBalance(collectionId):
    settings = getCollectionsSettings()
    settings.setdefault(LAST_SHOWN_COLLECTION_BALANCE, {}).setdefault(collectionId, 0)
    return settings[LAST_SHOWN_COLLECTION_BALANCE][collectionId]


def setLastShownCollectionBalance(collectionId, itemCount):
    settings = getCollectionsSettings()
    settings.setdefault(LAST_SHOWN_COLLECTION_BALANCE, {})
    settings[LAST_SHOWN_COLLECTION_BALANCE][collectionId] = itemCount
    setCollectionSettings(settings)
