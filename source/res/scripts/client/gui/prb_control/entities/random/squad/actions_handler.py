# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/random/squad/actions_handler.py
from CurrentVehicle import g_currentVehicle
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler

class RandomSquadActionsHandler(SquadActionsHandler):
    """
    Random squad actions handler
    """
    pass


class BalancedSquadActionsHandler(RandomSquadActionsHandler):
    """
    Random balanced squad actions handler
    """

    def execute(self):
        if self._entity.isCommander():
            func = self._entity
            fullData = func.getUnitFullData(unitIdx=self._entity.getUnitIdx())
            notReadyCount = 0
            for slot in fullData.slotsIterator:
                slotPlayer = slot.player
                if slotPlayer:
                    if slotPlayer.isInArena() or fullData.playerInfo.isInSearch() or fullData.playerInfo.isInQueue():
                        DialogsInterface.showI18nInfoDialog('squadHavePlayersInBattle', lambda result: None)
                        return True
                    if not slotPlayer.isReady:
                        notReadyCount += 1

            if not fullData.playerInfo.isReady:
                notReadyCount -= 1
            if fullData.stats.occupiedSlotsCount == 1:
                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNoPlayers'), self._confirmCallback)
                return True
            if notReadyCount > 0:
                if notReadyCount == 1:
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayer'), self._confirmCallback)
                    return True
                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayers'), self._confirmCallback)
                return True
            if not g_currentVehicle.isLocked():
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
                                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNoPlayers'), self._confirmCallback)
                                return True

            self._setCreatorReady()
        else:
            self._entity.togglePlayerReadyAction(True)
        return True
