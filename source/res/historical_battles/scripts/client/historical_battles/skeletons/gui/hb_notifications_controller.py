# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/skeletons/gui/hb_notifications_controller.py
from skeletons.gui.game_control import IGameController

class IHBEventNotifications(IGameController):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError
