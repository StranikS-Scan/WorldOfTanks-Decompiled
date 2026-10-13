# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/vehicle_selector.py
from __future__ import absolute_import
import logging
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from fort_rush.gui.impl.battle.fort_rush_vehicle_selector import FortRushVehicleSelectorView
from fort_rush.gui.battle_control.controllers.respawn_ctrl import ISpawnListener
_logger = logging.getLogger(__name__)

class FortRushVehicleSelectorComponent(InjectComponentAdaptor, ISpawnListener):

    def _makeInjectView(self):
        return FortRushVehicleSelectorView()

    def setSpawnPoints(self, points, pointId=None):
        pass

    def showSpawnPoints(self):
        pass

    def closeSpawnPoints(self):
        pass

    def updatePoint(self, vehicleId, pointId, prevPointId):
        pass

    def updateCloseTime(self, timeLeft, state):
        pass

    def onSelectPoint(self, pointId):
        pass

    def setSpawnType(self, spawnType):
        pass
