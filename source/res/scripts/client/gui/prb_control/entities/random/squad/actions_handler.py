# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/random/squad/actions_handler.py
from CurrentVehicle import g_currentVehicle
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.impl.gen import R
from gui.prb_control.entities.base import checkVehicleAmmoFull
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler
from gui.shared.event_dispatcher import showPlatoonResourceDialog

class RandomSquadActionsHandler(SquadActionsHandler):
    pass


class BalancedSquadActionsHandler(RandomSquadActionsHandler):

    def execute(self):
        func = self._entity
        fullData = func.getUnitFullData(unitMgrID=func.getID())
        if self._entity.isCommander():
            notReadyCount = 0
            for slot in fullData.slotsIterator:
                slotPlayer = slot.player
                if slotPlayer:
                    if slotPlayer.isInArena() or fullData.playerInfo.isInQueue():
                        DialogsInterface.showI18nInfoDialog('squadHavePlayersInBattle', lambda result: None)
                        return
                    if not slotPlayer.isReady:
                        notReadyCount += 1

            if not fullData.playerInfo.isReady:
                notReadyCount -= 1
            if fullData.stats.occupiedSlotsCount == 1:
                showPlatoonResourceDialog(R.strings.dialogs.squadHaveNoPlayers, self._confirmCallback)
                return
            if notReadyCount > 0:
                showPlatoonResourceDialog(R.strings.dialogs.squadHaveNotReadyPlayer, self._confirmCallback)
                return
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
                                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNoPlayers'), self._confirmCallback)
                                return

            self._setCreatorReady()
        elif not fullData.playerInfo.isReady:
            checkVehicleAmmoFull(g_currentVehicle.item, self._checkVehicleAmmoCallback)
        else:
            self._entity.togglePlayerReadyAction(True)
