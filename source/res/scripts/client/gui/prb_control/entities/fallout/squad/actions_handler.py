# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fallout/squad/actions_handler.py
from UnitBase import ROSTER_TYPE
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler

class FalloutSquadActionsHandler(SquadActionsHandler):

    def executeInit(self, ctx):
        g_eventDispatcher.loadFallout()
        return super(FalloutSquadActionsHandler, self).executeInit(ctx)

    def executeFini(self):
        g_eventDispatcher.removeFalloutFromCarousel()
        super(FalloutSquadActionsHandler, self).executeFini()

    def execute(self):
        if self._entity.isCommander():
            entity = self._entity
            fullData = entity.getUnitFullData(unitMgrID=entity.getID())
            isAutoFill = entity.getRosterType() == ROSTER_TYPE.FALLOUT_MULTITEAM_ROSTER
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
            if isAutoFill:
                if notReadyCount == 1:
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayerAuto'), self._confirmCallback)
                    return True
                if fullData.stats.freeSlotsCount == 1:
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNoPlayerAuto'), self._confirmCallback)
                    return True
            else:
                if fullData.stats.occupiedSlotsCount == 1:
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNoPlayers'), self._confirmCallback)
                    return True
                if notReadyCount > 0:
                    if notReadyCount == 1:
                        DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayer'), self._confirmCallback)
                        return True
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayers'), self._confirmCallback)
                    return True
            self._setCreatorReady()
        else:
            self._entity.togglePlayerReadyAction()
        return True

    def _setCreatorReady(self):
        self._sendBattleQueueRequest()
