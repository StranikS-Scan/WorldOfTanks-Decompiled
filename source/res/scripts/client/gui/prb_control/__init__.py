# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/__init__.py
import typing
if typing.TYPE_CHECKING:
    from typing import Any, Optional
    from gui.prb_control.dispatcher import _PreBattleDispatcher
    from gui.prb_control.entities.base.entity import BasePrbEntity

class prbDispatcherProperty(property):

    def __get__(self, obj, objType=None):
        from gui.prb_control.dispatcher import g_prbLoader
        return g_prbLoader.getDispatcher()


class prbEntityProperty(property):

    def __get__(self, obj, objType=None):
        from gui.prb_control.dispatcher import g_prbLoader
        dispatcher = g_prbLoader.getDispatcher()
        entity = None
        if dispatcher is not None:
            entity = dispatcher.getEntity()
        return entity


class prbPeripheriesHandlerProperty(property):

    def __get__(self, obj, objType=None):
        from gui.prb_control.dispatcher import g_prbLoader
        return g_prbLoader.getPeripheriesHandler()


class prbInvitesProperty(property):

    def __get__(self, obj, objType=None):
        from gui.prb_control.dispatcher import g_prbLoader
        return g_prbLoader.getInvitesManager()


class prbAutoInvitesProperty(property):

    def __get__(self, obj, objType=None):
        from gui.prb_control.dispatcher import g_prbLoader
        return g_prbLoader.getAutoInvitesNotifier()
