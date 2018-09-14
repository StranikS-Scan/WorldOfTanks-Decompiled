# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/unit/actions_handler.py
import weakref
from constants import PREBATTLE_TYPE
from debug_utils import LOG_DEBUG
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.unit.ctx import BattleQueueUnitCtx, AutoSearchUnitCtx
from gui.prb_control.settings import FUNCTIONAL_FLAG

class AbstractActionsHandler(object):
    """
    Abstract class that handles actions from unit. Jobs:
    - displaying in GUI proper page or windows with prebattle
    - updates interfaces with set of actions
    - sends unit into queue
    - handles init and fini actions
    """

    def __init__(self, entity):
        self._entity = weakref.proxy(entity)

    def showGUI(self):
        """
        Routine that should be invoked to show proper UI element related to prebattle:
        window, view or something else.
        """
        pass

    def setPlayerInfoChanged(self):
        """
        Routine that should be invoked when some player's info changes.
        """
        pass

    def setPlayersChanged(self):
        """
        Routine that should be invoked when players's list changes:
        players count, ready state or etc.
        """
        pass

    def setUnitChanged(self, flags=None):
        """
        Routine that should be invoked when unit changes its flags.
        """
        pass

    def executeInit(self, ctx):
        """
        Is used to do all initialization job related to specific prebattle type:
        - show progress in channel carousel
        - update some internal data
        - invoke UI events
        Args:
            ctx: initialization context
        """
        return FUNCTIONAL_FLAG.UNDEFINED

    def executeFini(self):
        """
        Is used to do all finalization job related to specific prebattle type:
        - removes item in channel carousel
        - invoke UI events
        """
        pass

    def executeRestore(self):
        """
        Is invoked when entity is restored due to some reason:
        - center was shut down
        - player was restored on another periphery
        """
        pass

    def execute(self):
        """
        Routine that should be invoked when player do some action:
        - makes himself ready/not ready
        - sends unit in queue
        - etc.
        """
        pass

    def clear(self):
        """
        Clears all internal data.
        """
        self._entity = None
        return

    def exitFromQueue(self):
        """
        Routine must be invoked to exit from queue if it is supported.
        """
        pass

    def _sendBattleQueueRequest(self, vInvID=0, action=1):
        """
        Sends enqueue or dequeue request for unit entity.
        Args:
            vInvID: vehicle inventory id
            action: action type where 1 is start and 0 is stop
        """
        ctx = BattleQueueUnitCtx('prebattle/battle_queue', action=action)
        ctx.selectVehInvID = vInvID
        LOG_DEBUG('Unit request', ctx)
        self._entity.doBattleQueue(ctx)


class UnitActionsHandler(AbstractActionsHandler):
    """
    Unit actions handler class.
    """

    def executeFini(self):
        prbType = self._entity.getEntityType()
        g_eventDispatcher.removeUnitFromCarousel(prbType)
        g_eventDispatcher.loadHangar()

    def execute(self):
        pInfo = self._entity.getPlayerInfo()
        if pInfo.isCommander():
            stats = self._entity.getStats()
            _, unit = self._entity.getUnit()
            if self._canDoAutoSearch(unit, stats):
                if self._entity.isParentControlActivated():
                    return
                if self._entity.getFlags().isDevMode():
                    DialogsInterface.showDialog(rally_dialog_meta.UnitConfirmDialogMeta(PREBATTLE_TYPE.UNIT, 'startBattle'), lambda result: self._sendBattleQueueRequest() if result else None)
                else:
                    ctx = AutoSearchUnitCtx('prebattle/auto_search')
                    LOG_DEBUG('Unit request', ctx)
                    self._entity.doAutoSearch(ctx)
            else:
                self._sendBattleQueueRequest()
        else:
            self._entity.togglePlayerReadyAction()

    def _canDoAutoSearch(self, unit, stats):
        """
        Can current commander do the player's auto search.
        Args:
            unit: unit object
            stats: unit stats object
        """
        return stats.freeSlotsCount > 0
