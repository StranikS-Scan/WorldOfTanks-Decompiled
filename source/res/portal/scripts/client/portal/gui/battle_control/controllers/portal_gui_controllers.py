# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/battle_control/controllers/portal_gui_controllers.py
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

@dependency.replace_none_kwargs(sessionProvider=IBattleSessionProvider)
def getPortalBattleMarkersController(portalCtrlID, sessionProvider=None):
    if sessionProvider is not None:
        repository = sessionProvider.dynamic._repository
        if hasattr(repository, '_ctrls'):
            return repository._ctrls.get(portalCtrlID)
        return
    else:
        return
