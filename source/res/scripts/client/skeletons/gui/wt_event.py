# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/wt_event.py
from skeletons.gui.game_control import IGameController

class IWTEventNotifications(IGameController):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError
