# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/__init__.py
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.managers.context_menu import ContextMenuManager
__all___ = ('PrbSendInvitesWindow', 'SquadWindow', 'BattleSessionWindow', 'BattleSessionList')
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.PREBATTLE_USER, 'gui.Scaleform.daapi.view.lobby.prb_windows.PrebattleUserCMHandler', 'PrebattleUserCMHandler')
