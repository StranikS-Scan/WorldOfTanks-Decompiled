# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/ext_constants.py


class XML_NAME_SPACE(object):
    BLOCKING_CMD = 'urn:xmpp:blocking'
    CHAT_STATES = 'http://jabber.org/protocol/chatstates'
    DELAY = 'urn:xmpp:delay'
    STANZA_ERROR = 'urn:ietf:params:xml:ns:xmpp-stanzas'
    RESULT_SET_MANAGEMENT = 'http://jabber.org/protocol/rsm'
    DISCO_ITEMS = 'http://jabber.org/protocol/disco#items'
    WG_EXTENSION = 'http://wargaming.net/xmpp#v2'
    WG_CLIENT = 'http://wargaming.net/xmpp#client'
    WG_SPA_RESOLVER = 'http://wargaming.net/xmpp#spa-resolver'
    WG_STORAGE = 'http://wargaming.net/xmpp#storage'
    WG_PRIVATE_HISTORY = 'http://wargaming.net/xmpp#private-message-history'
    WG_MESSAGE_ID = 'http://wargaming.net/xmpp#message-id'
    WG_MUC_ROOMS = 'http://wargaming.net/xmpp#filter-muc-rooms-disco'


class XML_TAG_NAME(object):
    BLOCK_LIST = 'blocklist'
    BLOCK_ITEM = 'block'
    UNBLOCK_ITEM = 'unblock'
    MESSAGE = 'message'
    DELAY = 'delay'
    QUERY = 'query'
    LIST = 'list'
    ITEM = 'item'
    ERROR = 'error'
    SET = 'set'
    FILTER = 'filter'
    CRITERION = 'criterion'
    WG_EXTENSION = 'wgexts'
    WG_CLIENT = 'wgexts-client'
    WG_PRIVATE_HISTORY = 'private-history'
    WG_MESSAGE_ID = 'message-id'
