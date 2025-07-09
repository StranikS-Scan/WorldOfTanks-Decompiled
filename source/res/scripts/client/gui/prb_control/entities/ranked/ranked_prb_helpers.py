# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/ranked/ranked_prb_helpers.py
import adisp
from gui.prb_control.entities.base.ctx import RankedPrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME

@adisp.adisp_process
def createRankedSquad(squadSize):
    from gui.prb_control.dispatcher import g_prbLoader
    prbDispatcher = g_prbLoader.getDispatcher()
    if prbDispatcher is not None:
        yield prbDispatcher.doSelectAction(RankedPrbAction(PREBATTLE_ACTION_NAME.RANKED_SQUAD, squadSize=squadSize))
    return
