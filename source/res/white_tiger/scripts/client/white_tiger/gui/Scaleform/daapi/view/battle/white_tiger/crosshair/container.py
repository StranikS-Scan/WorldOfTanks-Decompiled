# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/crosshair/container.py
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.crosshair import plugins

class WhiteTigerCrosshairPanelContainer(CrosshairPanelContainer):

    def __init__(self):
        super(WhiteTigerCrosshairPanelContainer, self).__init__()
        self.addPlugins(plugins.createPlugins())
