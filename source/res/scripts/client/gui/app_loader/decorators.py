# Embedded file name: scripts/client/gui/app_loader/decorators.py
from gui.app_loader.loader import g_appLoader
from gui.app_loader.settings import APP_NAME_SPACE as _SPACE

class app_getter(property):

    def __init__(self, fget = None, doc = None, space = None):
        super(app_getter, self).__init__(fget=fget, doc=doc)
        self._space = space

    def __get__(self, obj, objType = None):
        return g_appLoader.getApp(self._space)


class def_lobby(property):

    def __get__(self, obj, objType = None):
        return g_appLoader.getDefLobbyApp()


class def_battle(property):

    def __get__(self, obj, objType = None):
        return g_appLoader.getDefBattleApp()


class sf_lobby(app_getter):

    def __init__(self, fget = None, doc = None):
        super(sf_lobby, self).__init__(fget, doc, _SPACE.SF_LOBBY)


class sf_battle(app_getter):

    def __init__(self, fget = None, doc = None):
        super(sf_battle, self).__init__(fget, doc, _SPACE.SF_BATTLE)
