# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/scenery/TriggerListener.py
import TriggersManager

class TriggerListener(TriggersManager.ITriggerListener):

    def __init__(self, mission):
        super(TriggerListener, self).__init__()
        self._mission = mission
        TriggersManager.g_manager.addListener(self)

    def destroy(self):
        self._mission = None
        TriggersManager.g_manager.delListener(self)
        return

    def onTriggerActivated(self, params):
        self._mission.onTriggerActivated(params)

    def onTriggerDeactivated(self, params):
        self._mission.onTriggerDeactivated(params)
