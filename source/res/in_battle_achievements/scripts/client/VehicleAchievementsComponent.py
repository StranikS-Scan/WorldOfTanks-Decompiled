# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: in_battle_achievements/scripts/client/VehicleAchievementsComponent.py
import logging
import BigWorld
from dossiers2.custom.records import DB_ID_TO_RECORD as ID2NAME
logger = logging.getLogger(__name__)

class VehicleAchievementsComponent(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(VehicleAchievementsComponent, self).__init__()
        logger.debug('[IN_BATTLE_ACHIEVEMENTS] VehicleAchievementsComponent has been initialized')

    def setSlice_achievements(self, changePath, oldValue):
        logger.debug('[IN_BATTLE_ACHIEVEMENTS] self.setSlice_achievements: achievements: %s, changePath: %s', self.achievements, changePath)
        startIndex, endIndex = changePath[-1]
        receivedAchievements = self.achievements[startIndex:endIndex]
        revokedAchievements = oldValue
        logger.debug('[IN_BATTLE_ACHIEVEMENTS] Received: %s - Revoked: %s', ', '.join([ ID2NAME[item][1] for item in receivedAchievements if item in ID2NAME.iterkeys() ]), ', '.join([ ID2NAME[item][1] for item in revokedAchievements if item in ID2NAME.iterkeys() ]))
