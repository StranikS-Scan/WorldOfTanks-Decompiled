# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/ext_constants.py


class XML_NAME_SPACE(object):
    BLOCKING_CMD = 'urn:xmpp:blocking'
    CHAT_STATES = 'http://jabber.org/protocol/chatstates'
    DELAY = 'urn:xmpp:delay'
    STANZA_ERROR = 'urn:ietf:params:xml:ns:xmpp-stanzas'
    RESULT_SET_MANAGEMENT = 'http://jabber.org/protocol/rsm'
    WG_EXTENSION = 'http://wargaming.net/xmpp#v2'
    WG_SPA_RESOLVER = 'http://wargaming.net/xmpp#spa-resolver'
    WG_STORAGE = 'http://wargaming.net/xmpp#storage'


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
    WG_EXTENSION = 'wgexts'
