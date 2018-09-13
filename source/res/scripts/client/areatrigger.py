# Embedded file name: scripts/client/AreaTrigger.py
import BigWorld
import TriggersManager

class AreaTrigger(BigWorld.UserDataObject):

    def __init__(self):
        BigWorld.UserDataObject.__init__(self)
        self.__id = TriggersManager.g_manager.addTrigger(TriggersManager.TRIGGER_TYPE.AREA, name=self.name, position=self.position, radius=self.radius, exitInterval=self.exitInterval)

    def destroy(self):
        TriggersManager.g_manager.delTrigger(self.__id)
