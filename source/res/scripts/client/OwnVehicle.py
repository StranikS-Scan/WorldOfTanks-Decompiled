# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/OwnVehicle.py
import logging
import BigWorld
from OwnVehicleBase import OwnVehicleBase
from Avatar import PlayerAvatar
_logger = logging.getLogger(__name__)

class OwnVehicle(OwnVehicleBase):

    def _avatar(self):
        return BigWorld.player()

    def _doLog(self, msg):
        _logger.info(msg)

    def _serverTime(self):
        return BigWorld.serverTime()
