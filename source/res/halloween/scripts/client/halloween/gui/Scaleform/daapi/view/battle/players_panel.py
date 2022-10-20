# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/players_panel.py
from gui.Scaleform.daapi.view.meta.HWPlayersPanelMeta import HWPlayersPanelMeta
from gui.shared import EVENT_BUS_SCOPE
from halloween.gui.shared import events as hw_events
from gui.battle_control import avatar_getter

class HWPlayersPanel(HWPlayersPanelMeta):

    def __init__(self):
        super(HWPlayersPanel, self).__init__()
        self._buffs = {}

    def switchToOtherPlayer(self, vehicleID):
        pass

    def _populate(self):
        super(HWPlayersPanel, self)._populate()
        self.addListener(hw_events.BuffGUIEvent.ON_GLOBAL_APPLY, self.__handleBuffApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(hw_events.BuffGUIEvent.ON_GLOBAL_UNAPPLY, self.__handleBuffUnApply, scope=EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        super(HWPlayersPanel, self)._dispose()
        self.removeListener(hw_events.BuffGUIEvent.ON_GLOBAL_APPLY, self.__handleBuffApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(hw_events.BuffGUIEvent.ON_GLOBAL_UNAPPLY, self.__handleBuffUnApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self._buffs.clear()

    def __handleBuffUnApply(self, event):
        vehicleID = event.ctx['vehicleID']
        buff = (event.ctx['id'], vehicleID)
        vehicleBuffs = self._buffs.setdefault(vehicleID, [])
        if buff in vehicleBuffs:
            vehicleBuffs.remove(buff)
            self.__updateVehicleBuffIcon(vehicleBuffs[-1] if vehicleBuffs else ('', vehicleID))

    def __handleBuffApply(self, event):
        vehicleID = event.ctx['vehicleID']
        vehicleBuffs = self._buffs.setdefault(vehicleID, [])
        buff = (event.ctx['id'], vehicleID)
        if buff not in vehicleBuffs:
            vehicleBuffs.append(buff)
            self.__updateVehicleBuffIcon(buff)

    def __updateVehicleBuffIcon(self, buff):
        iconName, vehicleID = buff[0], buff[1]
        self.as_setPlayerBuffS(self.__isAlly(vehicleID), vehicleID, iconName)

    def __isAlly(self, vehicleID):
        arenaDP = self.sessionProvider.getArenaDP()
        vInfo = arenaDP.getVehicleInfo(vehicleID)
        return avatar_getter.getPlayerTeam() == vInfo.team if arenaDP.isPlayerObserver() else arenaDP.isAllyTeam(vInfo.team)
