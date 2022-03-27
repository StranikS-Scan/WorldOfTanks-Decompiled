# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/minimap/component.py
import BigWorld
import GUI
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent
from gui.Scaleform.daapi.view.battle.commander.minimap import plugins
from gui.Scaleform.daapi.view.battle.shared.minimap import settings

class CommanderMinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(CommanderMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = plugins.ArenaVehiclesPlugin
        if BigWorld.player().isCommander():
            setup['equipments'] = plugins.EquipmentsPlugin
            setup['personal'] = plugins.PersonalEntriesPlugin
            setup['pinging'] = plugins.CommanderMarkCellPlugin
            setup['points'] = plugins.CommanderTeamsOrControlsPointsPlugin
            setup['area'] = plugins.DisabledMarkerPlugin
            if arenaVisitor.gui.isRTSBootcamp():
                setup['bootcamp'] = plugins.BootcampTargetPlugin
        else:
            setup['points'] = plugins.RtsTeamsOrControlsPointsPlugin
        return setup

    def _createFlashComponent(self):
        return GUI.WGMinimapCommanderFlashAS3(self.app.movie, settings.MINIMAP_COMPONENT_PATH) if BigWorld.player().isCommander() else super(CommanderMinimapComponent, self)._createFlashComponent()

    def addFrustumEntry(self, symbol, container, active):
        entryID = self.getComponent().addFrustumEntry(symbol, container, active)
        if entryID:
            self._MinimapComponent__ids.add(entryID)
        return entryID

    def handleMouseOverUIMinimap(self, isMouseOver):
        self.getPlugin('pinging').handleMouseOverUIMinimap(isMouseOver)
