# Embedded file name: scripts/common/xmpp/Stanzas.py


def xmlText(text):
    t = text.replace(u'&', u'&#x26;')
    return t.replace(u'<', u'&#x3C;')


def getAttr(stanza, name):
    return stanza['attr'].get(name)


def getChild(stanza, name):
    for c in stanza['children']:
        if c['name'] == name:
            return c

    return None


def jidAttr(jid, name):
    attr = None
    if name == 'resource' or name == 'muc_user':
        if '/' in jid:
            attr = jid.split('/', 1)[-1]
    elif name == 'user':
        if '@' in jid:
            attr = jid.split('@', 1)[0]
    elif name in ('server', 'domain', 'host'):
        attr = jid.split('@', 1)[-1].split('/', 1)[0]
    elif name == 'bare':
        attr = jid.split('/', 1)[0]
    return attr or ''


STREAM_START = u"\n<stream:stream\n  xmlns='jabber:client'\n  xmlns:stream='http://etherx.jabber.org/streams'\n  to='%s'\n  version='1.0'>\n"
STREAM_END = u'\n</stream:stream>\n'
REGISTRATION_IQ = u"\n<iq type='get' id='reg1'>\n  <query xmlns='jabber:iq:register'/>\n</iq>\n"
REGISTRATION = u"\n<iq type='set' id='reg2'>\n  <query xmlns='jabber:iq:register'>\n    <username>%s</username>\n    <password>%s</password>\n  </query>\n</iq>\n"
AUTHENTICATION_MD5_START = u"\n<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl'\n         mechanism='DIGEST-MD5'/>\n"
AUTHENTICATION_MD5_RESPONSE = u"\n<response xmlns='urn:ietf:params:xml:ns:xmpp-sasl'>\n%s\n</response>\n"
AUTHENTICATION_MD5_BODY = u'username="%s",realm="%s",nonce="%s",cnonce="%s",nc=00000001,qop=auth,digest-uri="xmpp/%s",response=%s,charset=utf-8'
AUTHENTICATION_MD5_END = u"\n<response xmlns='urn:ietf:params:xml:ns:xmpp-sasl'/>\n"
AUTHENTICATION_PLAIN = u'\n<auth xmlns="urn:ietf:params:xml:ns:xmpp-sasl" mechanism="PLAIN">%s</auth>\n'
BIND_RESOURCE = u"\n<iq type='set' id='bind_2'>\n\t<bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'>\n\t\t<resource>%s</resource>\n\t</bind>\n</iq>\n"
SESSION = u"\n<iq type='set' id='sess_1'>\n\t<session xmlns='urn:ietf:params:xml:ns:xmpp-session'/>\n</iq>\n"
MESSAGE = u"\n<message from='%s' to='%s' xml:lang='en'>\n\t<body>%s</body>\n</message>\n"
QUERY_ROSTER = u"\n<iq from='%s' type='get' id='%s'>\n\t<query xmlns='jabber:iq:roster'/>\n</iq>\n"

def queryRoster(stanzaID, fromJID):
    return QUERY_ROSTER % (fromJID, stanzaID)


ROSTER_ADD = u"\n<iq from='%s' type='set' id='%s'>\n  <query xmlns='jabber:iq:roster'>\n    <item jid='%s' name='%s'/>\n  </query>\n</iq>\n<presence from='%s' to='%s' type='subscribe'/>\n"

def rosterAdd(stanzaID, senderJID, recipientJID):
    return ROSTER_ADD % (senderJID,
     stanzaID,
     recipientJID,
     recipientJID,
     senderJID,
     recipientJID)


ROSTER_SET_REPLY = u"\n<iq from='%s' to='%s' type='result' id='%s'/>\n"

def rosterSetReply(stanzaID, senderJID, recipientJID):
    return ROSTER_SET_REPLY % (senderJID, recipientJID, stanzaID)


ROSTER_DEL = u"\n<iq type='set' id='%s'>\n  <query xmlns='jabber:iq:roster'>\n    <item jid='%s' subscription='remove'/>\n  </query>\n</iq>\n"

def rosterDel(stanzaID, jidToRemove):
    return ROSTER_DEL % (stanzaID, jidToRemove)


SUBSCRIBE_ALLOW = u"\n<presence from='%s' to='%s' xml:lang='en' type='subscribed'/>\n"
QUERY_GATEWAY = u"\n<iq from='%s' to='%s' type='get' id='reg1'>\n\t<query xmlns='jabber:iq:register'/>\n</iq>\n"

def gatewayQuery(senderJID, transportDomain):
    return QUERY_GATEWAY % (senderJID, transportDomain)


REGISTER_GATEWAY = u"\n<iq from='%s' to='%s' type='set' id='%s'>\n\t<query xmlns='jabber:iq:register'>\n\t\t<username>%s</username>\n\t\t<password>%s</password>\n\t</query>\n</iq>\n"

def gatewayRegister(stanzaID, senderJID, gateway, username, password):
    return REGISTER_GATEWAY % (senderJID,
     gateway,
     stanzaID,
     username,
     password)


DEREGISTER_GATEWAY = u"\n<iq type='set' from='%s' to='%s' id='%s'>\n  <query xmlns='jabber:iq:register'>\n    <remove/>\n  </query>\n</iq>\n"

def gatewayDeregister(stanzaID, fromJID, toTransportJID):
    return DEREGISTER_GATEWAY % (fromJID, toTransportJID, stanzaID)


