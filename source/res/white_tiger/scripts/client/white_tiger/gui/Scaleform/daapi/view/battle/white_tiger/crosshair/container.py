# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/crosshair/container.py
from gui.Scaleform.daapi.view.meta.WTCrosshairPanelContainerMeta import WTCrosshairPanelContainerMeta
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.crosshair import plugins

class WhiteTigerCrosshairPanelContainer(WTCrosshairPanelContainerMeta):

    def __init__(self):
        super(WhiteTigerCrosshairPanelContainer, self).__init__()
        self.addPlugins(plugins.createPlugins())
