# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/messengerBar/__init__.py
from __future__ import absolute_import
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.messengerBar.ChannelListContextMenuHandler import ChannelListContextMenuHandler
    return ((CONTEXT_MENU_HANDLER_TYPE.CHANNEL_LIST, ChannelListContextMenuHandler),)


def getViewSettings():
    pass


def getBusinessHandlers():
    pass
