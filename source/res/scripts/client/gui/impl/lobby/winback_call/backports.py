# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback_call/backports.py
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.impl.backport import createContextMenuData

def getWinBackCallFrindContextMenuData(event):
    friendDbID = long(event.getArgument('databaseID', default=0))
    userName = str(event.getArgument('userName', default=''))
    if friendDbID:
        contextMenuArgs = {'dbID': friendDbID,
         'userName': userName}
        return createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.WIN_BACK_CALL_FRIEND_CONTEXT_MENU, contextMenuArgs)
    else:
        return None
