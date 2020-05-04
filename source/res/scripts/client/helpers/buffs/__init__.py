# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/buffs/__init__.py
import logging
from typing import List
import BigWorld
from buffs_common import Buff, BuffComponent, BuffsRepository
from vehicle_systems.entity_components import VehicleComponent
_logger = logging.getLogger(__name__)

class ClientBuffsRepository(BuffsRepository):

    @property
    def _buffFactory(self):
        from helpers.buffs.factories import ClientBuffFactory
        return ClientBuffFactory


class ClientBuff(Buff):
    pass


class ClientBuffComponent(BuffComponent):

    class VisibilityModes(object):
        NONE = 0
        SELF = 1
        OTHERS = 2
        ALL = 3

    def apply(self, ctx=None):
        if self._isVisible():
            self._apply()

    def unapply(self):
        if self._isVisible():
            self._unapply()

    def _apply(self):
        pass

    def _unapply(self):
        pass

    def _isVehicleObservedByAvatar(self):
        avatar = BigWorld.player()
        return False if not avatar else avatar.getVehicleAttached() == self._owner

    def _shouldShowForSelf(self):
        return self._owner.isPlayerVehicle or self._isVehicleObservedByAvatar()

    def _isVisible(self):
        if self._config.visibleTo == self.VisibilityModes.ALL:
            return True
        if self._config.visibleTo == self.VisibilityModes.SELF and self._shouldShowForSelf():
            return True
        return True if self._config.visibleTo == self.VisibilityModes.OTHERS and not self._shouldShowForSelf() else False


class BuffContainer(VehicleComponent):

    def __init__(self):
        self._buffs = {}

    def set_buffs(self, prevBuffs=None):
        buffsRepo = ClientBuffsRepository.getInstance()
        prevBuffs = set(prevBuffs) if prevBuffs else set()
        currentBuffs = set(self.buffs)
        toAddBuffIndices = currentBuffs - prevBuffs
        toRemoveBuffIndices = prevBuffs - currentBuffs
        for index in toAddBuffIndices:
            buffFactory = buffsRepo.getBuffFactoryByIndex(index)
            if buffFactory:
                buff = buffFactory.createBuff(self)
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
