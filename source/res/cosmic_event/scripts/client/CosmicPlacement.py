# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/CosmicPlacement.py
from typing import Optional
import BigWorld
import CGF
import Math
import cosmic_prefabs
from debug_utils import LOG_DEBUG_DEV, LOG_ERROR
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class LootHandler(object):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    __CMP_NAME = 'airDropComponent'

    def onCreated(self, placement):
        acmp = self._getCmp()
        if acmp:
            acmp.scheduleLoot(placement.id, placement.position, placement.dropTime)

    def _getCmp(self):
        cmpSystem = self.__guiSessionProvider.arenaVisitor.getComponentSystem()
        if cmpSystem:
            return getattr(cmpSystem, self.__CMP_NAME, None)
        else:
            LOG_ERROR("Couldn't find {}!".format(self.__CMP_NAME))
            return None


class CosmicPlacement(BigWorld.Entity):
    PLACEMENT_PREFAB_PATH = cosmic_prefabs.Loot.UNKNOWN

    def __init__(self):
        self.__handler = None
        return

    def onEnterWorld(self, *args):
        self.__handler = LootHandler()
        LOG_DEBUG_DEV('[Placement] type={} onEnterWorld'.format(self.typeID), BigWorld.time())
        self.__handler.onCreated(self)
        CGF.loadGameObjectIntoHierarchy(self.PLACEMENT_PREFAB_PATH, self.entityGameObject, Math.Vector3(0, 0, 0))

    def onLeaveWorld(self):
        LOG_DEBUG_DEV('[Placement] type={} onLeaveWorld'.format(self.typeID), BigWorld.time())
        self.__handler = None
        return
