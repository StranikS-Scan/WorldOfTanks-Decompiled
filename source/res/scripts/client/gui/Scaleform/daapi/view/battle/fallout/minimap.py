# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/fallout/minimap.py
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent
from gui.Scaleform.daapi.view.battle.classic.minimap import GlobalSettingsPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME
_F_STATES = settings.FLAG_ENTRY_STATE
_R_STATES = settings.RESOURCE_ENTRY_STATE

class FalloutMinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(FalloutMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['settings'] = FalloutGlobalSettingsPlugin
        return setup


class FalloutGlobalSettingsPlugin(GlobalSettingsPlugin):
    __slots__ = ('__previousSizeSettings', '__onRespawnVisibilityChanged')

    def __init__(self, parentObj):
        super(FalloutGlobalSettingsPlugin, self).__init__(parentObj)
        self.__previousSizeSettings = None
        return

    def start(self):
        super(FalloutGlobalSettingsPlugin, self).start()
        if GUI_SETTINGS.minimapSize:
            ctrl = self.sessionProvider.dynamic.respawn
            if ctrl is not None:
                ctrl.onRespawnVisibilityChanged += self.__onRespawnVisibilityChanged
        return

    def stop(self):
        if GUI_SETTINGS.minimapSize:
            ctrl = self.sessionProvider.dynamic.respawn
            if ctrl is not None:
                ctrl.onRespawnVisibilityChanged -= self.__onRespawnVisibilityChanged
        super(FalloutGlobalSettingsPlugin, self).stop()
        return

    def __onRespawnVisibilityChanged(self, isVisible):
        if isVisible:
            self.__previousSizeSettings = self._changeSizeSettings('minimapRespawnSize')
        else:
            self._changeSizeSettings(self.__previousSizeSettings)
            self.__previousSizeSettings = None
        return
