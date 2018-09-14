# Embedded file name: scripts/client/tutorial/gui/Scaleform/chains/proxy.py
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.gui.Scaleform import effects_player
from tutorial.gui.Scaleform.chains import settings
from tutorial.gui.Scaleform.lobby.proxy import SfLobbyProxy
from tutorial.gui.commands import GUICommandsFactory

class SfChainsProxy(SfLobbyProxy):

    def __init__(self):
        effects = {GUI_EFFECT_NAME.SHOW_HINT: effects_player.ShowChainHint(),
         GUI_EFFECT_NAME.SHOW_WINDOW: effects_player.ShowWindowEffect(settings.WINDOW_ALIAS_MAP),
         GUI_EFFECT_NAME.SET_CRITERIA: effects_player.SetCriteriaEffect(),
         GUI_EFFECT_NAME.SET_TRIGGER: effects_player.SetTriggerEffect()}
        super(SfChainsProxy, self).__init__(effects_player.EffectsPlayer(effects))
        self._commands = GUICommandsFactory()

    def fini(self, isItemsRevert = True):
        self._commands = None
        super(SfChainsProxy, self).fini(isItemsRevert)
        return

    def getViewSettings(self):
        return settings.CHAINS_VIEW_SETTINGS

    def getViewsAliases(self):
        return settings.WINDOW_ALIAS_MAP

    def invokeCommand(self, command):
        self._commands.invoke(None, command)
        return
