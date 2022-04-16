# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/vehicles_panel.py
import logging
import BigWorld
import BattleReplay
from RTSShared import RTSManner
from gui.Scaleform.daapi.view.meta.VehiclesPanelMeta import VehiclesPanelMeta
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.battle_control.controllers.commander.common import FocusPriority, hasAppendModifiers
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import GameEvent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from soft_exception import SoftException
from gui.battle_control.battle_constants import VehicleConditions
import Keys
_logger = logging.getLogger(__name__)

class VehiclesPanel(VehiclesPanelMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(VehiclesPanel, self).__init__()
        self.__lastSelected = None
        self.__currentlySelected = []
        self.__panelIDOrder = []
        self.__vehProxyMgr = None
        if self.__sessionProvider.dynamic.rtsCommander:
            self.__vehProxyMgr = vehProxyMgr = self.__sessionProvider.dynamic.rtsCommander.vehicles
            vehProxyMgr.onVehicleDisabledStateChanged += self.onVehicleDisabledStateChanged
            vehProxyMgr.onVehicleSelectionChangeAttempt += self.__onVehicleSelectionChangeAttempt
        return

    def __del__(self):
        if self.__sessionProvider.dynamic.rtsCommander and self.__vehProxyMgr is not None:
            vehProxyMgr = self.__vehProxyMgr
            vehProxyMgr.onVehicleDisabledStateChanged -= self.onVehicleDisabledStateChanged
            vehProxyMgr.onVehicleSelectionChangeAttempt -= self.__onVehicleSelectionChangeAttempt
        return

    def onVehicleDisabledStateChanged(self, vehicleID, isDisabled):
        if isDisabled:
            self.__vehProxyMgr.onVehicleConditionUpdated(vehicleID, VehicleConditions.NO_CONDITION)

    def onSelectVehicle(self, vehicleID):
        if not BattleReplay.isPlaying():
            vehicle = self.__vehProxyMgr.get(int(vehicleID))
            if vehicle:
                if self.__lastSelected and self.__panelIDOrder and BigWorld.isKeyDown(Keys.KEY_LSHIFT) and self.__currentlySelected:
                    self.__vehProxyMgr.appendSelection(self.__getShiftSelectedIDs(vehicleID))
                    self.__lastSelected = vehicleID
                elif hasAppendModifiers():
                    if vehicle.isSelected:
                        self.__vehProxyMgr.clearSelection([vehicle.id])
                        for i, csVehicleID in enumerate(self.__currentlySelected):
                            if csVehicleID == vehicleID:
                                self.__currentlySelected.pop(i)
                                break

                        self.__lastSelected = min(self.__currentlySelected) if self.__currentlySelected else None
                    else:
                        self.__lastSelected = vehicleID
                        self.__vehProxyMgr.appendSelection([vehicle.id])
                else:
                    self.__lastSelected = vehicleID
                    self.__vehProxyMgr.setSelection([vehicle.id])
                self.__currentlySelected = self.__vehProxyMgr.keys(lambda v: v.isSelected)
                self.__sessionProvider.dynamic.rtsSound.selectionChanged(self.__currentlySelected, selectionViaPanel=True)
            else:
                _logger.warning('Vehicle is not available as commander vehicle')
        return

    def onSwitchVehicle(self, vehicleID):
        if not BattleReplay.isPlaying():
            self.__sessionProvider.dynamic.rtsCommander.moveToVehicle(int(vehicleID))

    def setVehicleHighlight(self, vehicleID, highlight):
        self.__vehProxyMgr.setFocusVehicle(int(vehicleID), highlight, FocusPriority.PANEL)

    def onUpdateVehicleOrder(self, orderList):
        self.__panelIDOrder = orderList

    def __getShiftSelectedIDs(self, vehicleID):
        s1 = self.__panelIDOrder.index(self.__lastSelected)
        s2 = self.__panelIDOrder.index(vehicleID)
        first = min(s1, s2)
        last = max(s1, s2)
        toSelect = [ self.__panelIDOrder[index] for index in range(first, last + 1) ]
        return toSelect

    def __onVehicleSelectionChangeAttempt(self, vIDs):
        self.__currentlySelected = list(vIDs)
        self.__lastSelected = min(vIDs) if vIDs else None
        return


class VehiclesPanelContextMenuHandler(AbstractContextMenuHandler):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __HALT = 'halt'
    __START_VEHICLE_CONTROL = 'startVehicleControl'
    __MANNERS = {'manner_%s' % mannerID:mannerID for mannerID in RTSManner.ALL if RTSManner.DEFAULT != mannerID}

    def __init__(self, cmProxy, ctx=None):
        g_eventBus.addListener(GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        super(VehiclesPanelContextMenuHandler, self).__init__(cmProxy, ctx=ctx)

    def fini(self):
        g_eventBus.removeListener(GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        super(VehiclesPanelContextMenuHandler, self).fini()

    def onOptionSelect(self, optionId):
        if optionId == self.__HALT:
            self.__sessionProvider.dynamic.rtsCommander.halt([self._vehicleID])
        elif optionId == self.__START_VEHICLE_CONTROL:
            ctrl = self.__sessionProvider.dynamic.vehicleChange
            if ctrl is not None:
                ctrl.changeVehicle(self._vehicleID)
        else:
            manner = self.__MANNERS[optionId]
            if self._isSelectedManner(manner):
                manner = RTSManner.DEFAULT
            self.__sessionProvider.dynamic.rtsCommander.changeManner([self._vehicleID], manner)
        return

    def _initFlashValues(self, ctx):
        if ctx is None:
            raise SoftException('ID of the selected vehicle is incorrect')
        self._vehicleID = int(ctx)
        return

    def _clearFlashValues(self):
        self._vehicleID = None
        return

    def _isSelectedManner(self, mannerID):
        commanderData = BigWorld.player().arena.commanderData.get(self._vehicleID)
        return commanderData and commanderData.orderData and commanderData.orderData.manner == mannerID

    def _generateOptions(self, ctx=None):
        options = [ self._makeItem(mannerKey, optLabel='#rts_battles:commanderHelp/%s' % mannerKey, optInitData={'soundEnabled': False}, iconType=mannerKey if self._isSelectedManner(mannerID) else mannerKey + '_disabled') for mannerKey, mannerID in self.__MANNERS.iteritems() ]
        options.append(self._makeItem(self.__HALT, optLabel='#rts_battles:commanderHelp/halt'))
        options.append(self._makeItem(self.__START_VEHICLE_CONTROL, optLabel='#rts_battles:commanderHelp/startVehicleControl'))
        return options

    def __handleHideCursor(self, _):
        self.onContextMenuHide()
