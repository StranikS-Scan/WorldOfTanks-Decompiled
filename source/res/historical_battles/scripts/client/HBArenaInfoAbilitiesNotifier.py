# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBArenaInfoAbilitiesNotifier.py
import BigWorld
from helpers import dependency
from items import vehicles
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider

class HBArenaInfoAbilitiesNotifier(DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def notifyLaunchPosition(self, equipmentId, position, direction, launchTime, duration):
        delay = launchTime - BigWorld.serverTime()
        time = duration - delay
        equipment = vehicles.g_cache.equipments()[equipmentId]
        self.__showGuiMarker(equipment, position, direction, time)

    def __showGuiMarker(self, equipment, position, direction, time):
        ctrl = self.__guiSessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.showMarker(equipment, position, direction, time)
        return
