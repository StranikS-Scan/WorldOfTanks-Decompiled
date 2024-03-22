# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/Mine.py
import logging
import typing
import BigWorld
import CGF
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from battleground.mines_object import loadMines
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.managers_registrator import onAddedQuery
from entity_game_object import EntityGameObject
from gui.battle_control import avatar_getter
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import getEquipmentById
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
from PlayerEvents import g_playerEvents
from battle_royale.gui.battle_control.controllers.br_battle_sounds import BREvents
if typing.TYPE_CHECKING:
    from typing import Any, Tuple
_logger = logging.getLogger(__name__)
DETONATION_TIMER_SPEEDUP_TIME = 30

class Mine(EntityGameObject):
    battleSession = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(Mine, self).__init__()
        self.__callbackID = None
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
            self.__callbackID = BigWorld.callback(0, self.__tick)

    def onLeaveWorld(self):
        CGF.getManager(self.spaceID, MineFieldManager).onMineRemoved(self)
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        super(Mine, self).onLeaveWorld()
        return

    def set_isDetonated(self, prev=None):
        if self.isDetonated:
            if self.gameObject is not None:
                self.gameObject.detonate()
        return

    @property
    def fieldID(self):
        return (self.ownerVehicleID, self.deployTime)

    def _loadGameObject(self):
        return loadMines(self.ownerVehicleID, self._registerGameObject)

    def _registerGameObject(self, gameObject):
        self.gameObject.setPosition(self.position)
        self.gameObject.setIsEnemyMarkerEnabled(True)
        super(Mine, self)._registerGameObject(gameObject)

    def __onAvatarReady(self):
        self.__currentObservedVehicleID = avatar_getter.getVehicleIDAttached()

    def __onObservedVehicleChanged(self, observedVehicleID):
        observedVehicleTeam = self.battleSession.getArenaDP().getVehicleInfo(observedVehicleID).team
        observerIsAlly = observedVehicleTeam == self.__ownerTeam
        if observerIsAlly and not self.gameObject.isAllyMine or not observerIsAlly and self.gameObject.isAllyMine:
            self.gameObject.destroy()
            self.gameObject = loadMines(self.ownerVehicleID, self._registerGameObject, startEffectEnabled=False)

    def __tick(self):
        observedVehicleID = avatar_getter.getVehicleIDAttached()
        if observedVehicleID != self.__currentObservedVehicleID:
            self.__currentObservedVehicleID = observedVehicleID
            self.__onObservedVehicleChanged(observedVehicleID)
        self.__callbackID = BigWorld.callback(0.5, self.__tick)


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, CGF.DomainOption.DomainClient)
class MineFieldManager(CGF.ComponentManager):

    def __init__(self, *args):
        super(MineFieldManager, self).__init__(*args)
        self.__activeMinefields = {}

    @onAddedQuery(Mine, CGF.GameObject)
    def onMineAdded(self, mine, _):
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
