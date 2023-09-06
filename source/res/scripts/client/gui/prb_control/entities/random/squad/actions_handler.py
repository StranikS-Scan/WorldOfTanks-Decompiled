# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/random/squad/actions_handler.py
from BWUtil import AsyncReturn
from CurrentVehicle import g_currentVehicle
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from gui.impl.gen import R
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler
from gui.shared.event_dispatcher import showPlatoonWarningDialog
from wg_async import wg_async, wg_await

class RandomSquadActionsHandler(SquadActionsHandler):
    pass


class BalancedSquadActionsHandler(RandomSquadActionsHandler):

    @wg_async
    def _validateUnitState(self, entity):
        result = yield wg_await(super(BalancedSquadActionsHandler, self)._validateUnitState(entity))
        if not result:
            raise AsyncReturn(result)
        if entity.isCommander():
            fullData = entity.getUnitFullData(unitMgrID=entity.getID())
            if not g_currentVehicle.isLocked() and not fullData.playerInfo.isReady:
                _, unit = self._entity.getUnit()
                playerVehicles = unit.getVehicles()
                if playerVehicles:
                    commanderLevel = g_currentVehicle.item.level
                    lowerBound, upperBound = self._entity.getSquadLevelBounds()
                    minLevel = max(MIN_VEHICLE_LEVEL, commanderLevel + lowerBound)
                    maxLevel = min(MAX_VEHICLE_LEVEL, commanderLevel + upperBound)
                    levelRange = range(minLevel, maxLevel + 1)
                    for _, unitVehicles in playerVehicles.iteritems():
                        for vehicle in unitVehicles:
                            if vehicle.vehLevel not in levelRange:
                                result = yield wg_await(showPlatoonWarningDialog(R.strings.dialogs.squadHaveNoPlayers))
                                if not result:
                                    raise AsyncReturn(result)

        raise AsyncReturn(True)

    @staticmethod
    def _isSquadHavePlayersInBattle(slotPlayer, playerInfo):
        return slotPlayer.isInArena() or playerInfo.isInQueue()
