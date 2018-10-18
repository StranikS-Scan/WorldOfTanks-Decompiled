# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ZombieSpawnPoint.py
import logging
import BigWorld
_logger = logging.getLogger(__name__)

class ZombieSpawnPoint(BigWorld.UserDataObject):

    def __init__(self):
        BigWorld.UserDataObject.__init__(self)
        _logger.debug('ZombieSpawnPoint UDO init. Position: %s', self.position)
