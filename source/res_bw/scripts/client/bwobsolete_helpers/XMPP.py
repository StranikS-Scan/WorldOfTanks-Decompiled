# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_helpers/XMPP.py
import FantasyDemo
import FDGUI
import XMPPRoster

class AvatarRosterVisitor(XMPPRoster.XMPPRosterVisitor):

    def __init__(self):
        XMPPRoster.XMPPRosterVisitor.__init__(self)

    def onFriendAdd(self, friend, transport):
        msg = 'Added %s to the friends list.' % friend
        FantasyDemo.addChatMsg(-1, msg, FDGUI.TEXT_COLOUR_SYSTEM)

    def onFriendDelete(self, friend, transport):
        msg = 'Removed %s from the friends list.' % friend
        FantasyDemo.addChatMsg(-1, msg, FDGUI.TEXT_COLOUR_SYSTEM)

    def onFriendPresenceChange(self, friend, transport, oldPresence, newPresence):
        state = None
        if oldPresence == 'available' and newPresence == 'unavailable':
            state = 'gone offline'
        elif oldPresence == 'unavailable' and newPresence == 'available':
            state = 'come online'
        if state:
            msg = '%s has %s' % (friend, state)
            FantasyDemo.addChatMsg(-1, msg, FDGUI.TEXT_COLOUR_SYSTEM)
        return

    def onError(self, message):
        FantasyDemo.addChatMsg(-1, message, FDGUI.TEXT_COLOUR_SYSTEM)
