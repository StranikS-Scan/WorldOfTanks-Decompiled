# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWVehicleBuffContainer.py
import BigWorld
from buffs import ClientBuffsRepository
ClientBuffsRepository.init()

class HWVehicleBuffContainer(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(HWVehicleBuffContainer, self).__init__()
        self._buffs = {}
        BigWorld.player().onVehicleEnterWorld += self.__onVehicleEnterWorld
        BigWorld.player().onVehicleLeaveWorld += self.__onVehicleLeaveWorld
        BigWorld.player().arena.onVehicleHealthChanged += self.__onDamageReceived
        self.set_buffs()

    def onDestroy(self):
        self.clearBuffs()
        BigWorld.player().onVehicleEnterWorld -= self.__onVehicleEnterWorld
        BigWorld.player().onVehicleLeaveWorld -= self.__onVehicleLeaveWorld
        BigWorld.player().arena.onVehicleHealthChanged -= self.__onDamageReceived

    def onEnterWorld(self, *args):
        pass

    def onLeaveWorld(self, *args):
        self.onDestroy()

    def set_buffs(self, prevBuffs=None):
        if not self.entity.isStarted:
            return
        else:
            buffsRepo = ClientBuffsRepository.getInstance()
            prevBuffs = set(prevBuffs) if prevBuffs else set()
            currentBuffs = set(self.buffs)
            toAddBuffIndices = currentBuffs - prevBuffs
            toRemoveBuffIndices = prevBuffs - currentBuffs
            for index in toAddBuffIndices:
                buffFactory = buffsRepo.getBuffFactoryByIndex(index)
                if buffFactory:
                    buff = buffFactory.createBuff(self.entity)
                    buff.apply()
                    self._buffs[index] = buff

            for index in toRemoveBuffIndices:
                buff = self._buffs.pop(index, None)
                if buff:
                    buff.unapply()

            return

    def clearBuffs(self):
        for buff in self._buffs.itervalues():
            buff.unapply()

        self._buffs.clear()

    def isBuffActive(self, buffName):
        buffIdx = ClientBuffsRepository.getInstance().getBuffIndexByBuffName(buffName)
        return buffIdx in self.buffs

    def __onVehicleEnterWorld(self, v):
        if self.entity.id != v.id:
            return
        self.set_buffs()

    def __onVehicleLeaveWorld(self, v):
        if self.entity.id != v.id:
            return
        self.clearBuffs()

    def __onDamageReceived(self, vehicleId, _, __):
        if self.entity.id != vehicleId:
            return
        if self.entity.health <= 0:
            self.clearBuffs()
