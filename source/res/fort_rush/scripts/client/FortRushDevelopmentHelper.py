# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/FortRushDevelopmentHelper.py
from __future__ import absolute_import
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from debug_utils import LOG_WARNING
from fort_rush_common.component_helpers import getInvaderComponent
from fort_rush_common.fort_rush_constants import FORT_RUSH_DEVELOPMENT_HELPER
from gui.battle_control import avatar_getter

class FortRushDevelopmentHelper(DynamicScriptComponent):

    def progressZone(self, zoneName):
        if not zoneName:
            LOG_WARNING('[FORT_RUSH] progressZone: zone name is required')
            return
        avatar = BigWorld.player()
        vehID = avatar.playerVehicleID
        avatar.base.setDevelopmentFeature(vehID, FORT_RUSH_DEVELOPMENT_HELPER + '/progressZone', vehID, zoneName)

    def progressCapturingZone(self):
        vehicle = avatar_getter.getPlayerVehicle()
        if vehicle is None:
            LOG_WARNING('[FORT_RUSH] progressCapturingZone: no vehicle attached')
            return
        else:
            invaderComp = getInvaderComponent(vehicle)
            if invaderComp is None:
                LOG_WARNING('[FORT_RUSH] progressCapturingZone: not capturing any zone')
                return
            self.progressZone(invaderComp.capturablePointName)
            return

    def captureZone(self, zoneName):
        avatar = BigWorld.player()
        vehID = avatar.playerVehicleID
        avatar.base.setDevelopmentFeature(vehID, FORT_RUSH_DEVELOPMENT_HELPER + '/captureZone', vehID, zoneName)

    def captureZoneEnemy(self, zoneName):
        avatar = BigWorld.player()
        vehID = avatar.playerVehicleID
        avatar.base.setDevelopmentFeature(vehID, FORT_RUSH_DEVELOPMENT_HELPER + '/captureZoneEnemy', vehID, zoneName)

    def neutralizeZone(self, zoneName):
        avatar = BigWorld.player()
        vehID = avatar.playerVehicleID
        avatar.base.setDevelopmentFeature(vehID, FORT_RUSH_DEVELOPMENT_HELPER + '/neutralizeZone', vehID, zoneName)

    def captureCurrentZone(self):
        avatar = BigWorld.player()
        vehID = avatar.playerVehicleID
        avatar.base.setDevelopmentFeature(vehID, FORT_RUSH_DEVELOPMENT_HELPER + '/captureCurrentZone', vehID, '')
