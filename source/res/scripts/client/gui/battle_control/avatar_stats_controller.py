# Embedded file name: scripts/client/gui/battle_control/avatar_stats_controller.py
import Event

class AvatarStatsController(object):

    def __init__(self):
        super(AvatarStatsController, self).__init__()
        self.__stats = {}
        self.__eManager = Event.EventManager()
        self.onUpdated = Event.Event(self.__eManager)

    def stop(self):
        self.__eManager.clear()
        self.__eManager = None
        return

    def getStats(self):
        return self.__stats

    def update(self, stats):
        self.__stats = stats
        self.onUpdated(stats)
