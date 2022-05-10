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

    def initExtensionGUIPackages(self, extensionName, lobbyPackages, battlePackages, arenaGUITypes):
        lobbyPackages = self.__convertToList(lobbyPackages)
        self._lobbyPackages.extend(lobbyPackages)
        battlePackages = self.__convertToList(battlePackages)
        arenaGUITypes = self.__convertToList(arenaGUITypes)
        for arenaGUIType in arenaGUITypes:
            if arenaGUIType not in self._battlePackages:
                self._battlePackages[arenaGUIType] = battlePackages
            self._battlePackages[arenaGUIType].extend(battlePackages)

        self.__initHandlers(lobbyPackages, extensionName)
        self.__initHandlers(battlePackages, extensionName, arenaGUITypes)

    def __initHandlers(self, paths, extensionName, guiTypes=None):
        guiTypes = guiTypes or (None,)
        for guiType in guiTypes:
            self._activeViewAliases.setdefault(guiType, {})
            self._activeContextMenuAliases.setdefault(guiType, {})

        for path in paths:
            imported = importlib.import_module(path)
            try:
                settings = imported.getViewSettings()
            except AttributeError:
                raise SoftException('Package {0} does not have method getViewSettings'.format(path))

            for setting in settings:
                for guiType in guiTypes:
                    if setting.alias in self._activeViewAliases[guiType]:
                        raise SoftException('Active extensions:{0}, {1} in wot_ext contains duplicate gui views alias={2}'.format(self._activeViewAliases[guiType][settings.alias], extensionName, settings.alias))
                    self._activeViewAliases[guiType][setting.alias] = extensionName

            try:
                handlers = imported.getContextMenuHandlers()
            except AttributeError:
                raise SoftException('Package {0} does not have method getContextMenuHandlers'.format(path))

            for handler in handlers:
                alias, _ = handler[:2]
                for guiType in guiTypes:
                    if alias in self._activeContextMenuAliases[guiType]:
                        raise SoftException('Active extensions:{0}, {1} in wot_ext contains duplicate context menu alias={2}'.format(self._activeContextMenuAliases[guiType][alias], extensionName, alias))
                    self._activeContextMenuAliases[guiType][alias] = extensionName

        return None

    def __convertToList(self, items):
        return [items] if not hasattr(items, '__iter__') else items


g_overrideScaleFormViewsConfig = _OverrideScaleFormViewsManager()
