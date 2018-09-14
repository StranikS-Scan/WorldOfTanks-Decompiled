# Python bytecode 2.7 (decompiled from Python 2.7)
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
        self.__circleModel = None
        self.__parent = g_ctfManager.getFlagInfo(self.flagID)['flag']
        self.__flagType = self.__parent.flagType
        return

    def setPosition(self, position):
        self.__servo = None
        if position is not None:
            self.teleport(position, Vector3())
            if self.__circleModel is not None:
                self.__circleModel.position = position
        return

    def prerequisites(self):
        return [g_ctfManager.flagModelName(self.__flagType), g_ctfManager.flagCircleModelName]

    def onEnterWorld(self, prereqs):
        if prereqs.failedIDs:
            LOG_ERROR('Failed to load flag model %s' % (prereqs.failedIDs,))
            return
        else:
            modelName = g_ctfManager.flagModelName(self.__flagType)
            self.model = prereqs[modelName]
            if g_ctfManager.flagCircleModelName != '':
                self.__circleModel = prereqs[g_ctfManager.flagCircleModelName]
                self.__circleModel.position = self.position
            self.model.position = self.position
            animAction = g_ctfManager.flagAnimAction(self.__flagType)
            if animAction is not None:
                try:
                    animAction()
                except:
                    LOG_WARNING('Unable to start "%s" animation action for model "%s"' % (animAction, modelName))

            self.model.visible = False
            self.__parent.flagEnterWorld(self)
            self.model.addMotor(BigWorld.Servo(self.matrix))
            return

    def onLeaveWorld(self):
        if self.__parent is not None:
            self.show(False)
            self.__parent.flagLeaveWorld()
            self.__parent = None
        self.__circleModel = None
        return

    def show(self, isVisible):
        if self.model is not None:
            if isVisible:
                if not self.model.visible:
                    BigWorld.wgAddEdgeDetectEntity(self, 3, 2, False)
                    if self.__circleModel is not None:
                        BigWorld.addModel(self.__circleModel)
            elif self.model.visible:
                BigWorld.wgDelEdgeDetectEntity(self)
                if self.__circleModel is not None:
                    BigWorld.delModel(self.__circleModel)
            self.model.visible = isVisible
        return
