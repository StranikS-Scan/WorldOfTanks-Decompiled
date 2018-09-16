# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/badges.py
from web_client_api import w2c, W2CSchema
from gui.shared import event_dispatcher as shared_events

class BadgesWebApiMixin(object):

    @w2c(W2CSchema, 'badges')
    def openBadges(self, cmd):
        shared_events.showBadges()
