# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/collection/collections_constants.py
from collections_common import COLLECTIONS_PREFIX
COLLECTION_ITEM_BONUS_NAME = 'collectionItem'
COLLECTION_ITEM_PREFIX_NAME = COLLECTIONS_PREFIX + '_item'
COLLECTION_ITEM_TOKEN_PREFIX_NAME = 'cllc:item:'
COLLECTION_ITEM_RES_KEY_TEMPLATE = '{}_{}_{}'
COLLECTION_RES_PREFIX = 'collection_'
COLLECTION_START_EVENT_TYPE = 'collectionStart'
COLLECTIONS_UPDATED_ENTRY_EVENT_TYPE = 'collectionsUpdatedEntry'
COLLECTIONS_RENEW_EVENT_TYPE = 'collectionsRenew'
COLLECTION_START_SEEN = 'collectionStartNotification'
COLLECTIONS_UPDATED_ENTRY_SEEN = 'collectionsUpdatedEntryNotification'
COLLECTION_RENEW_SEEN = 'collectionRenewNotification'

def cllcTokenToEntitlement(tokenID):
    try:
        _, _, collectionId, itemId = tokenID.split(':')
        return COLLECTION_ITEM_PREFIX_NAME + '_{}_{}'.format(collectionId, itemId)
    except ValueError:
        return None

    return None
