# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/crosshair/container.py
from gui.Scaleform.daapi.view.external_components import ExternalFlashSettings
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.shared.crosshair import settings
from white_tiger.gui.Scaleform.daapi.view.battle.crosshair import plugins
from white_tiger.gui.Scaleform.daapi.view.meta.WhiteTigerCrosshairPanelContainerMeta import WhiteTigerCrosshairPanelContainerMeta

class WhiteTigerCrosshairPanelContainer(WhiteTigerCrosshairPanelContainerMeta):
    EXTERNAL_FLASH_SETTINGS = ExternalFlashSettings(BATTLE_VIEW_ALIASES.CROSSHAIR_PANEL, 'white_tiger|whiteTigerBattleCrosshairsApp.swf', settings.CROSSHAIR_ROOT_PATH, settings.CROSSHAIR_INIT_CALLBACK)

    def __init__(self):
        super(WhiteTigerCrosshairPanelContainer, self).__init__()
        self._addPlugins(plugins.createPlugins())
