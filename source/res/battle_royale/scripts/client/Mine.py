# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/Mine.py
from __future__ import absolute_import
import logging
import typing
import BigWorld
import CGF
from battleground.mines_object import loadMines
from entity_world_object import EntityWorldObject
from gui.battle_control import avatar_getter
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import getEquipmentById
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
from PlayerEvents import g_playerEvents
from battle_royale.gui.battle_control.controllers.br_battle_sounds import BREvents
if typing.TYPE_CHECKING:
    from typing import Tuple
_logger = logging.getLogger(__name__)
DETONATION_TIMER_SPEEDUP_TIME = 30

class Mine(EntityWorldObject):
    battleSession = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(Mine, self).__init__()
        self.__ownerTeam = self.battleSession.getArenaDP().getVehicleInfo(self.ownerVehicleID).team
        player = BigWorld.player()
        if player is not None and player.userSeesWorld():
            self.__currentObservedVehicleID = avatar_getter.getVehicleIDAttached()
        else:
            self.__currentObservedVehicleID = None
            g_playerEvents.onAvatarReady += self.__onAvatarReady
        return

    def onEnterWorld(self, *args):
        super(Mine, self).onEnterWorld(*args)
        if BigWorld.player().isObserver():
            self.__callbackID = BigWorld.callback(0, self.tick)

    def onLeaveWorld(self):
        CGF.getSystem(self.spaceID, MineFieldSystem).onMineRemoved(self)
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        super(Mine, self).onLeaveWorld()

    def set_isDetonated(self, prev=None):
        if self.isDetonated:
            if self.worldObject is not None:
                self.worldObject.detonate()
        return

    def tick(self):
        observedVehicleID = avatar_getter.getVehicleIDAttached()
        if observedVehicleID != self.__currentObservedVehicleID:
            self.__currentObservedVehicleID = observedVehicleID
            self.__onObservedVehicleChanged(observedVehicleID)

    @property
    def fieldID(self):
        return (self.ownerVehicleID, self.deployTime)

    def _loadWorldObject(self):
        return loadMines(self.ownerVehicleID, self._registerWorldObject)

    def _registerWorldObject(self, worldObject):
        worldObject.setPosition(self.position)
        worldObject.setIsEnemyMarkerEnabled(True)
        super(Mine, self)._registerWorldObject(worldObject)

    def __onAvatarReady(self):
        self.__currentObservedVehicleID = avatar_getter.getVehicleIDAttached()

    def __onObservedVehicleChanged(self, observedVehicleID):
        observedVehicleTeam = self.battleSession.getArenaDP().getVehicleInfo(observedVehicleID).team
        observerIsAlly = observedVehicleTeam == self.__ownerTeam
        mines = self.worldObject
        if observerIsAlly and not mines.isAllyMine or not observerIsAlly and mines.isAllyMine:
            mines.destroy()
            self.worldObject = loadMines(self.ownerVehicleID, self._registerWorldObject, startEffectEnabled=False)


class MineFieldSystem(CGF.System):
    MineActivated = CGF.ActivateReaction(CGF.ReactRo(Mine))
    MineIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Rw(Mine))
    Reactions = CGF.Reactions(MineActivated, MineIterate)

    def commonUpdate(self):
        for mine in self.reaction(self.MineActivated):
            self.onMineAdded(mine)

    def periodUpdate(self):
        player = BigWorld.player()
        if player is None or not player.isObserver():
            return
        else:
            for mine in self.reaction(self.MineIterate):
                mine.tick()

            return

    def __init__(self, *args):
        super(MineFieldSystem, self).__init__(*args)
        self.__activeMinefields = {}

    def onMineAdded(self, mine):
        if mine.fieldID not in self.__activeMinefields:
            equipment = getEquipmentById(mine.equipmentID)
            detonationTime = mine.deployTime + equipment.mineParams.lifetime
            self.__activeMinefields[mine.fieldID] = MineField(mine.fieldID, detonationTime, mine.position)
        else:
            self.__activeMinefields[mine.fieldID].addMine()

    def onMineRemoved(self, mine):
        mineField = self.__activeMinefields.get(mine.fieldID)
        if not mineField:
            return
        mineField.removeMine()
        if not mineField.hasMines:
            mineField.destroy()
            del self.__activeMinefields[mine.fieldID]

    def destroy(self):
        self.__activeMinefields = None
        return


class MineField(CallbackDelayer):

    def __init__(self, id_, detonationTime, position):
        super(MineField, self).__init__()
        _logger.debug('Created MineField with id %s', id_)
        self.__id = id_
        self.__detonationTime = detonationTime
        self.__position = position
        self.__minesCount = 1
        self.__soundObj = BREvents.getSoundObject(self.__soundObjectName, position)
        self.__startTimerSound()

    def addMine(self):
        self.__minesCount += 1

    def removeMine(self):
        self.__minesCount = max(self.__minesCount - 1, 0)

    @property
    def hasMines(self):
        return bool(self.__minesCount)

    def destroy(self):
        super(MineField, self).destroy()
        self.__soundObj.play(BREvents.MINEFIELD_TIMER_STOP)
        self.__soundObj.stopAll()
        self.__soundObj = None
        _logger.debug('Destroyed MineField with id %s', self.__id)
        return

    def __startTimerSound(self):
        self.__soundObj.play(BREvents.MINEFIELD_TIMER)
        timeTillDetonation = self.__timeTillDetonation
        timeout = 0
        if timeTillDetonation > DETONATION_TIMER_SPEEDUP_TIME:
            timeout = timeTillDetonation - DETONATION_TIMER_SPEEDUP_TIME
        self.delayCallback(timeout, self.__setRTPC)

    def __setRTPC(self):
        self.__soundObj.setRTPC(BREvents.MINEFIELD_TIMER_RTPC, self.__timeTillDetonation)
        if self.__timeTillDetonation > 0:
            self.delayCallback(0.5, self.__setRTPC)

    @property
    def __soundObjectName(self):
        return 'MineField_{}_{}'.format(self.__id[0], self.__id[1])

    @property
    def __timeTillDetonation(self):
        return self.__detonationTime - BigWorld.serverTime()
