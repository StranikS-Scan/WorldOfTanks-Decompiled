# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWArenaInfoVehicleBuffsBroadcaster.py
import BigWorld
from PlayerEvents import g_playerEvents
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from halloween.gui.shared import events as hw_events
from buffs import ClientBuffsRepository

class HWArenaInfoVehicleBuffsBroadcaster(BigWorld.DynamicScriptComponent):
    ICON_COMPONENT_NAME = 'icon'
    buffsRepo = ClientBuffsRepository.getInstance()

    def __init__(self):
        g_playerEvents.onAvatarReady += self._onAvatarReady

    def set_buffs(self, prevBuffs):
        self._sendNotifications(self.buffs, prevBuffs)

    def setSlice_buffs(self, path, oldValue):
        self._sendNotifications(_getNewValue(self.buffs, path), oldValue)

    def _onAvatarReady(self):
        g_playerEvents.onAvatarReady -= self._onAvatarReady
        self._sendNotifications(self.buffs, [])

    def _sendNotifications(self, addedItems, removedItems):
        for item in addedItems:
            icon, tooltip = self._getBuffIconNameAndTooltip(item['buff'])
            if icon is None:
                continue
            g_eventBus.handleEvent(hw_events.BuffGUIEvent(hw_events.BuffGUIEvent.ON_GLOBAL_APPLY, ctx={'id': icon,
             'iconName': icon,
             'tooltip': tooltip,
             'vehicleID': item['vehicleID']}), scope=EVENT_BUS_SCOPE.BATTLE)

        for item in removedItems:
            icon, tooltip = self._getBuffIconNameAndTooltip(item['buff'])
            if icon is None:
                continue
            g_eventBus.handleEvent(hw_events.BuffGUIEvent(hw_events.BuffGUIEvent.ON_GLOBAL_UNAPPLY, ctx={'id': icon,
             'vehicleID': item['vehicleID']}), scope=EVENT_BUS_SCOPE.BATTLE)

        return

    def _getBuffIconNameAndTooltip(self, buffName):
        buffFactory = self.buffsRepo.getBuffFactoryByName(buffName)
        if buffFactory is None:
            tooltip = {'params': {},
             'tag': buffName}
            return (buffName, tooltip)
        else:
            componentsFactories = buffFactory.getComponentFactoriesByName(self.ICON_COMPONENT_NAME)
            if not componentsFactories:
                return (None, None)
            cfg = componentsFactories[0].config
            return (cfg.iconName, cfg.tooltip)


def _getNewValue(sequence, path):
    startIndex, endIndex = path[-1]
    return sequence[startIndex:endIndex]
