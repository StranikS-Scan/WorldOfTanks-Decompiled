# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/override_scaleform_views_manager.py
import importlib
from constants import ARENA_GUI_TYPE
from soft_exception import SoftException

class _OverrideScaleFormViewsManager(object):
    __slots__ = ('_activeViewAliases', '_activeContextMenuAliases', '_battlePackages', '_lobbyPackages')

    def __init__(self):
        super(_OverrideScaleFormViewsManager, self).__init__()
        self._activeViewAliases = {}
        self._activeContextMenuAliases = {}
        self._lobbyPackages = []
        self._battlePackages = {arenaGUIType:[] for arenaGUIType in ARENA_GUI_TYPE.RANGE}

    @property
    def activeExtensionsViewAliases(self):
        return self._activeViewAliases

    @property
    def activeExtensionsCMAliases(self):
        return self._activeContextMenuAliases

    @property
    def lobbyPackages(self):
        return self._lobbyPackages

    @property
    def battlePackages(self):
        return self._battlePackages

    def initExtensionLobbyPackages(self, extensionName, lobbyPackages):
        self._lobbyPackages.extend(lobbyPackages)
        self.__initHandlers(lobbyPackages, extensionName)

    def initExtensionBattlePackages(self, extensionName, battlePackages, arenaGUIType):
        if arenaGUIType not in self._battlePackages:
            self._battlePackages[arenaGUIType] = battlePackages
        else:
            self._battlePackages[arenaGUIType].extend(battlePackages)
        self.__initHandlers(battlePackages, extensionName, arenaGUIType)

    def __initHandlers(self, paths, extensionName, guiType=None):
        self._activeViewAliases.setdefault(guiType, {})
        self._activeContextMenuAliases.setdefault(guiType, {})
        for path in paths:
            imported = importlib.import_module(path)
            try:
                settings = imported.getViewSettings()
            except AttributeError:
                raise SoftException('Package {0} does not have method getViewSettings'.format(path))

            for setting in settings:
                if setting.alias in self._activeViewAliases[guiType]:
                    raise SoftException('Active extensions:{0}, {1} in wot_ext contains duplicate gui views alias={2}'.format(self._activeViewAliases[guiType][setting.alias], extensionName, setting.alias))
                self._activeViewAliases[guiType][setting.alias] = extensionName

            try:
                handlers = imported.getContextMenuHandlers()
            except AttributeError:
                raise SoftException('Package {0} does not have method getContextMenuHandlers'.format(path))

            for handler in handlers:
                alias, _ = handler[:2]
                if alias in self._activeContextMenuAliases[guiType]:
                    raise SoftException('Active extensions:{0}, {1} in wot_ext contains duplicate context menu alias={2}'.format(self._activeContextMenuAliases[guiType][alias], extensionName, alias))
                self._activeContextMenuAliases[guiType][alias] = extensionName


g_overrideScaleFormViewsConfig = _OverrideScaleFormViewsManager()
