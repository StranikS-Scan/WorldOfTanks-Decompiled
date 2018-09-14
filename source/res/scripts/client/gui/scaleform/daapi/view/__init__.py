# Embedded file name: scripts/client/gui/Scaleform/daapi/view/__init__.py
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.managers.context_menu import ContextMenuManager
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.APPEAL_USER, 'gui.Scaleform.daapi.view.lobby.user_cm_handlers', 'AppealCMHandler')
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.BASE_USER, 'gui.Scaleform.daapi.view.lobby.user_cm_handlers', 'BaseUserCMHandler')
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.BASE_CLAN, 'gui.Scaleform.daapi.view.lobby.clans.clan_cm_handlers', 'BaseClanCMHandler')
