# Embedded file name: scripts/client/gui/battle_control/RepairController.py
import weakref
import BigWorld
import Event
import SoundGroups
from constants import REPAIR_POINT_ACTION, REPAIR_POINT_STATE
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI

class RepairController(object):
    __REPAIR_SOUND_NAME = '/GUI/fallout/point_repair'

    class __REPAIR_STATE(object):
        PROGRESS = 'progress'
        COOLDOWN = 'cooldown'

    def __init__(self):
        super(RepairController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onRepairPointStateChanged = Event.Event(self.__eManager)
        self.__ui = None
        return

    def start(self, ui):
        self.__ui = weakref.proxy(ui)

    def stop(self):
        self.__ui = None
        self.__eManager.clear()
        self.__eManager = None
        return

    def action(self, repairPointIndex, action, nextActionTime):
        if self.__ui is None:
            return
        else:
            timeLeft = max(0, nextActionTime - BigWorld.serverTime())
            if action in (REPAIR_POINT_ACTION.START_REPAIR, REPAIR_POINT_ACTION.RESTART_REPAIR):
                self.__ui.call('repairTimer.show', [timeLeft,
                 self.__REPAIR_STATE.PROGRESS,
                 INGAME_GUI.REPAIRPOINT_TITLE,
                 None])
            elif action == REPAIR_POINT_ACTION.COMPLETE_REPAIR:
                self.__ui.call('repairTimer.show', [timeLeft,
                 self.__REPAIR_STATE.COOLDOWN,
                 INGAME_GUI.REPAIRPOINT_TITLE,
                 INGAME_GUI.REPAIRPOINT_UNAVAILABLE])
                SoundGroups.g_instance.FMODplaySound(self.__REPAIR_SOUND_NAME)
            elif action == REPAIR_POINT_ACTION.ENTER_WHILE_CD:
                self.__ui.call('repairTimer.show', [timeLeft, self.__REPAIR_STATE.COOLDOWN, ''])
            elif action in (REPAIR_POINT_ACTION.LEAVE_WHILE_CD, REPAIR_POINT_ACTION.CANCEL_REPAIR):
                self.__ui.call('repairTimer.hide')
            self.onRepairPointStateChanged(repairPointIndex, action, timeLeft)
            return
