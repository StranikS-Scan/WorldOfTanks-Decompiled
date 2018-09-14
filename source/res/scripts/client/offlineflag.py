# Embedded file name: scripts/client/OfflineFlag.py
import BigWorld
from OfflineEntity import OfflineEntity
from CTFManager import g_ctfManager
from debug_utils import LOG_ERROR, LOG_WARNING
from Math import Vector3

class OfflineFlag(OfflineEntity):

    def __init__(self):
        super(OfflineFlag, self).__init__()
        self.__parent = None
        return

    def setPosition(self, position):
        if position is not None:
            self.teleport(position, Vector3())
        return

    def prerequisites(self):
        return [g_ctfManager.flagModelName, g_ctfManager.flagCircleModelName]

    def onEnterWorld(self, prereqs):
        if prereqs.failedIDs:
            LOG_ERROR('Failed to load flag model %s' % (prereqs.failedIDs,))
            return
        else:
            self.__parent = g_ctfManager.getFlagInfo(self.flagID)['flag']
            self.model = prereqs[g_ctfManager.flagModelName]
            flagCircleModel = prereqs[g_ctfManager.flagCircleModelName]
            self.model.position = self.position
            self.model.root.attach(flagCircleModel)
            if g_ctfManager.flagAnimAction is not None:
                try:
                    animAction = self.model.action(g_ctfManager.flagAnimAction)
                    animAction()
                except:
                    LOG_WARNING('Unable to start "%s" animation action for model "%s"' % (g_ctfManager.flagAnimAction, g_ctfManager.flagModelName))

            self.model.visible = False
            self.__parent.flagEnterWorld(self)
            return

    def onLeaveWorld(self):
        self.show(False)
        self.__parent.flagLeaveWorld()
        self.__parent = None
        return

    def show(self, isVisible):
        if self.model is not None:
            if isVisible:
                if not self.model.visible:
                    BigWorld.wgAddEdgeDetectEntity(self, 3, 2)
            elif self.model.visible:
                BigWorld.wgDelEdgeDetectEntity(self)
            self.model.visible = isVisible
        return
