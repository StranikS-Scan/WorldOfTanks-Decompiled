# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/GameInfoPanel.py
# Compiled at: 2010-04-27 19:00:41
import BigWorld
import time
from gui import DebugPanel
from gui import DEPTH_OF_GameInfoPanel
import constants
from debug_utils import *

class GameInfoPanel(object):

    def __init__(self):
        self.__panel = None
        self.__lastLagDuration = 0
        self.__worstLagDuration = 0
        self.__nextTimeOfResetWorstLag = 0
        return

    def prerequisites(self):
        return []

    def start(self):
        self.__panel = self.__createDebugPanelRelease()
        self.setVisible(False)

    def destroy(self):
        self.__panel.destroy()
        self.__panel = None
        return

    def setVisible(self, bValue):
        if self.__panel is not None:
            self.__panel.setVisible(bValue)
        return

    def __createDebugPanelDevelopment(self):
        resPanel = DebugPanel.DebugPanel()
        resPanel.setPosition((0.47, 0.98, DEPTH_OF_GameInfoPanel))
        resPanel.setAlign((True,
         True,
         True,
         True))
        resPanel.setMargin((0.04, 0.04, 0.04, 0.04))
        resPanel.setVisible(True)
        item = DebugPanel.DebugPanelItem('FPS:')
        item.setDivider('')
        item.setFont(('system_small.font', 'system_small.font'))
        item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
        resPanel.addItem('fps', item)
        updater = DebugPanel.DebugPanelItemUpdater(lambda : BigWorld.getFPS(), 0.0)
        item = DebugPanel.DebugPanelItem('current', updater, lambda x: '%0.3d' % x[0])
        item.setFont(('system_small.font', 'system_small.font'))
        item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
        resPanel.addItem('fps_current', item)
        item = DebugPanel.DebugPanelItem('average', updater, lambda x: '%0.3d' % x[1])
        item.setFont(('system_small.font', 'system_small.font'))
        item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
        resPanel.addItem('fps_average', item)
        item = DebugPanel.DebugPanelItem('min', updater, lambda x: '%0.3d' % x[2])
        item.setFont(('system_small.font', 'system_small.font'))
        item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
        resPanel.addItem('fps_min', item)
        item = DebugPanel.DebugPanelItem('max', updater, lambda x: '%0.3d' % x[3])
        item.setFont(('system_small.font', 'system_small.font'))
        item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
        resPanel.addItem('fps_max', item)
        item = DebugPanel.DebugPanelItem(' ')
        item.setDivider('')
        resPanel.addItem('empty line 01', item)
        item = DebugPanel.DebugPanelItem('Ping:')
        item.setDivider('')
        item.setFont(('system_small.font', 'system_small.font'))
        item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
        resPanel.addItem('net', item)
        updater = DebugPanel.DebugPanelItemUpdater(lambda : self.__updater_net(), 0.0)
        item = DebugPanel.DebugPanelItem('latency', updater, lambda x: '%0.3d' % x[0])
        item.setFont(('system_small.font', 'system_small.font'))
        item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
        resPanel.addItem('net_latency', item)
        item = DebugPanel.DebugPanelItem('lagging', updater, lambda x: '%s' % x[1])
        item.setFont(('system_small.font', 'system_small.font'))
        item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
        resPanel.addItem('net_lagging', item)
        item = DebugPanel.DebugPanelItem('last lag', updater, lambda x: '%0.3d' % x[2])
        item.setFont(('system_small.font', 'system_small.font'))
        item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
        resPanel.addItem('net_lastlag', item)
        item = DebugPanel.DebugPanelItem('worst lag', updater, lambda x: '%0.3d' % x[3])
        item.setFont(('system_small.font', 'system_small.font'))
        item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
        resPanel.addItem('net_worstlag', item)
        item = DebugPanel.DebugPanelItem(' ')
        item.setDivider('')
        resPanel.addItem('empty line 02', item)
        item = DebugPanel.DebugPanelItem('Tank:')
        item.setDivider('')
        item.setFont(('system_small.font', 'system_small.font'))
        item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
        resPanel.addItem('tank', item)
        updater = DebugPanel.DebugPanelItemUpdater(lambda : self.__updater_tank(), 0.0)
        item = DebugPanel.DebugPanelItem('v, km/h', updater, lambda x: '%3.0f' % (x[0][0] * 3.6))
        item.setFont(('system_small.font', 'system_small.font'))
        item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
        resPanel.addItem('tank_linear_velocity', item)
        item = DebugPanel.DebugPanelItem('r, gr/s', updater, lambda x: '%3.0f' % (x[0][1] * 57.3))
        item.setFont(('system_small.font', 'system_small.font'))
        item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
        resPanel.addItem('tank_angular_velocity', item)
        resPanel.update()
        return resPanel

    def __createDebugPanelRelease(self):
        resPanel = DebugPanel.DebugPanel()
        resPanel.setPosition((-0.99, 0.99, DEPTH_OF_GameInfoPanel))
        resPanel.setAlign((True,
         True,
         True,
         True))
        resPanel.setMargin((0.04, 0.04, 0.04, 0.04))
        resPanel.setVisible(True)
        updater = DebugPanel.DebugPanelItemUpdater(lambda : '%3.0d' % BigWorld.getFPS()[1], 0.0)
        item = DebugPanel.DebugPanelItem('FPS:', updater)
        item.setDivider('  ')
        item.setFont(('system_small.font', 'system_small.font'))
        item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
        resPanel.addItem('fps_average', item)
        updater = DebugPanel.DebugPanelItemUpdater(lambda : '%3.0f' % self.__updater_normalized_ping(), 0.0)
        item = DebugPanel.DebugPanelItem('Ping:', updater)
        item.setDivider('  ')
        item.setFont(('system_small.font', 'system_small.font'))
        item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
        resPanel.addItem('normalized_ping', item)
        resPanel.update()
        return resPanel

    def __updater_net(self):
        ping = BigWorld.LatencyInfo().value[3] * 1000
        isLaggingNow = False
        timeFromLagStart = 0
        if BigWorld.player() is None:
            return
        else:
            vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
            if vehicle is not None and isinstance(vehicle.filter, BigWorld.WGVehicleFilter):
                isLaggingNow = vehicle.filter.isLaggingNow
                timeFromLagStart = vehicle.filter.timeFromLagStart * 1000
                timeNow = time.time()
            else:
                isLaggingNow = False
                timeFromLagStart = 0
                timeNow = time.time()
            if isLaggingNow:
                self.__lastLagDuration = timeFromLagStart
            if timeNow > self.__nextTimeOfResetWorstLag:
                self.__worstLagDuration = 0
                self.__nextTimeOfResetWorstLag = timeNow + 20
            elif timeFromLagStart > self.__worstLagDuration:
                self.__worstLagDuration = timeFromLagStart
            return (min(ping, 999),
             'YES' if isLaggingNow else 'no',
             min(self.__lastLagDuration, 999),
             min(self.__worstLagDuration, 999))

    def __updater_tank(self):
        vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        if vehicle is None:
            return ((0.0, 0.0),)
        else:
            return (vehicle.filter.speedInfo.value,)

    def __updater_normalized_ping(self):
        upd = self.__updater_net()
        if upd is None:
            return 0
        else:
            latency = upd[0]
            if latency == 999:
                return 999
            return max(1, latency - 500.0 * constants.SERVER_TICK_LENGTH)
