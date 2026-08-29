# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/generic_mechanics/bustle_feed/mechanic_interfaces.py
from __future__ import absolute_import

class IBustleFeedEventsLogic(object):
    onReloadTriggered = None

    def processReloadTriggered(self, shell, side, duration):
        raise NotImplementedError


class IBustleFeedListenerLogic(object):

    def onReloadTriggered(self, shell, side, duration):
        pass
