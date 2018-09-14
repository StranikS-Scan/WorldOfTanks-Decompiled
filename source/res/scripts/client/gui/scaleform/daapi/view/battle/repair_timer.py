# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/repair_timer.py
import weakref
from debug_utils import LOG_DEBUG
from gui.battle_control import g_sessionProvider
from gui.shared.utils.plugins import IPlugin
_CALLBACK_NAME = 'battle.onLoadRepairTimer'

class _RepairTimer(object):

    def __init__(self, battleUI):
        self.__flashObject = weakref.proxy(battleUI.movie.repairTimer.instance)

    def destroy(self):
        self.__flashObject = None
        return

    def showTimer(self, time, state, title, description):
        self.__flashObject.as_show(time, state, title, description)

    def hideTimer(self):
        self.__flashObject.as_hide()


class RepairTimerPlugin(IPlugin):

    def __init__(self, parentObj):
        super(RepairTimerPlugin, self).__init__(parentObj)
        self.__repairTimer = None
        return

    def init(self):
        super(RepairTimerPlugin, self).init()
        self._parentObj.addExternalCallback(_CALLBACK_NAME, self.__onLoad)

    def fini(self):
        self._parentObj.removeExternalCallback(_CALLBACK_NAME)
        super(RepairTimerPlugin, self).fini()

    def start(self):
        super(RepairTimerPlugin, self).start()
        self._parentObj.movie.falloutItems.as_loadRepairTimer()

    def stop(self):
        g_sessionProvider.getRepairCtrl().stop()
        if self.__repairTimer is not None:
            self.__repairTimer.destroy()
            self.__repairTimer = None
        super(RepairTimerPlugin, self).stop()
        return

    def __onLoad(self, _):
        self.__repairTimer = _RepairTimer(self._parentObj)
        g_sessionProvider.getRepairCtrl().start(self.__repairTimer)
