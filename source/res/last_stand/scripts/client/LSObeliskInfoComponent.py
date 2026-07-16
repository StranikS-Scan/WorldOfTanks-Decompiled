# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSObeliskInfoComponent.py
from __future__ import absolute_import
import BigWorld
from Event import Event
from helpers import isPlayerAvatar
from script_component.DynamicScriptComponent import DynamicScriptComponent

class ObeliskInfoStates(object):
    SHOW = 'show'
    HIT = 'hit'
    DEATH = 'death'
    HIDE = 'hide'


class LSObeliskInfoComponent(DynamicScriptComponent):

    def __init__(self):
        super(LSObeliskInfoComponent, self).__init__()
        self.onStateChange = Event()
        self.onObeliskObserved = Event()

    def onDestroy(self):
        self.onStateChange.clear()
        super(LSObeliskInfoComponent, self).onDestroy()

    def set_isPresent(self, _):
        if self.isPresent:
            self.onStateChange(ObeliskInfoStates.SHOW)
        else:
            self.onStateChange(ObeliskInfoStates.HIDE)

    def set_observedObeliskCD(self, _):
        self.onObeliskObserved(self.observedObeliskCD)

    def onDamageReceived(self):
        if self.isPresent:
            self.onStateChange(ObeliskInfoStates.HIT)

    def onDeath(self):
        self.onStateChange(ObeliskInfoStates.DEATH)

    @staticmethod
    def getInstance():
        if not isPlayerAvatar():
            return None
        else:
            player = BigWorld.player()
            return None if not player or not player.arena else getattr(player.arena.arenaInfo, 'LSObeliskInfoComponent', None)

    def _onAvatarReady(self):
        super(LSObeliskInfoComponent, self)._onAvatarReady()
        self.onObeliskObserved(self.observedObeliskCD)
