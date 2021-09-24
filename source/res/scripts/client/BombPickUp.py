# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BombPickUp.py
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from Event import Event

class BombPickUpComponent(object):

    def __init__(self):
        super(BombPickUpComponent, self).__init__()
        self.update = Event()
        self.leftTime = 0
        self.endTime = BigWorld.serverTime()
        self.totalTime = 0
        self.refCount = 1

    def destroy(self):
        self.update.clear()
        self.update = None
        return


class BombPickUp(DynamicScriptComponent):

    def __init__(self):
        super(BombPickUp, self).__init__()
        self.changeRefCnt(True)

    def onDestroy(self):
        super(BombPickUp, self).onDestroy()
        self.changeRefCnt(False)

    def changeRefCnt(self, sign):
        go = self.entity.entityGameObject
        pickUp = go.findComponentByType(BombPickUpComponent)
        if not bool(pickUp):
            go.createComponent(BombPickUpComponent)
            self.set_endTime()
            return
        pickUp.refCount += 1 if sign else -1
        if pickUp.refCount == 0:
            self.update(0.0)
            go.removeComponentByType(BombPickUpComponent)
            return

    def set_endTime(self, *_):
        self.update(self.endTime)

    def update(self, endTime):
        go = self.entity.entityGameObject
        pickUp = go.findComponentByType(BombPickUpComponent)
        if pickUp:
            pickUp.leftTime = endTime - BigWorld.serverTime() if endTime > 0.0 else 0.0
            pickUp.endTime = endTime
            pickUp.totalTime = self.totalTime
            pickUp.update(self.entity, pickUp, go)
        return bool(pickUp)