PRESENCE_SUBSCRIBE = u"<presence from='%s' to='%s' type='subscribe'/>"

def presenceSubscribe(fromJID, toJID):
    return PRESENCE_SUBSCRIBE % (fromJID, toJID)


IQ_BODY = u"\n<iq  id='%s' from='%s' to='%s' type='%s'>\n\t%s\n</iq>\n"
DISCO_ITEMS_ELEMENT = u"<query xmlns='http://jabber.org/protocol/disco#items'/>"

def queryDiscoItems(id, fromJID, to):
    return IQ_BODY % (id,
     fromJID,
     to,
     'get',
     DISCO_ITEMS_ELEMENT)


DISCO_INFO_ELEMENT = u"<query xmlns='http://jabber.org/protocol/disco#info'/>"

def queryDiscoInfo(id, fromJID, to):
    return IQ_BODY % (id,
     fromJID,
     to,
     'get',
     DISCO_INFO_ELEMENT)


MUC_CONFIGURATION_ELEMENT = u"<x xmlns='http://jabber.org/protocol/muc#owner'/>"

def mucConfigutation(id, from_jid, to_jid):
    return IQ_BODY % (id,
     from_jid,
     to_jid,
     'get',
     MUC_CONFIGURATION_ELEMENT)


MUC_CANCEL_CREATION_ELEMENT = u"\n<query xmlns='http://jabber.org/protocol/muc#owner'>\n\t<x xmlns='jabber:x:data' type='cancel'/>\n</query>\n"

def mucCancelCreation(id, from_jid, to_jid):
    return IQ_BODY % (id,
     from_jid,
     to_jid,
     'set',
     MUC_CANCEL_CREATION_ELEMENT)


MUC_CHANGE_AFFILATION_ELEMENT = u"\n<query xmlns='http://jabber.org/protocol/muc#admin'>\n\t%s\n</query>\n"
MUC_AFFILATION_ITEM = u"\n\t<item affiliation='%s' jid='%s'/>\n"

def mucChangeAffiliation(id, from_jid, to_jid, affiliations):
    items = u''
    for jid, affiliation in affiliations:
        items += MUC_AFFILATION_ITEM % (affiliation, jid)

    return IQ_BODY % (id,
     from_jid,
     to_jid,
     'set',
     MUC_CHANGE_AFFILATION_ELEMENT % items)


MUC_DESTROY_ROOM_ELEMENT = u"\n<query xmlns='http://jabber.org/protocol/muc#owner'>\n\t<destroy>\n\t\t<reason>%s</reason>\n\t</destroy>\n</query>\n"

def mucDestroyRoom(id, from_jid, to_jid, reason = ''):
    return IQ_BODY % (id,
     from_jid,
     to_jid,
     'set',
     MUC_DESTROY_ROOM_ELEMENT % reason)


MUC_QUERY_MEMBERS_ELEMENT = u"\n<query xmlns='http://jabber.org/protocol/muc#admin'>\n\t<item affiliation='%s'/>\n</query>\n"

def mucQueryMembers(id, from_jid, to_jid, members = u'member'):
    return IQ_BODY % (id,
     from_jid,
     to_jid,
     'get',
     MUC_QUERY_MEMBERS_ELEMENT % members)


def presence():
    return u'<presence/>'


PRESENCE_BODY = u"\n<presence from='%s' to='%s'>\n\t%s\n</presence>\n"
MUC_EXTENSION_ELEMENT = u"<x xmlns='http://jabber.org/protocol/muc'/>"

def mucPresence(from_jid, to_jid):
    return PRESENCE_BODY % (from_jid, to_jid, MUC_EXTENSION_ELEMENT)


PRESENCE_BODY_ID = u"\n<presence id='%s' from='%s' to='%s'>\n\t%s\n</presence>\n"

def mucPresenceId(id, from_jid, to_jid):
    return PRESENCE_BODY_ID % (id,
     from_jid,
     to_jid,
     MUC_EXTENSION_ELEMENT)


PRESENCE_BODY_TYPE = u"\n<presence from='%s' to='%s' type='%s'/>\n"

def mucPresenceType(from_jid, to_jid, type):
    return PRESENCE_BODY_TYPE % (from_jid, to_jid, type)


FORM_FIELD_VALUE = u"\n<field var='%s'>\n\t<value>%s</value>\n</field>\n"

def formField(name, value):
    return FORM_FIELD_VALUE % (name, value)


FORM_SUBMIT_ELEMENT = u"\n<query xmlns='http://jabber.org/protocol/muc#owner'>\n\t<x xmlns='jabber:x:data' type='submit'>\n\t\t<field var='FORM_TYPE'>\n\t\t<value>http://jabber.org/protocol/muc#roomconfig</value>\n\t\t</field>\n\t\t%s\n\t</x>\n</query>\n"

def submitForm(id, from_jid, to_jid, fields):
    return IQ_BODY % (id,
     from_jid,
     to_jid,
     'set',
     FORM_SUBMIT_ELEMENT % fields)


MESSAGE_BODY = u"\n<message from='%s' to='%s' type='%s'>\n\t<body>%s</body>\n</message>\n"

def mucMessage(from_jid, to_jid, msg):
    return MESSAGE_BODY % (from_jid,
     to_jid,
     'groupchat',
     msg)
