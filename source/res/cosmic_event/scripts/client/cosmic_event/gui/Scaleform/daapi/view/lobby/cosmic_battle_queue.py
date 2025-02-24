# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/Scaleform/daapi/view/lobby/cosmic_battle_queue.py
from gui.Scaleform.daapi.view.lobby.battle_queue import RandomQueueProvider

class CosmicEventQueueProvider(RandomQueueProvider):

    def processQueueInfo(self, qInfo):
        self._proxy.setPlayersTypeCDs(qInfo.get('vehTypeCompDescrs', {}))
        self._proxy.setSelectedVehicle()

    def _createCommonPlayerString(self, playerCount):
        pass
