# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBVehicleDevComponent.py
import BigWorld
import constants
from debug_utils import LOG_WARNING, LOG_CODEPOINT_WARNING
from gui.battle_control import avatar_getter
from script_component.DynamicScriptComponent import DynamicScriptComponent

class HBVehicleDevComponent(DynamicScriptComponent):

    def setDevelopmentFeature(self, name, intArg=0, strArg=''):
        if not constants.HAS_DEV_RESOURCES:
            LOG_CODEPOINT_WARNING()
            return
        if avatar_getter.getPlayerVehicleID() != self.entity.id:
            LOG_WARNING('Cannot do dev feature not on own vehicle')
            return
        fullFeatureName = self.__getFullFeatureName(name)
        BigWorld.player().base.setDevelopmentFeature(0, fullFeatureName, intArg, strArg)

    def __getFullFeatureName(self, name):
        return '{}/{}'.format(self.keyName, name)
