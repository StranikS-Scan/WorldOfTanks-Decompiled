# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/prb_control/races_queue.py
from gui.Scaleform.daapi.view.lobby.battle_queue import RandomQueueProvider

class RacesQueueProvider(RandomQueueProvider):

    def processQueueInfo(self, qInfo):
        count = qInfo.get('players', 0)
        self._proxy.setPlayersCount(count)

    def _createCommonPlayerString(self, playerCount):
        pass
