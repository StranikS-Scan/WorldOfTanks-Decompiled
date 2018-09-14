# Embedded file name: scripts/client/messenger/proto/xmpp/wrappers.py
from collections import namedtuple
XMPPChannelData = namedtuple('XMPPChannelData', ('name', 'msgType'))
XMPPMessageData = namedtuple('XMPPChannelData', ('accountDBID', 'accountName', 'text', 'sentAt'))
