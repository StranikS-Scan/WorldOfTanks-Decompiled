# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/crosshair.py
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import AimDamagePlugin

class EpicAimDamagePlugin(AimDamagePlugin):

    def start(self):
        super(EpicAimDamagePlugin, self).start()
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        destructibleComponent = getattr(componentSystem, 'destructibleEntityComponent', None)
        if destructibleComponent is not None:
            destructibleComponent.onDestructibleEntityFeedbackReceived += self.__onDestructibleEntityFeedbackReceived
        return

    def stop(self):
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        destructibleComponent = getattr(componentSystem, 'destructibleEntityComponent', None)
        if destructibleComponent is not None:
            destructibleComponent.onDestructibleEntityFeedbackReceived -= self.__onDestructibleEntityFeedbackReceived
        return

    def __onDestructibleEntityFeedbackReceived(self, eventID, _, value):
        if eventID in self._DAMAGE_EVENTS:
            self._invalidateAimDamage(value)


class EpicCrosshairPanelContainer(CrosshairPanelContainer):

    def _getPlugins(self):
        plugins = super(EpicCrosshairPanelContainer, self)._getPlugins()
        plugins['aimDamage'] = EpicAimDamagePlugin
        return plugins
