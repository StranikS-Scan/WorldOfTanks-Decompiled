# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/battle_royale/__init__.py
from CurrentVehicle import g_currentPreviewVehicle
from gui.prb_control.settings import FUNCTIONAL_FLAG

def isNeedToLoadHangar(ctx):
    if g_currentPreviewVehicle.isPresent():
        reqFlags = FUNCTIONAL_FLAG.LOAD_PAGE | FUNCTIONAL_FLAG.SWITCH | FUNCTIONAL_FLAG.TRAINING
        if ctx and not ctx.hasFlags(reqFlags):
            return True
    return False
